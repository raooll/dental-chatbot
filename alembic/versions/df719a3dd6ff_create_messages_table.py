"""create messages table

Revision ID: df719a3dd6ff
Revises: 78db51f3addc
Create Date: 2025-11-07 14:46:26.573099

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "df719a3dd6ff"
down_revision: Union[str, Sequence[str], None] = "78db51f3addc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(12),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("sender_type", sa.String(50), nullable=False),  # Python-only enum
        sa.Column("content", sa.Text, nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("meta", sa.JSON, nullable=True),  # optional: attachments, AI info
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("messages")
