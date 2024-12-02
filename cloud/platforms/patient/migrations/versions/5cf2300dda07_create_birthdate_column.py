"""
create_birthdate_column
"""

import sqlalchemy as sa
from alembic import op

revision = "5cf2300dda07"
down_revision = "49568342159e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("birth_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("patients", "birth_date")
