"""
Add device tables
"""

import sqlalchemy as sa
from alembic import op

revision = "e84a207714ed"
down_revision = "937872246b27"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("primary_identifier", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.UUID(), nullable=True),
        sa.Column("model_number", sa.String(length=255), nullable=True),
        sa.Column("gateway_id", sa.UUID(), nullable=True),
        sa.Column("subject_identifier", sa.String(length=255), nullable=True),
        sa.Column("audio_pause_enabled", sa.Boolean(), nullable=False),
        sa.Column("audio_enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["gateway_id"],
            ["devices.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("location"),
    )
    op.create_index(
        "ix_device_location",
        "devices",
        ["location"],
        unique=True,
        postgresql_using="btree",
    )
    op.create_index(
        "ix_device_primary_identifier",
        "devices",
        [sa.text("lower(primary_identifier)")],
        unique=True,
    )
    op.create_index(op.f("ix_devices_gateway_id"), "devices", ["gateway_id"], unique=False)
    op.create_index(op.f("ix_devices_model_number"), "devices", ["model_number"], unique=False)
    op.create_table(
        "device_alerts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column("priority", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_device_alerts_device_id"), "device_alerts", ["device_id"], unique=False
    )
    op.create_index(
        "ix_unique_device_id_with_code",
        "device_alerts",
        [sa.text("lower(code)"), "device_id"],
        unique=True,
    )
    op.create_table(
        "device_vital_ranges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("upper_limit", sa.Float(), nullable=True),
        sa.Column("lower_limit", sa.Float(), nullable=True),
        sa.Column("alert_condition_enabled", sa.Boolean(), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_device_vital_ranges_device_id"),
        "device_vital_ranges",
        ["device_id"],
        unique=False,
    )
    op.create_table(
        "technical_alerts",
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column("determination_time", sa.DateTime(), nullable=False),
        sa.Column("value_number", sa.DECIMAL(), nullable=True),
        sa.Column("value_text", sa.String(), nullable=True),
        sa.Column("patient_primary_identifier", sa.String(), nullable=False),
        sa.Column("device_code", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
        ),
        sa.PrimaryKeyConstraint(
            "device_id", "code", "patient_primary_identifier", "determination_time"
        ),
    )
    op.create_index(op.f("ix_technical_alerts_code"), "technical_alerts", ["code"], unique=False)
    op.create_index(
        op.f("ix_technical_alerts_device_code"),
        "technical_alerts",
        ["device_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_technical_alerts_device_id"),
        "technical_alerts",
        ["device_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_technical_alerts_device_id"), table_name="technical_alerts")
    op.drop_index(op.f("ix_technical_alerts_device_code"), table_name="technical_alerts")
    op.drop_index(op.f("ix_technical_alerts_code"), table_name="technical_alerts")
    op.drop_table("technical_alerts")
    op.drop_index(op.f("ix_device_vital_ranges_device_id"), table_name="device_vital_ranges")
    op.drop_table("device_vital_ranges")
    op.drop_index("ix_unique_device_id_with_code", table_name="device_alerts")
    op.drop_index(op.f("ix_device_alerts_device_id"), table_name="device_alerts")
    op.drop_table("device_alerts")
    op.drop_index(op.f("ix_devices_model_number"), table_name="devices")
    op.drop_index(op.f("ix_devices_gateway_id"), table_name="devices")
    op.drop_index("ix_device_primary_identifier", table_name="devices")
    op.drop_index("ix_device_location", table_name="devices", postgresql_using="btree")
    op.drop_table("devices")
