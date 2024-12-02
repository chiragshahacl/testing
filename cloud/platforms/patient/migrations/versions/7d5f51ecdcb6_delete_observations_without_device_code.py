"""
delete_observations_without_device_code
"""

from alembic import op

revision = "7d5f51ecdcb6"
down_revision = "20b0b85e3bd0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Delete observations where device_code is NULL
    op.execute("DELETE FROM observations WHERE device_code IS NULL")


def downgrade() -> None:
    # No need to define a downgrade operation for this migration
    pass
