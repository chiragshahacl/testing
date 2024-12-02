"""
Fix group name index
"""

import sqlalchemy as sa
from alembic import op

revision = "aa33ccea10a0"
down_revision = "7d669afa85d8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_unique_group_name", "patient_groups", [sa.text("lower(name)")], unique=True)


def downgrade() -> None:
    op.drop_index("ix_unique_group_name", table_name="patient_groups")
