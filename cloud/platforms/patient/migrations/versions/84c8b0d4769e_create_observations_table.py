"""
create_observations_table
"""

import sqlalchemy as sa
from alembic import op

revision = "84c8b0d4769e"
down_revision = "1b5d81fe4dbc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "observations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("effective_dt", sa.DateTime(), nullable=False),
        sa.Column("value_number", sa.DECIMAL(), nullable=True),
        sa.Column("value_text", sa.String(), nullable=True),
        sa.Column("is_alert", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("observations")
