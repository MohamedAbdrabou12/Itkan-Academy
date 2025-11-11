"""create student_classes table

Revision ID: 348ec5471b93
Revises: c0fdde6b7933
Create Date: 2025-11-11 18:11:55.825439

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "348ec5471b93"
down_revision = "c0fdde6b7933"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_classes",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("enrollment_date", sa.Date(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("progress_percent", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("final_grade", sa.String(length=10), nullable=True),
        sa.Column("last_attendance", sa.Date(), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "class_id"),
    )

    op.drop_constraint(op.f("students_class_id_fkey"), "students", type_="foreignkey")
    op.drop_column("students", "class_id")


def downgrade() -> None:
    op.add_column(
        "students",
        sa.Column("class_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        op.f("students_class_id_fkey"),
        "students",
        "classes",
        ["class_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_table("student_classes")
