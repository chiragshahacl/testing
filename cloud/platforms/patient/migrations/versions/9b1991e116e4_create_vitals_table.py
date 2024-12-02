"""
create_vitals_table
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "9b1991e116e4"
down_revision = "7d5f51ecdcb6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vitals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("patient_primary_identifier", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.Column("message", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("vitals")
