# File: stock_market_game/alembic/versions/20250206_create_tables.py
"""create tables

Revision ID: 20250206_create_tables
Revises: 
Create Date: 2025-02-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250206_create_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'stocks',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('symbol', sa.String, unique=True, index=True),
        sa.Column('price', sa.Float),
        sa.Column('volume', sa.Integer),
        sa.Column('volatility', sa.Float),
    )
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, unique=True, index=True),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('cash', sa.Float, server_default="10000.0", nullable=False),
        sa.Column('open_positions', sa.JSON, server_default='{}', nullable=False),
        sa.Column('profit_loss', sa.Float, server_default="0.0", nullable=False),
    )

def downgrade():
    op.drop_table('accounts')
    op.drop_table('stocks')
