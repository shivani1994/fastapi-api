from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class Product(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(gt=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    name: str
    description: str | None
    price: Decimal
    quantity: int

