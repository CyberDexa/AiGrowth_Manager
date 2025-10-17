"""merge_heads

Revision ID: 1e42017c3543
Revises: 17a5b8c9d0e1, d4ac33648836
Create Date: 2025-10-14 09:28:47.055480+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e42017c3543'
down_revision: Union[str, None] = ('17a5b8c9d0e1', 'd4ac33648836')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
