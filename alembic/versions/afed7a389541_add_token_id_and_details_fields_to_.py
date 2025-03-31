"""Add token_id and details fields to CFDIHistory model

Revision ID: afed7a389541
Revises: 945f8533c50d
Create Date: 2025-03-31 16:52:15.952680

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'afed7a389541'
down_revision = '945f8533c50d'
branch_labels = None
depends_on = None


def upgrade():
    # Add token_id column
    op.add_column('cfdi_history', sa.Column('token_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_cfdi_history_token_id'), 'cfdi_history', ['token_id'], unique=False)
    
    # Add details column - using JSON type that works in both SQLite and PostgreSQL
    op.add_column('cfdi_history', sa.Column('details', sa.JSON(), nullable=True))


def downgrade():
    # Drop details column
    op.drop_column('cfdi_history', 'details')
    
    # Drop token_id column and its index
    op.drop_index(op.f('ix_cfdi_history_token_id'), table_name='cfdi_history')
    op.drop_column('cfdi_history', 'token_id')
