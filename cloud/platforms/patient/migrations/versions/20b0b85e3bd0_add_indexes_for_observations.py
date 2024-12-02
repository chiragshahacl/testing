"""
Add indexes for observations
"""

from alembic import op

revision = "20b0b85e3bd0"
down_revision = "8b413b4ad742"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_observations_code"), "observations", ["code"], unique=False)
    op.create_index(
        op.f("ix_observations_device_code"),
        "observations",
        ["device_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_observations_subject_id"), "observations", ["subject_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_observations_subject_id"), table_name="observations")
    op.drop_index(op.f("ix_observations_device_code"), table_name="observations")
    op.drop_index(op.f("ix_observations_code"), table_name="observations")
