"""
Remove
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "2397a65ef7bf"
down_revision = "fb4429a86ede"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("observations")


def downgrade() -> None:
    op.create_table(
        "observations",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("category", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("code", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("subject_id", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("effective_dt", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column("value_number", sa.NUMERIC(), autoincrement=False, nullable=True),
        sa.Column("value_text", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("is_alert", sa.BOOLEAN(), autoincrement=False, nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="observations_pkey"),
    )
