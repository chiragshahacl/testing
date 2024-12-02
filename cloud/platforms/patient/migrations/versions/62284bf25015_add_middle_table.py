"""
Add middle table
"""

import sqlalchemy as sa
from alembic import op

revision = "62284bf25015"
down_revision = "682ab05ce01f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "patient_group_association_table",
        "patient_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.alter_column(
        "patient_group_association_table",
        "group_id",
        existing_type=sa.UUID(),
        nullable=False,
    )
    op.drop_constraint("patients_group_id_fkey", "patients", type_="foreignkey")
    op.drop_column("patients", "group_id")


def downgrade() -> None:
    op.add_column("patients", sa.Column("group_id", sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key(
        "patients_group_id_fkey", "patients", "patient_groups", ["group_id"], ["id"]
    )
    op.alter_column(
        "patient_group_association_table",
        "group_id",
        existing_type=sa.UUID(),
        nullable=True,
    )
    op.alter_column(
        "patient_group_association_table",
        "patient_id",
        existing_type=sa.UUID(),
        nullable=True,
    )
