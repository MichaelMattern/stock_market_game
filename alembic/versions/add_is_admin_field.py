"""Add is_admin field to Account

Revision ID: add_is_admin_field
Revises: 20250208_create_pen_ord
Create Date: 2023-08-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_admin_field'
down_revision = '20250208_create_pen_ord'  # Updated to link with previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Add is_admin column with default value of False to accounts table
    op.add_column('accounts', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='False'))
    
    # Create first admin user if none exists
    op.execute("""
    INSERT INTO accounts (user_id, password, cash, open_positions, profit_loss, is_admin)
    SELECT 1000, 'admin', 10000.0, '{}', 0.0, True
    WHERE NOT EXISTS (SELECT 1 FROM accounts WHERE is_admin = True LIMIT 1)
    """)


def downgrade():
    # Remove is_admin column
    op.drop_column('accounts', 'is_admin') 