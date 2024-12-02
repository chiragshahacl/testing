"""
Add physiological alerts table
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "937872246b27"
down_revision = "5c7fa9e062f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "physiological_alerts",
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("determination_time", sa.DateTime(), nullable=False),
        sa.Column("value_number", sa.DECIMAL(), nullable=True),
        sa.Column("value_text", sa.String(), nullable=True),
        sa.Column("device_primary_identifier", sa.String(), nullable=False),
        sa.Column("device_code", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
        ),
        sa.PrimaryKeyConstraint(
            "patient_id", "code", "device_primary_identifier", "determination_time"
        ),
    )
    op.create_index(
        op.f("ix_physiological_alerts_code"),
        "physiological_alerts",
        ["code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_physiological_alerts_device_code"),
        "physiological_alerts",
        ["device_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_physiological_alerts_patient_id"),
        "physiological_alerts",
        ["patient_id"],
        unique=False,
    )
    op.drop_table("vitals")
    op.drop_index("ix_new_vitals_timestamp", table_name="new_vitals")
    op.drop_table("new_vitals")


def downgrade() -> None:
    op.create_table(
        "new_vitals",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("event_type", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("timestamp", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column(
            "patient_primary_identifier",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "device_primary_identifier",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("vital_code", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("device_code", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("unit_code", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "datapoints",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="new_vitals_pkey"),
    )
    op.create_index("ix_new_vitals_timestamp", "new_vitals", ["timestamp"], unique=False)
    op.create_table(
        "vitals",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("event_type", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("timestamp", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column(
            "patient_primary_identifier",
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("code", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column(
            "message",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
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
        sa.PrimaryKeyConstraint("id", name="vitals_pkey"),
    )
    op.drop_index(op.f("ix_physiological_alerts_patient_id"), table_name="physiological_alerts")
    op.drop_index(op.f("ix_physiological_alerts_device_code"), table_name="physiological_alerts")
    op.drop_index(op.f("ix_physiological_alerts_code"), table_name="physiological_alerts")
    op.drop_table("physiological_alerts")
