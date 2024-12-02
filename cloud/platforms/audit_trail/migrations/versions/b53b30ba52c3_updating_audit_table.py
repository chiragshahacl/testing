"""
updating-audit-table
"""

import sqlalchemy as sa
from alembic import op

revision = "b53b30ba52c3"
down_revision = "c2f8dca5ec51"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("internal_audit", sa.Column("emitted_by", sa.String(length=255), nullable=False))
    op.add_column(
        "internal_audit",
        sa.Column("performed_by", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("internal_audit", "performed_by")
    op.drop_column("internal_audit", "emitted_by")
