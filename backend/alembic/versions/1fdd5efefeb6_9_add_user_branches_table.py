"""add user_branches table

Revision ID: 1fdd5efefeb6
Revises: 348ec5471b93
Create Date: 2025-11-12 16:14:59.251669

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1fdd5efefeb6"
down_revision = "348ec5471b93"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_branches",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "branch_id"),
    )


def downgrade() -> None:
    op.drop_table("user_branches")
