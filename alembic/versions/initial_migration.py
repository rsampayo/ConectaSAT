"""Initial migration.

Revision ID: 1a1a1a1a1a1a Revises: Create Date: 2023-05-01 00:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.sql import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "1a1a1a1a1a1a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create superadmins table
    op.create_table(
        "superadmins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_superadmins_id"), "superadmins", ["id"], unique=False)
    op.create_index(
        op.f("ix_superadmins_username"), "superadmins", ["username"], unique=True
    )

    # Create api_tokens table
    op.create_table(
        "api_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_tokens_id"), "api_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_api_tokens_token"), "api_tokens", ["token"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_api_tokens_token"), table_name="api_tokens")
    op.drop_index(op.f("ix_api_tokens_id"), table_name="api_tokens")
    op.drop_table("api_tokens")

    op.drop_index(op.f("ix_superadmins_username"), table_name="superadmins")
    op.drop_index(op.f("ix_superadmins_id"), table_name="superadmins")
    op.drop_table("superadmins")
