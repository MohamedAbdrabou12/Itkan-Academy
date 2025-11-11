"""create teachers and teacher_classes

Revision ID: c0fdde6b7933
Revises: f94ca4c38486
Create Date: 2025-11-11 03:41:29.200830

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c0fdde6b7933"
down_revision = "f94ca4c38486"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --------- create teachers table ---------
    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("qualification", sa.String(length=255), nullable=True),
        sa.Column("specialization", sa.String(length=255), nullable=True),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column(
            "employment_type",
            sa.Enum("full_time", "part_time", "contract", name="employmenttype"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # create teacher_classes table
    op.create_table(
        "teacher_classes",
        sa.Column(
            "teacher_id",
            sa.Integer(),
            sa.ForeignKey("teachers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "class_id",
            sa.Integer(),
            sa.ForeignKey("classes.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "assigned_date",
            sa.Date(),
            server_default=sa.func.current_date(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("teacher_classes")
    op.drop_table("teachers")
    # drop enum type
    sa.Enum(name="employmenttype").drop(op.get_bind(), checkfirst=True)
