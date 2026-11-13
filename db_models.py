from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import CheckConstraint, Column, Integer, Numeric, String

Base = declarative_base()

class Product(Base):

    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_products_price_positive"),
        CheckConstraint("quantity > 0", name="ck_products_quantity_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

