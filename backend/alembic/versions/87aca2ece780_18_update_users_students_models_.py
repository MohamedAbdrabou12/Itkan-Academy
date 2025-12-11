"""IA-243 update users & students models (login fields + national id + nullable fixes)

Revision ID: 87aca2ece780
Revises: bc373c7674d2
Create Date: 2025-12-11 02:46:58.259125

"""

from alembic import op
import sqlalchemy as sa

revision = "87aca2ece780"
down_revision = "bc373c7674d2"
branch_labels = None
depends_on = None


def upgrade():
    # USERS TABLE (SAFE MIGRATION)
    with op.batch_alter_table("users", schema=None) as batch_op:
        # email -> nullable
        batch_op.alter_column(
            "email",
            existing_type=sa.String(length=120),
            nullable=True,
            existing_nullable=False,
        )

        # Add login_identifier (TEMP nullable=True)
        batch_op.add_column(
            sa.Column("login_identifier", sa.String(length=100), nullable=True)
        )

        # Add login_type (TEMP nullable=True)
        batch_op.add_column(
            sa.Column("login_type", sa.String(length=20), nullable=True)
        )

    # Fill login_identifier + login_type for existing users (temporary values)
    op.execute("""
        UPDATE users
        SET login_identifier = COALESCE(email, 'user_' || id::text),
            login_type = 'email';
    """)

    # Now enforce NOT NULL + UNIQUE
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "login_identifier",
            existing_type=sa.String(length=100),
            nullable=False,
            existing_nullable=True,
        )
        batch_op.alter_column(
            "login_type",
            existing_type=sa.String(length=20),
            nullable=False,
            existing_nullable=True,
        )
        batch_op.create_unique_constraint(
            "uq_users_login_identifier", ["login_identifier"]
        )

    # STUDENTS TABLE
    with op.batch_alter_table("students", schema=None) as batch_op:
        # Add national_id (nullable=True temporarily)
        batch_op.add_column(sa.Column("national_id", sa.String(20), nullable=True))

    # Fill national_id (temp value for existing rows)
    op.execute("""
        UPDATE students
        SET national_id = 'temp_' || id::text
        WHERE national_id IS NULL;
    """)

    # Enforce NOT NULL + unique constraint
    with op.batch_alter_table("students", schema=None) as batch_op:
        batch_op.alter_column(
            "national_id",
            existing_type=sa.String(length=20),
            nullable=False,
            existing_nullable=True,
        )
        batch_op.create_unique_constraint("uq_students_national_id", ["national_id"])
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=True,
            existing_nullable=False,
        )

    # UPDATE login fields for students only
    # Set students to use national_id for login instead of email
    op.execute("""
        UPDATE users
        SET 
            login_identifier = s.national_id,
            login_type = 'national_id'
        FROM students s
        WHERE users.id = s.user_id;
    """)


def downgrade():
    with op.batch_alter_table("students", schema=None) as batch_op:
        batch_op.drop_constraint("uq_students_national_id", type_="unique")
        batch_op.drop_column("national_id")
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("uq_users_login_identifier", type_="unique")
        batch_op.drop_column("login_identifier")
        batch_op.drop_column("login_type")
        batch_op.alter_column(
            "email",
            existing_type=sa.String(length=120),
            nullable=False,
        )
