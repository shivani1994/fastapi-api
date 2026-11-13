from decimal import Decimal

import pytest
from fastapi import HTTPException, Response, status
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from main import app
import db_models
from models import Product, ProductResponse
from routers.products import (
    create_product,
    delete_product,
    get_product,
    replace_product,
    router,
)

client = TestClient(app)


def product_payload(**overrides):
    payload = {
        "name": "Desk lamp",
        "description": "Adjustable office lamp",
        "price": 24.5,
        "quantity": 10,
    }
    return {**payload, **overrides}


def test_http_crud_contract_and_persistence(clean_database):
    created = client.post("/products/", json=product_payload())
    assert created.status_code == status.HTTP_201_CREATED
    product = created.json()
    product_id = product["id"]

    assert client.get(f"/products/{product_id}").json() == product
    assert client.get("/products/").json() == [product]

    replacement = product_payload(name="Floor lamp", quantity=4)
    updated = client.put(f"/products/{product_id}", json=replacement)
    assert updated.status_code == status.HTTP_200_OK
    assert updated.json()["name"] == "Floor lamp"
    assert client.get(f"/products/{product_id}").json()["quantity"] == 4

    deleted = client.delete(f"/products/{product_id}")
    assert deleted.status_code == status.HTTP_204_NO_CONTENT
    assert deleted.content == b""
    assert client.get(f"/products/{product_id}").status_code == status.HTTP_404_NOT_FOUND


def test_http_missing_product_responses_are_404(clean_database):
    assert client.get("/products/999").status_code == status.HTTP_404_NOT_FOUND
    assert client.put(
        "/products/999", json=product_payload()
    ).status_code == status.HTTP_404_NOT_FOUND
    assert client.delete("/products/999").status_code == status.HTTP_404_NOT_FOUND


def test_http_rejects_invalid_product_body(clean_database):
    invalid_payload = product_payload(price=0)
    assert client.post("/products/", json=invalid_payload).status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_products_returns_empty_list(clean_database):
    assert client.get("/products/").json() == []


def test_list_products_applies_pagination(db_session):
    db_session.add_all(
        [
            db_models.Product(
                id=30,
                name="Lamp C",
                description=None,
                price=Decimal("3.00"),
                quantity=1,
            ),
            db_models.Product(
                id=10,
                name="Lamp A",
                description=None,
                price=Decimal("1.00"),
                quantity=1,
            ),
            db_models.Product(
                id=20,
                name="Lamp B",
                description=None,
                price=Decimal("2.00"),
                quantity=1,
            ),
        ]
    )
    db_session.commit()
    db_session.close()

    page = client.get("/products/?skip=1&limit=1")
    assert [product["id"] for product in page.json()] == [20]
    assert client.get("/products/?limit=101").status_code == 422


@pytest.mark.parametrize(
    "price, quantity",
    [(Decimal("0.00"), 1), (Decimal("1.00"), 0)],
)
def test_database_rejects_nonpositive_price_or_quantity(
    db_session, price, quantity
):
    db_session.add(
        db_models.Product(
            name="Lamp", description=None, price=price, quantity=quantity
        )
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_create_product_persists_and_returns_product(db_session):
    product = create_product(Product(**product_payload()), db_session)
    response_model = ProductResponse.model_validate(product)

    assert product.id is not None
    assert product.name == "Desk lamp"
    assert db_session.get(db_models.Product, product.id) is not None
    expected = product_payload()
    expected["price"] = Decimal("24.50")
    assert response_model.model_dump() == {"id": product.id, **expected}


def test_get_product_returns_existing_product(db_session):
    created = create_product(Product(**product_payload()), db_session)

    result = get_product(created.id, db_session)

    assert result.id == created.id
    assert result.name == created.name


def test_get_missing_product_raises_404(db_session):
    with pytest.raises(HTTPException) as error:
        get_product(999, db_session)

    assert error.value.status_code == status.HTTP_404_NOT_FOUND
    assert error.value.detail == "Product not found"


def test_product_input_rejects_invalid_fields():
    invalid_payloads = (
        product_payload(name="x"),
        product_payload(price=0),
        product_payload(quantity=0),
    )

    for payload in invalid_payloads:
        with pytest.raises(ValidationError):
            Product(**payload)


def test_put_replaces_product_and_returns_updated_product(db_session):
    created = create_product(Product(**product_payload()), db_session)
    replacement = product_payload(name="Floor lamp", quantity=4)

    updated = replace_product(Product(**replacement), created.id, db_session)

    assert updated.id == created.id
    assert updated.name == "Floor lamp"
    assert updated.quantity == 4


def test_put_missing_product_raises_404(db_session):
    with pytest.raises(HTTPException) as error:
        replace_product(Product(**product_payload()), 999, db_session)

    assert error.value.status_code == status.HTTP_404_NOT_FOUND
    assert error.value.detail == "Product not found"


def test_delete_returns_no_content_and_removes_product(db_session):
    created = create_product(Product(**product_payload()), db_session)

    response = delete_product(created.id, db_session)

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.body == b""
    assert db_session.get(db_models.Product, created.id) is None


def test_delete_missing_product_raises_404(db_session):
    with pytest.raises(HTTPException) as error:
        delete_product(999, db_session)

    assert error.value.status_code == status.HTTP_404_NOT_FOUND
    assert error.value.detail == "Product not found"


def test_route_contract_declares_created_and_no_content_statuses():
    endpoints = {route.endpoint.__name__: route for route in router.routes}

    assert endpoints["create_product"].status_code == status.HTTP_201_CREATED
    assert endpoints["delete_product"].status_code == status.HTTP_204_NO_CONTENT
    assert endpoints["get_products"].response_model == list[ProductResponse]
    assert endpoints["get_product"].response_model is ProductResponse
    assert endpoints["replace_product"].response_model is ProductResponse


def test_product_ids_are_constrained_to_positive_values():
    endpoints = {route.endpoint.__name__: route for route in router.routes}

    for endpoint_name in ("get_product", "replace_product", "delete_product"):
        path_parameter = next(
            parameter
            for parameter in endpoints[endpoint_name].dependant.path_params
            if parameter.name == "product_id"
        )
        assert any(
            getattr(constraint, "gt", None) == 0
            for constraint in path_parameter.field_info.metadata
        )


def test_openapi_documents_crud_success_and_not_found_responses():
    paths = app.openapi()["paths"]

    assert "201" in paths["/products/"]["post"]["responses"]
    create_response = paths["/products/"]["post"]["responses"]["201"]
    response_schema = create_response["content"]["application/json"]["schema"]
    assert response_schema["$ref"].endswith("/ProductResponse")

    for method in ("get", "put", "delete"):
        responses = paths["/products/{product_id}"][method]["responses"]
        assert "404" in responses

    assert "204" in paths["/products/{product_id}"]["delete"]["responses"]
    assert "content" not in paths["/products/{product_id}"]["delete"]["responses"]["204"]
