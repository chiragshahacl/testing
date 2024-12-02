"""
Add event name column
"""

import sqlalchemy as sa
from alembic import op

revision = "840f107f09d7"
down_revision = "b53b30ba52c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("internal_audit", sa.Column("event_name", sa.String(length=100), nullable=False))


def downgrade() -> None:
    op.drop_column("internal_audit", "event_name")
