"""add_meta_fields_to_social_accounts

Revision ID: d87a1f121c3c
Revises: 02f2fa21dac3
Create Date: 2025-10-13 09:14:28.748033+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd87a1f121c3c'
down_revision: Union[str, None] = '02f2fa21dac3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Meta-specific fields to social_accounts table
    op.add_column('social_accounts', sa.Column('page_id', sa.String(), nullable=True))
    op.add_column('social_accounts', sa.Column('page_name', sa.String(), nullable=True))
    op.add_column('social_accounts', sa.Column('page_access_token', sa.Text(), nullable=True))
    op.add_column('social_accounts', sa.Column('instagram_account_id', sa.String(), nullable=True))
    op.add_column('social_accounts', sa.Column('instagram_username', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove Meta-specific fields
    op.drop_column('social_accounts', 'instagram_username')
    op.drop_column('social_accounts', 'instagram_account_id')
    op.drop_column('social_accounts', 'page_access_token')
    op.drop_column('social_accounts', 'page_name')
    op.drop_column('social_accounts', 'page_id')
