"""
Add message id
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

revision = "2b00ddfa995e"
down_revision = "840f107f09d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("internal_audit", sa.Column("event_type", sa.String(length=100), nullable=True))
    op.add_column("internal_audit", sa.Column("message_id", sa.UUID(), nullable=True))
    conn = op.get_bind()
    session = Session(bind=conn)
    session.execute(sa.text("UPDATE internal_audit SET message_id=gen_random_uuid()"))
    session.commit()
    op.alter_column("internal_audit", "message_id", nullable=False)
    op.create_unique_constraint("unique_message_id", "internal_audit", ["message_id"])


def downgrade() -> None:
    op.drop_constraint("unique_message_id", "internal_audit", type_="unique")
    op.drop_column("internal_audit", "message_id")
    op.drop_column("internal_audit", "event_type")
