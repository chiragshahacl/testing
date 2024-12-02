"""
Add tenant id
"""

import sqlalchemy as sa
from alembic import op

revision = "2fe6ef23d75f"
down_revision = "b8837eb8f77d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing index in favor of composite index
    op.drop_index(op.f("ix_patient_primary_identifier"), table_name="patients")

    # Add `tenant_id` column with `sibel` as default
    op.add_column("patients", sa.Column("tenant_id", sa.String(length=36), nullable=True))
    op.execute("UPDATE patients SET tenant_id = 'sibel' WHERE tenant_id IS NULL")
    op.alter_column(table_name="patients", column_name="tenant_id", nullable=False)

    # Create lower(tenant_id) + lower(primary_identifier) index
    op.create_index(
        op.f("ix_primary_identifier_tenant_id"),
        "patients",
        [
            sa.text("lower(tenant_id)"),
            sa.text("lower(primary_identifier)"),
        ],
        unique=True,
    )

    # Create lower(tenant_id) + id index
    op.create_index(
        op.f("ix_patient_id_tenant_id"),
        "patients",
        [sa.text("lower(tenant_id)"), "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_primary_identifier_tenant_id")
    op.drop_column("patients", "tenant_id")
    op.create_index(
        op.f("ix_patient_primary_identifier"),
        "patients",
        [sa.text("lower(primary_identifier)"), "primary_identifier"],
    )
