"""create pending_orders table

Revision ID: 20250208_create_pen_ord
Revises: 20250207_pos_trades  # or whatever your previous revision is
Create Date: 2025-02-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250208_create_pen_ord'
down_revision = '20250207_pos_trades'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'pending_orders',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('order_id', sa.String, unique=True, index=True, nullable=False),
        sa.Column('user_id', sa.Integer, index=True, nullable=False),
        sa.Column('symbol', sa.String, index=True, nullable=False),
        sa.Column('side', sa.String, nullable=False),  # "buy" or "sell"
        sa.Column('quantity', sa.Float, nullable=False),
        sa.Column('order_type', sa.String, nullable=False),  # "market" or "limit"
        sa.Column('limit_price', sa.Float, nullable=True),
        sa.Column('timestamp', sa.Integer, nullable=False),
    )

def downgrade():
    op.drop_table('pending_orders')
