"""
Rename phy alerts table to audit
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "4a2fa0837bf2"
down_revision = "d8f5684aa3e9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("physiological_alerts", "alerts_log")


def downgrade() -> None:
    op.rename_table("alerts_log", "physiological_alerts")
