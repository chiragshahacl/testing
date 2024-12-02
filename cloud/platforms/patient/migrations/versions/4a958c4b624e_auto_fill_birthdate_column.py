"""
auto_fill_birthdate_column
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

revision = "4a958c4b624e"
down_revision = "5cf2300dda07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    patient = table("patients", column("birth_date", sa.Date))
    op.execute(patient.update().values({"birth_date": op.inline_literal("2020-03-29")}))


def downgrade() -> None:
    pass
