"""Add analytics models

Revision ID: a1b2c3d4e5f6
Revises: 2327ab4bdcf8
Create Date: 2025-10-12 01:15:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '2327ab4bdcf8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create content_metrics table
    op.create_table(
        'content_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('views', sa.Integer(), server_default='0', nullable=True),
        sa.Column('likes', sa.Integer(), server_default='0', nullable=True),
        sa.Column('shares', sa.Integer(), server_default='0', nullable=True),
        sa.Column('comments', sa.Integer(), server_default='0', nullable=True),
        sa.Column('clicks', sa.Integer(), server_default='0', nullable=True),
        sa.Column('engagement_rate', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('click_through_rate', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('measured_at', sa.DateTime(), nullable=False),
        sa.Column('platform_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_metrics_id'), 'content_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_content_metrics_content_id'), 'content_metrics', ['content_id'], unique=False)
    
    # Create business_metrics table
    op.create_table(
        'business_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('total_posts', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_reach', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_engagement', sa.Integer(), server_default='0', nullable=True),
        sa.Column('avg_engagement_rate', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('platform_breakdown', sa.JSON(), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_metrics_id'), 'business_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_business_metrics_business_id'), 'business_metrics', ['business_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_business_metrics_business_id'), table_name='business_metrics')
    op.drop_index(op.f('ix_business_metrics_id'), table_name='business_metrics')
    op.drop_table('business_metrics')
    
    op.drop_index(op.f('ix_content_metrics_content_id'), table_name='content_metrics')
    op.drop_index(op.f('ix_content_metrics_id'), table_name='content_metrics')
    op.drop_table('content_metrics')
