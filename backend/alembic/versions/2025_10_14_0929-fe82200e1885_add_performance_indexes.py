"""add_performance_indexes

Revision ID: fe82200e1885
Revises: 1e42017c3543
Create Date: 2025-10-14 09:29:23.681015+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe82200e1885'
down_revision: Union[str, None] = '1e42017c3543'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add performance indexes for optimizing common queries.
    
    Indexes created:
    1. social_accounts: (business_id, platform, is_active) - Fast account lookup
    2. published_posts: (business_id, published_at DESC) - Recent posts query
    3. scheduled_posts: (status, scheduled_for) - Pending posts lookup (partial index) [if table exists]
    4. scheduled_posts: (celery_task_id) - Task cancellation lookup (partial index) [if table exists]
    5. scheduled_posts: (business_id, status, scheduled_for) - Dashboard queries [if table exists]
    """
    
    # Get connection to check if tables exist
    conn = op.get_bind()
    
    # Index 1: Social Accounts - Fast lookup by business + platform + active status
    # Used by: OAuth flow, publishing endpoints
    op.create_index(
        'idx_social_accounts_business_platform_active',
        'social_accounts',
        ['business_id', 'platform', 'is_active'],
        unique=False
    )
    
    # Index 2: Published Posts - Recent posts by business (descending order)
    # Used by: Analytics, dashboard, post history
    op.create_index(
        'idx_published_posts_business_published_desc',
        'published_posts',
        ['business_id', sa.text('published_at DESC')],
        unique=False,
        postgresql_using='btree'
    )
    
    # Index 6: Published Posts - Platform + published date
    # Used by: Platform-specific analytics, performance tracking
    op.create_index(
        'idx_published_posts_platform_published',
        'published_posts',
        ['platform', sa.text('published_at DESC')],
        unique=False,
        postgresql_using='btree'
    )
    
    # Index 7: Social Accounts - Platform user ID lookup
    # Used by: OAuth callback, account verification
    op.create_index(
        'idx_social_accounts_platform_user',
        'social_accounts',
        ['platform', 'platform_user_id'],
        unique=False
    )
    
    # Check if scheduled_posts table exists before creating indexes
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'scheduled_posts'
        )
    """))
    scheduled_posts_exists = result.scalar()
    
    if scheduled_posts_exists:
        # Index 3: Scheduled Posts - Pending posts lookup (partial index)
        # Used by: Celery beat task (check_and_publish_scheduled_posts)
        op.execute("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_posts_pending_scheduled
            ON scheduled_posts (status, scheduled_for)
            WHERE status IN ('pending', 'queued')
        """)
        
        # Index 4: Scheduled Posts - Celery task ID lookup (partial index)
        # Used by: Task cancellation endpoint
        op.execute("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_posts_celery_task
            ON scheduled_posts (celery_task_id)
            WHERE celery_task_id IS NOT NULL
        """)
        
        # Index 5: Scheduled Posts - Dashboard queries (business + status + date)
        # Used by: List scheduled posts endpoint, calendar view
        op.execute("""
            CREATE INDEX IF NOT EXISTS idx_scheduled_posts_business_status_scheduled
            ON scheduled_posts (business_id, status, scheduled_for)
        """)


def downgrade() -> None:
    """Remove performance indexes"""
    
    # Drop indexes in reverse order
    op.drop_index('idx_social_accounts_platform_user', table_name='social_accounts')
    op.drop_index('idx_published_posts_platform_published', table_name='published_posts')
    op.drop_index('idx_scheduled_posts_business_status_scheduled', table_name='scheduled_posts')
    op.execute('DROP INDEX IF EXISTS idx_scheduled_posts_celery_task')
    op.execute('DROP INDEX IF EXISTS idx_scheduled_posts_pending_scheduled')
    op.drop_index('idx_published_posts_business_published_desc', table_name='published_posts')
    op.drop_index('idx_social_accounts_business_platform_active', table_name='social_accounts')
