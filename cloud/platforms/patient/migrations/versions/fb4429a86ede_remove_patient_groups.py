"""
Remove patient groups
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "fb4429a86ede"
down_revision = "b424ef224dea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("patient_group_association_table")
    op.drop_index("ix_unique_patient_group_name", table_name="patient_groups")
    op.drop_table("patient_groups")


def downgrade() -> None:
    op.create_table(
        "patient_groups",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column("description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="patient_groups_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_index(
        "ix_unique_patient_group_name",
        "patient_groups",
        [sa.text("lower(name::text)")],
        unique=False,
    )
    op.create_table(
        "patient_group_association_table",
        sa.Column("patient_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("group_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["patient_groups.id"],
            name="patient_group_association_table_group_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="patient_group_association_table_patient_id_fkey",
        ),
    )
