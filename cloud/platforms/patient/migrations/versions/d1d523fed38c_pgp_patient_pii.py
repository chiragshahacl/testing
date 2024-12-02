"""
Apply PGP encryption to  patient PII
"""

import sqlalchemy as sa
from alembic import op

from app.common.models import PGPString
from app.settings import config

revision = "d1d523fed38c"
down_revision = "63822a8b32b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "patients",
        "given_name",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.add_column(
        "patients",
        sa.Column(
            "bytea_given_name",
            PGPString(config.DB_ENCRYPTION_KEY.get_secret_value()),
            nullable=True,
        ),
    )
    op.add_column(
        "patients",
        sa.Column(
            "bytea_family_name",
            PGPString(config.DB_ENCRYPTION_KEY.get_secret_value()),
            nullable=True,
        ),
    )
    op.execute(
        f"UPDATE patients SET bytea_given_name = "
        f"pgp_sym_encrypt(given_name, '{config.DB_ENCRYPTION_KEY.get_secret_value()}'), "
        f"bytea_family_name = pgp_sym_encrypt(family_name, "
        f"'{config.DB_ENCRYPTION_KEY.get_secret_value()}');"
    )
    op.drop_column("patients", "given_name")
    op.drop_column("patients", "family_name")
    op.alter_column(
        "patients",
        "bytea_given_name",
        existing_type=PGPString(config.DB_ENCRYPTION_KEY.get_secret_value()),
        new_column_name="given_name",
    )
    op.alter_column(
        "patients",
        "bytea_family_name",
        existing_type=PGPString(config.DB_ENCRYPTION_KEY.get_secret_value()),
        new_column_name="family_name",
    )


def downgrade() -> None:
    op.add_column("patients", sa.Column("given_name_2", sa.VARCHAR(), nullable=True))
    op.add_column("patients", sa.Column("family_name_2", sa.VARCHAR(), nullable=True))

    op.execute(
        f"UPDATE patients "
        f"SET given_name_2 = pgp_sym_decrypt("
        f"given_name, '{config.DB_ENCRYPTION_KEY.get_secret_value()}'),"
        f"family_name_2 = pgp_sym_decrypt("
        f"family_name, '{config.DB_ENCRYPTION_KEY.get_secret_value()}');"
    )

    op.drop_column("patients", "given_name")
    op.drop_column("patients", "family_name")

    op.alter_column(
        "patients",
        "given_name_2",
        existing_type=sa.VARCHAR(),
        nullable=False,
        new_column_name="given_name",
    )
    op.alter_column(
        "patients",
        "family_name_2",
        existing_type=sa.VARCHAR(),
        nullable=False,
        new_column_name="family_name",
    )
