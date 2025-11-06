"""add failed_message and user relationship to notifications

Revision ID: 4457cb957767
Revises: a252f6e29415
Create Date: 2025-11-06 11:02:03.390379

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4457cb957767"
down_revision = "a252f6e29415"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_notifications_user_id",
        "notifications",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_notifications_user_id", "notifications", type_="foreignkey")
