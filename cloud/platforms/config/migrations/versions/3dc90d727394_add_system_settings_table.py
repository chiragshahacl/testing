"""
Add system settings table
"""

import sqlalchemy as sa
from alembic import op

revision = "3dc90d727394"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_vitals_retention_period_ms", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("system_settings")
