"""
Add Patient Table
"""

import sqlalchemy as sa
from alembic import op

from app.common.models import GenderType

revision = "8e465898ee25"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("given_name", sa.String(length=255), nullable=False),
        sa.Column("family_name", sa.String(), nullable=False),
        sa.Column("gender", GenderType(), nullable=False),
        sa.CheckConstraint("char_length(given_name) > 0", name="given_name_min_len"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("patients")
