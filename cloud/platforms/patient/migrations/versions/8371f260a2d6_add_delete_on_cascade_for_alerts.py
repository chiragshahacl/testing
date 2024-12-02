"""
Add delete cascade on physiological alerts
"""

from alembic import op

revision = "8371f260a2d6"
down_revision = "40432cee6d78"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "physiological_alerts_patient_id_fkey",
        "physiological_alerts",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "physiological_alerts",
        "patients",
        ["patient_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(None, "physiological_alerts", type_="foreignkey")
    op.create_foreign_key(
        "physiological_alerts_patient_id_fkey",
        "physiological_alerts",
        "patients",
        ["patient_id"],
        ["id"],
    )
