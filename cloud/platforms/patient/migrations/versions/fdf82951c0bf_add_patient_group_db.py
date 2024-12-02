"""
add_patient_group_db
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "fdf82951c0bf"
down_revision = "a727c9bd8b23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patient_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("patients", sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, "patients", "patient_groups", ["group_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "patients", type_="foreignkey")
    op.drop_column("patients", "group_id")
    op.drop_table("patient_groups")
