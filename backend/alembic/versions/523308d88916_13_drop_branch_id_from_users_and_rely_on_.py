"""drop branch_id from users and rely on user_branches

Revision ID: 523308d88916
Revises: 55cf1b7f3f9e
Create Date: 2025-11-13 20:31:14.946507

"""

from alembic import op
import sqlalchemy as sa


revision = "523308d88916"
down_revision = "55cf1b7f3f9e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop branch_id column from users
    try:
        with op.batch_alter_table("users") as batch_op:
            batch_op.drop_column("branch_id")
    except Exception:
        pass
    # Rename name to full_name in users
    try:
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column("name", new_column_name="full_name")
    except Exception:
        pass
    # Drop parent_name from students
    try:
        with op.batch_alter_table("students") as batch_op:
            batch_op.drop_column("parent_name")
    except Exception:
        pass


def downgrade() -> None:
    # Revert full_name for name in users
    try:
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column("full_name", new_column_name="name")
    except Exception:
        pass  # column not present

    # Add parent_name back to students
    try:
        with op.batch_alter_table("students") as batch_op:
            batch_op.add_column(
                sa.Column("parent_name", sa.String(length=120), nullable=False)
            )
    except Exception:
        pass
