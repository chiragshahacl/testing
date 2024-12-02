"""
make_birthdate_non_nullable
"""

import sqlalchemy as sa
from alembic import op

revision = "1b5d81fe4dbc"
down_revision = "4a958c4b624e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("patients", "birth_date", existing_type=sa.DATE(), nullable=False)


def downgrade() -> None:
    op.alter_column("patients", "birth_date", existing_type=sa.DATE(), nullable=True)
