"""Add products table

Revision ID: 2c030d164446
Revises: 9b3ddbeea45f
Create Date: 2025-11-02 12:40:11.466354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c030d164446'
down_revision: Union[str, Sequence[str], None] = '9b3ddbeea45f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    products = op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(), nullable=False),
    sa.Column('amount', sa.String(), nullable=False),
    sa.Column('percentage', sa.Float(), nullable=False),
    sa.Column('flow_type', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.bulk_insert(
        products,
        [
            {'product_name': 'MicroLoan', 'amount': '30000',
             'percentage': 15.0, 'flow_type': 'pioneer'},
            {'product_name': 'QuickMoney', 'amount': '60000',
             'percentage': 10.0, 'flow_type': 'pioneer'},
            {'product_name': 'ConsumerLoan', 'amount': '120000',
             'percentage': 10.0, 'flow_type': 'pioneer'},
            {'product_name': 'LoyaltyLoan', 'amount': '500000',
             'percentage': 1.8, 'flow_type': 'repeater'},
            {'product_name': 'AdvantagePlus', 'amount': '1200000',
             'percentage': 1.6, 'flow_type': 'repeater'},
            {'product_name': 'PrimeCredit', 'amount': '5000000',
             'percentage': 1.4, 'flow_type': 'repeater'},
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('products')
