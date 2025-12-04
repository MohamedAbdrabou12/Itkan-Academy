"""create parents and parent_students tables

Revision ID: bc373c7674d2
Revises: 685e54821682
Create Date: 2025-12-04 12:11:18.233687

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bc373c7674d2"
down_revision = "685e54821682"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Create parents table ---
    op.create_table(
        "parents",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("occupation", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # --- Create parent_students table ---
    op.create_table(
        "parent_students",
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("parents.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "student_id",
            sa.Integer(),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade() -> None:
    # Drop parent_students first due to FK dependency
    op.drop_table("parent_students")
    # Drop parents table
    op.drop_table("parents")
