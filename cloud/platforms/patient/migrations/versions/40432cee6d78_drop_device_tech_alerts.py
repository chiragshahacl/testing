"""
Drop device tech alerts
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "40432cee6d78"
down_revision = "e84a207714ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_technical_alerts_code", table_name="technical_alerts")
    op.drop_index("ix_technical_alerts_device_code", table_name="technical_alerts")
    op.drop_index("ix_technical_alerts_device_id", table_name="technical_alerts")
    op.drop_table("technical_alerts")
    op.alter_column(
        "devices",
        "primary_identifier",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
    )
    op.alter_column("devices", "model_number", existing_type=sa.VARCHAR(length=255), nullable=False)


def downgrade() -> None:
    op.alter_column("devices", "model_number", existing_type=sa.VARCHAR(length=255), nullable=True)
    op.alter_column(
        "devices",
        "primary_identifier",
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
    )
    op.create_table(
        "technical_alerts",
        sa.Column("code", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("device_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "determination_time",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("value_number", sa.NUMERIC(), autoincrement=False, nullable=True),
        sa.Column("value_text", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "patient_primary_identifier",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("device_code", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"], ["devices.id"], name="technical_alerts_device_id_fkey"
        ),
        sa.PrimaryKeyConstraint(
            "device_id",
            "code",
            "patient_primary_identifier",
            "determination_time",
            name="technical_alerts_pkey",
        ),
    )
    op.create_index(
        "ix_technical_alerts_device_id", "technical_alerts", ["device_id"], unique=False
    )
    op.create_index(
        "ix_technical_alerts_device_code",
        "technical_alerts",
        ["device_code"],
        unique=False,
    )
    op.create_index("ix_technical_alerts_code", "technical_alerts", ["code"], unique=False)
