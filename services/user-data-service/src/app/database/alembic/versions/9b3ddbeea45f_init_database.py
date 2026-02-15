"""Init database

Revision ID: 9b3ddbeea45f
Revises: 
Create Date: 2025-10-29 21:59:55.583672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b3ddbeea45f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('monthly_income', sa.Integer(), nullable=False),
    sa.Column('employment_type', sa.String(), nullable=False),
    sa.Column('has_property', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('phone')
    )
    op.create_table('loans',
    sa.Column('loan_id', sa.String(), nullable=False),
    sa.Column('product_name', sa.String(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('issue_date', sa.Date(), nullable=False),
    sa.Column('term_days', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('close_date', sa.Date(), nullable=True),
    sa.Column('user_phone', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_phone'], ['users.phone'], ),
    sa.PrimaryKeyConstraint('loan_id')
    )


def downgrade() -> None:
    op.drop_table('loans')
    op.drop_table('users')
