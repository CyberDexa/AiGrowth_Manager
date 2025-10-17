"""add_analytics_tables

Revision ID: d4ac33648836
Revises: 8aedf3a5c925
Create Date: 2025-10-13 15:38:36.773282+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4ac33648836'
down_revision: Union[str, None] = '8aedf3a5c925'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create post_analytics table
    op.create_table(
        'post_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('published_post_id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        
        # Engagement Metrics
        sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comments_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('shares_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reactions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('retweets_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quote_tweets_count', sa.Integer(), nullable=False, server_default='0'),
        
        # Reach Metrics
        sa.Column('impressions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reach', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('clicks', sa.Integer(), nullable=False, server_default='0'),
        
        # Video Metrics
        sa.Column('video_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('video_watch_time', sa.Integer(), nullable=False, server_default='0'),
        
        # Calculated Metrics
        sa.Column('engagement_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.0'),
        sa.Column('click_through_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.0'),
        
        # Metadata
        sa.Column('fetched_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('platform_post_id', sa.String(length=255), nullable=True),
        sa.Column('platform_post_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['published_post_id'], ['published_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for post_analytics
    op.create_index('ix_post_analytics_id', 'post_analytics', ['id'])
    op.create_index('ix_post_analytics_post_id', 'post_analytics', ['published_post_id'])
    op.create_index('ix_post_analytics_business_id', 'post_analytics', ['business_id'])
    op.create_index('ix_post_analytics_platform', 'post_analytics', ['platform'])
    op.create_index('ix_post_analytics_fetched_at', 'post_analytics', ['fetched_at'])
    
    # Create analytics_summaries table
    op.create_table(
        'analytics_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        
        # Time Period
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        
        # Summary Metrics
        sa.Column('total_posts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_likes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_comments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_shares', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_impressions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_reach', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_clicks', sa.Integer(), nullable=False, server_default='0'),
        
        # Calculated Metrics
        sa.Column('avg_engagement_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.0'),
        sa.Column('avg_impressions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('follower_growth', sa.Integer(), nullable=False, server_default='0'),
        
        # Best Performing
        sa.Column('best_post_id', sa.Integer(), nullable=True),
        sa.Column('best_post_engagement_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['best_post_id'], ['published_posts.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for analytics_summaries
    op.create_index('ix_analytics_summaries_id', 'analytics_summaries', ['id'])
    op.create_index('ix_analytics_summaries_business', 'analytics_summaries', ['business_id'])
    op.create_index('ix_analytics_summaries_period', 'analytics_summaries', ['period_start', 'period_end'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_analytics_summaries_period', 'analytics_summaries')
    op.drop_index('ix_analytics_summaries_business', 'analytics_summaries')
    op.drop_index('ix_analytics_summaries_id', 'analytics_summaries')
    
    op.drop_index('ix_post_analytics_fetched_at', 'post_analytics')
    op.drop_index('ix_post_analytics_platform', 'post_analytics')
    op.drop_index('ix_post_analytics_business_id', 'post_analytics')
    op.drop_index('ix_post_analytics_post_id', 'post_analytics')
    op.drop_index('ix_post_analytics_id', 'post_analytics')
    
    # Drop tables
    op.drop_table('analytics_summaries')
    op.drop_table('post_analytics')
