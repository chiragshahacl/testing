"""
Make
"""

import sqlalchemy as sa
from alembic import op

revision = "5e9180cb66a4"
down_revision = "41c5f6025860"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("patients", "birth_date", existing_type=sa.DATE(), nullable=True)


def downgrade() -> None:
    op.alter_column("patients", "birth_date", existing_type=sa.DATE(), nullable=False)
