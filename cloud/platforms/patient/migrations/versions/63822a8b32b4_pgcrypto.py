"""
pgcrypto
"""

from alembic import op

revision = "63822a8b32b4"
down_revision = "b61cfa32b871"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
