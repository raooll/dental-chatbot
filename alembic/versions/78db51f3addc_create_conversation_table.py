"""create conversation table

Revision ID: 78db51f3addc
Revises: 3d76e3776eb0
Create Date: 2025-11-07 14:41:48.308318

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78db51f3addc'
down_revision: Union[str, Sequence[str], None] = '3d76e3776eb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        "conversations",
    sa.Column("id", sa.String(length=12), primary_key=True),
    sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=True),
    sa.Column("status", sa.String(50), nullable=False, server_default="active"),
    sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),

    sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.func.now(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=False), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("conversations")
