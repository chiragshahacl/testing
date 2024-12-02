"""
create_group_patient_relationship_table
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "682ab05ce01f"
down_revision = "612441de9ae3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patient_group_association_table",
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["patient_groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
        ),
    )


def downgrade() -> None:
    op.drop_table("patient_group_association_table")
