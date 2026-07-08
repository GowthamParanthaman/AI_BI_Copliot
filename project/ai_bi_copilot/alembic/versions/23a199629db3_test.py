"""test

Revision ID: 23a199629db3
Revises: 9f6323a2835f
Create Date: 2026-06-10 21:54:00.562941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23a199629db3'
down_revision: Union[str, Sequence[str], None] = '9f6323a2835f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
