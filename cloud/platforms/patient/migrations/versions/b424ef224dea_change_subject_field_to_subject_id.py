"""
change_subject_field_to_subject_id
"""

import sqlalchemy as sa
from alembic import op

revision = "b424ef224dea"
down_revision = "84c8b0d4769e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "observations",
        "subject",
        nullable=False,
        new_column_name="subject_id",
        existing_type=sa.VARCHAR(length=255),
    )


def downgrade() -> None:
    op.alter_column(
        "observations",
        "subject_id",
        nullable=False,
        new_column_name="subject",
        existing_type=sa.VARCHAR(length=255),
    )
