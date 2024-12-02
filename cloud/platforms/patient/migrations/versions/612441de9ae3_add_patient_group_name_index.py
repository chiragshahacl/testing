"""
add_patient_group_name_index
"""

import sqlalchemy as sa
from alembic import op

revision = "612441de9ae3"
down_revision = "fdf82951c0bf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_patient_groups_name"),
        "patient_groups",
        [sa.text("lower(name)"), "name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_patient_groups_name", table_name="patient_groups")
