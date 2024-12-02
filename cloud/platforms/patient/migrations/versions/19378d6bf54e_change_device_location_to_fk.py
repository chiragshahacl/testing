"""
change_device_location_to_fk
"""

import sqlalchemy as sa
from alembic import op

revision = "19378d6bf54e"
down_revision = "1f89714eed53"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("devices", sa.Column("location_id", sa.UUID(), nullable=True))
    op.drop_constraint("devices_location_key", "devices", type_="unique")
    op.drop_index("ix_device_location", table_name="devices")
    op.create_index("ix_device_location_id", "devices", ["location_id"], unique=True)
    op.create_unique_constraint(None, "devices", ["location_id"])
    op.create_foreign_key(None, "devices", "beds", ["location_id"], ["id"])
    op.drop_column("devices", "location")


def downgrade() -> None:
    op.add_column("devices", sa.Column("location", sa.UUID(), autoincrement=False, nullable=True))
    op.drop_constraint(None, "devices", type_="foreignkey")
    op.drop_constraint(None, "devices", type_="unique")
    op.drop_index("ix_device_location_id", table_name="devices")
    op.create_index("ix_device_location", "devices", ["location"], unique=True)
    op.create_unique_constraint("devices_location_key", "devices", ["location"])
    op.drop_column("devices", "location_id")
