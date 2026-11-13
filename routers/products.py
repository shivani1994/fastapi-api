from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from models import Product, ProductResponse
from database import DBSession
import db_models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/products",
    tags = ["Products"]
)

"""created method to get db connection"""
def getdb():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[ProductResponse])
def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(getdb),
):
    db_products = (
        db.query(db_models.Product)
        .order_by(db_models.Product.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return db_products


def get_product_or_404(product_id: int, db: Session) -> db_models.Product:
    db_product = db.query(db_models.Product).filter(db_models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return db_product


@router.get(
    "/{product_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Product not found"}},
)
def get_product(
    product_id: int = Path(gt=0),
    db: Session = Depends(getdb),
):
    product = get_product_or_404(product_id, db)
    return {
        "status": status.HTTP_200_OK,
        "data": product
    }

@router.post(
    "/",
    #response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: Product, db: Session = Depends(getdb)):
    db_product = db_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {
        "status": status.HTTP_201_CREATED,
        "data": db_product
    }


@router.put(
    "/{product_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Product not found"}},
)
def replace_product(
    product: Product,
    product_id: int = Path(gt=0),
    db: Session = Depends(getdb),
):
    db_product = get_product_or_404(product_id, db)
    for field, value in product.model_dump().items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return {
        "status": status.HTTP_200_OK,
        "data": db_product
    }


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Product not found"}},
)
def delete_product(
    product_id: int = Path(gt=0),
    db: Session = Depends(getdb),
):
    db_product = get_product_or_404(product_id, db)
    db.delete(db_product)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
