"""Create the products table.

Revision ID: 20261028_0001
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "20261028_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint("price > 0", name="ck_products_price_positive"),
        sa.CheckConstraint("quantity > 0", name="ck_products_quantity_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_id", "products", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")
