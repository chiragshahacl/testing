"""
add_device_code_to_alarms
"""

import sqlalchemy as sa
from alembic import op

revision = "8b413b4ad742"
down_revision = "5e9180cb66a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "observations",
        sa.Column("device_primary_identifier", sa.String(length=255), nullable=True),
    )
    op.add_column("observations", sa.Column("device_code", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("observations", "device_code")
    op.drop_column("observations", "device_primary_identifier")
