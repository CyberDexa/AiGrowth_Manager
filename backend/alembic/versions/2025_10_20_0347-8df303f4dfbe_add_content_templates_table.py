"""add_content_templates_table

Revision ID: 8df303f4dfbe
Revises: a1b649b8da99
Create Date: 2025-10-20 03:47:22.819101+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8df303f4dfbe'
down_revision: Union[str, None] = 'a1b649b8da99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create content_templates table
    op.create_table(
        'content_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=True),
        sa.Column('template_structure', sa.Text(), nullable=False),
        sa.Column('placeholders', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_content_templates_business_id', 'content_templates', ['business_id'])
    op.create_index('ix_content_templates_category', 'content_templates', ['category'])
    op.create_index('ix_content_templates_platform', 'content_templates', ['platform'])
    op.create_index('ix_content_templates_is_public', 'content_templates', ['is_public'])


def downgrade() -> None:
    op.drop_index('ix_content_templates_is_public', table_name='content_templates')
    op.drop_index('ix_content_templates_platform', table_name='content_templates')
    op.drop_index('ix_content_templates_category', table_name='content_templates')
    op.drop_index('ix_content_templates_business_id', table_name='content_templates')
    op.drop_table('content_templates')
