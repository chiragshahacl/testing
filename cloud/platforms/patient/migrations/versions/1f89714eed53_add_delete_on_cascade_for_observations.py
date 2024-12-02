"""
Delete
"""

from alembic import op

revision = "1f89714eed53"
down_revision = "8371f260a2d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("observations_subject_id_fkey", "observations", type_="foreignkey")
    op.create_foreign_key(
        None, "observations", "patients", ["subject_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint(None, "observations", type_="foreignkey")
    op.create_foreign_key(
        "observations_subject_id_fkey",
        "observations",
        "patients",
        ["subject_id"],
        ["id"],
    )
