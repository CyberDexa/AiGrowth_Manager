"""add_scheduled_posts_table

Revision ID: 17a5b8c9d0e1
Revises: 02f2fa21dac3
Create Date: 2025-01-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '17a5b8c9d0e1'
down_revision = '02f2fa21dac3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scheduled_posts table
    op.create_table(
        'scheduled_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('social_account_id', sa.Integer(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('platform_params', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('scheduled_for', sa.TIMESTAMP(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('published_post_id', sa.Integer(), nullable=True),
        sa.Column('platform_post_id', sa.String(length=255), nullable=True),
        sa.Column('platform_post_url', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_retry_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('published_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], ),
        sa.ForeignKeyConstraint(['published_post_id'], ['published_posts.id'], ),
    )
    
    # Create indexes
    op.create_index('ix_scheduled_posts_id', 'scheduled_posts', ['id'])
    op.create_index('ix_scheduled_posts_business_id', 'scheduled_posts', ['business_id'])
    op.create_index('ix_scheduled_posts_platform', 'scheduled_posts', ['platform'])
    op.create_index('ix_scheduled_posts_scheduled_for', 'scheduled_posts', ['scheduled_for'])
    op.create_index('ix_scheduled_posts_status', 'scheduled_posts', ['status'])
    op.create_index('ix_scheduled_posts_celery_task_id', 'scheduled_posts', ['celery_task_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_scheduled_posts_celery_task_id', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_status', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_scheduled_for', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_platform', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_business_id', table_name='scheduled_posts')
    op.drop_index('ix_scheduled_posts_id', table_name='scheduled_posts')
    
    # Drop table
    op.drop_table('scheduled_posts')
