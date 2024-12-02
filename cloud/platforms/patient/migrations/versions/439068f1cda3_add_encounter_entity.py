"""
add encounter entity
"""

import sqlalchemy as sa
from alembic import op

revision = "439068f1cda3"
down_revision = "19378d6bf54e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "encounters",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("subject_id", sa.UUID(), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PLANNED",
                "IN_PROGRESS",
                "COMPLETED",
                "CANCELLED",
                name="encounter_status",
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["patients.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id"),
        sa.UniqueConstraint("subject_id"),
    )
    op.create_index("ix_encounter_device_id", "encounters", ["device_id"], unique=True)
    op.create_index("ix_encounter_subject_id", "encounters", ["subject_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_encounter_subject_id", table_name="encounters")
    op.drop_index("ix_encounter_device_id", table_name="encounters")
    op.drop_table("encounters")
    op.execute("DROP TYPE encounter_status")
