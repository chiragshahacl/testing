"""
Add Patient Identifier Field
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.common.models import GenderType

revision = "b8837eb8f77d"
down_revision = "18e9ae3a5459"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("patients")
    op.create_table(
        "patients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("primary_identifier", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("given_name", sa.String(length=255), nullable=False),
        sa.Column("family_name", sa.String(), nullable=False),
        sa.Column("gender", GenderType(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("char_length(given_name) > 0", name="given_name_min_len"),
        sa.CheckConstraint(
            "char_length(primary_identifier) > 0", name="primary_identifier_min_len"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_patient_primary_identifier"),
        "patients",
        [sa.text("lower(primary_identifier)"), "primary_identifier"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_patient_primary_identifier"), table_name="patients")
    op.drop_table("patients")
