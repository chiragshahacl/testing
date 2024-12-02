"""
Flush remaining migrations
"""

import sqlalchemy as sa
from alembic import op

revision = "7d669afa85d8"
down_revision = "62284bf25015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "patient_groups",
        "description",
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
    )
    op.drop_index("ix_patient_groups_name", table_name="patient_groups")


def downgrade() -> None:
    op.create_index(
        "ix_patient_groups_name",
        "patient_groups",
        [sa.text("lower(name::text)"), "name"],
        unique=False,
    )
    op.alter_column(
        "patient_groups",
        "description",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
    )
