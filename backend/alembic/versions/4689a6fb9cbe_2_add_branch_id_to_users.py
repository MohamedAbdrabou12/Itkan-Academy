"""Add branch_id to users

Revision ID: 4689a6fb9cbe
Revises: c132530085fe
Create Date: 2025-11-05 17:29:07.517887

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4689a6fb9cbe"
down_revision = "c132530085fe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add branch_id column to users table
    op.add_column("users", sa.Column("branch_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_users_branch_id",
        "users",
        "branches",
        ["branch_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Drop the foreign key and column
    op.drop_constraint("fk_users_branch_id", "users", type_="foreignkey")
    op.drop_column("users", "branch_id")
