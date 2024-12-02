"""
add_patient_primary_identifier_to_alert_log
"""

import sqlalchemy as sa
from alembic import op

revision = "95a9782cce7a"
down_revision = "19943ebcc90e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "alerts_log", sa.Column("patient_primary_identifier", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("alerts_log", "patient_primary_identifier")
