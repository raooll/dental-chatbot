"""create booking table

Revision ID: 3d76e3776eb0
Revises: 81fd9ea8222a
Create Date: 2025-11-07 13:38:28.268976

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3d76e3776eb0"
down_revision: Union[str, Sequence[str], None] = "81fd9ea8222a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "appointments",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column(
            "patient_id",
            sa.String(length=12),
            sa.ForeignKey("patients.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("appointment_type", sa.String(length=50), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column(
            "start_time", sa.DateTime(timezone=False), nullable=False, index=True
        ),
        sa.Column("end_time", sa.DateTime(timezone=False), nullable=False),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="scheduled"
        ),
        sa.Column("notes", sa.Text(), nullable=True),
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
    op.drop_table("appointments")
