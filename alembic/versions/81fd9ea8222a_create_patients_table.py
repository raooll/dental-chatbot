"""create patients table

Revision ID: 81fd9ea8222a
Revises:
Create Date: 2025-11-07 13:30:19.651418
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81fd9ea8222a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — create the patients table."""
    op.create_table(
        "patients",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False, unique=True),
        sa.Column("date_of_birth", sa.Date, nullable=False),
        sa.Column("insurance_name", sa.String(length=255), nullable=True),
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
    op.create_index(
        op.f("ix_patients_phone_number"), "patients", ["phone_number"], unique=True
    )


def downgrade() -> None:
    """Downgrade schema — drop the patients table."""
    op.drop_index(op.f("ix_patients_phone_number"), table_name="patients")
    op.drop_table("patients")
