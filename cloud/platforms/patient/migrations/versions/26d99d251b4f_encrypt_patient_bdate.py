"""
encrypt patient bdate
"""

import sqlalchemy as sa
from alembic import op

from app.common.models import PGPDate
from app.settings import config

revision = "26d99d251b4f"
down_revision = "d1d523fed38c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "patients",
        sa.Column(
            "bytea_bdate",
            PGPDate(config.DB_ENCRYPTION_KEY.get_secret_value()),
            nullable=True,
        ),
    )
    op.execute(
        f"UPDATE patients SET bytea_bdate = pgp_sym_encrypt(CAST(birth_date AS TEXT), "
        f"'{config.DB_ENCRYPTION_KEY.get_secret_value()}')"
    )
    op.drop_column("patients", "birth_date")
    op.alter_column(
        "patients",
        "bytea_bdate",
        existing_type=PGPDate(config.DB_ENCRYPTION_KEY.get_secret_value()),
        new_column_name="birth_date",
    )


def downgrade() -> None:
    op.add_column("patients", sa.Column("birth_date_2", sa.Date(), nullable=True))

    op.execute(
        f"UPDATE patients SET birth_date_2 = CAST(pgp_sym_decrypt(birth_date, "
        f"'{config.DB_ENCRYPTION_KEY.get_secret_value()}') AS DATE)"
    )

    op.drop_column("patients", "birth_date")

    op.alter_column(
        "patients",
        "birth_date_2",
        existing_type=sa.Date(),
        nullable=True,
        new_column_name="birth_date",
    )
