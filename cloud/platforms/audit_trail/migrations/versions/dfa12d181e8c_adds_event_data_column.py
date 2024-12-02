"""
Adds event data column
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "dfa12d181e8c"
down_revision = "2b00ddfa995e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "internal_audit",
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("internal_audit", "event_data")
