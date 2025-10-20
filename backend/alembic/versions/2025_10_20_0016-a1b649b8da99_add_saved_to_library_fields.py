"""add_saved_to_library_fields

Revision ID: a1b649b8da99
Revises: fe82200e1885
Create Date: 2025-10-20 00:16:13.933425+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b649b8da99'
down_revision: Union[str, None] = 'fe82200e1885'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add saved_to_library to content table
    op.add_column('content', sa.Column('saved_to_library', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('content', sa.Column('library_saved_at', sa.DateTime(), nullable=True))
    
    # Add saved_to_library to published_posts table
    op.add_column('published_posts', sa.Column('saved_to_library', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('published_posts', sa.Column('library_saved_at', sa.TIMESTAMP(), nullable=True))
    
    # Create indexes for efficient library queries
    op.create_index('ix_content_saved_to_library', 'content', ['saved_to_library', 'business_id'])
    op.create_index('ix_published_posts_saved_to_library', 'published_posts', ['saved_to_library', 'business_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_published_posts_saved_to_library', table_name='published_posts')
    op.drop_index('ix_content_saved_to_library', table_name='content')
    
    # Remove columns from published_posts
    op.drop_column('published_posts', 'library_saved_at')
    op.drop_column('published_posts', 'saved_to_library')
    
    # Remove columns from content
    op.drop_column('content', 'library_saved_at')
    op.drop_column('content', 'saved_to_library')
