"""add_images_table

Revision ID: 8aedf3a5c925
Revises: d87a1f121c3c
Create Date: 2025-10-13 12:57:31.414183+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8aedf3a5c925'
down_revision: Union[str, None] = 'd87a1f121c3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create images table
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_provider', sa.String(length=20), nullable=False),
        sa.Column('storage_url', sa.Text(), nullable=False),
        sa.Column('cloudinary_public_id', sa.String(length=255), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(length=50), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ai_prompt', sa.Text(), nullable=True),
        sa.Column('ai_model', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE')
    )
    
    # Create indexes for performance
    op.create_index('ix_images_id', 'images', ['id'])
    op.create_index('ix_images_business_id', 'images', ['business_id'])
    op.create_index('ix_images_created_at', 'images', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_images_created_at', table_name='images')
    op.drop_index('ix_images_business_id', table_name='images')
    op.drop_index('ix_images_id', table_name='images')
    
    # Drop table
    op.drop_table('images')
