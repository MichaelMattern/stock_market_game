# File: stock_market_game/alembic/versions/20250207_pos_trades.py
"""create positions and trades tables

Revision ID: 20250207_pos_trades
Revises: 20250206_create_tables
Create Date: 2025-02-07 21:02:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250207_pos_trades'
down_revision = '20250206_create_tables'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'positions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, index=True, nullable=False),
        sa.Column('symbol', sa.String, index=True, nullable=False),
        sa.Column('quantity', sa.Float, nullable=False, server_default="0"),
    )
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('order_id', sa.String, unique=True, index=True, nullable=False),
        sa.Column('user_id', sa.Integer, index=True, nullable=False),
        sa.Column('symbol', sa.String, index=True, nullable=False),
        sa.Column('side', sa.String, nullable=False),  # "buy" or "sell"
        sa.Column('quantity', sa.Float, nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('timestamp', sa.Integer, nullable=False),
    )

def downgrade():
    op.drop_table('trades')
    op.drop_table('positions')
