"""add stock history table

Revision ID: add_stock_history_table
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_stock_history_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'stock_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('volatility', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.Integer(), nullable=False),
        sa.Column('timeframe', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_history_symbol'), 'stock_history', ['symbol'], unique=False)
    op.create_index(op.f('ix_stock_history_timestamp'), 'stock_history', ['timestamp'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_stock_history_timestamp'), table_name='stock_history')
    op.drop_index(op.f('ix_stock_history_symbol'), table_name='stock_history')
    op.drop_table('stock_history') 