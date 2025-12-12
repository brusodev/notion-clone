"""add tags and page_tags tables

Revision ID: 7adef4018204
Revises: dad7963312f4
Create Date: 2025-12-12 09:57:46.989338

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7adef4018204'
down_revision = 'dad7963312f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tags table
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'name', name='uq_workspace_tag_name')
    )

    # Create indexes for tags table
    op.create_index('ix_tags_name', 'tags', ['name'])
    op.create_index('ix_tags_workspace_id', 'tags', ['workspace_id'])
    op.create_index('ix_tags_workspace_id_name', 'tags', ['workspace_id', 'name'])

    # Create page_tags table
    op.create_table('page_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('page_id', 'tag_id', name='uq_page_tag')
    )

    # Create indexes for page_tags table
    op.create_index('ix_page_tags_page_id', 'page_tags', ['page_id'])
    op.create_index('ix_page_tags_tag_id', 'page_tags', ['tag_id'])
    op.create_index('ix_page_tags_page_id_tag_id', 'page_tags', ['page_id', 'tag_id'])


def downgrade() -> None:
    # Drop page_tags table and its indexes
    op.drop_index('ix_page_tags_page_id_tag_id', table_name='page_tags')
    op.drop_index('ix_page_tags_tag_id', table_name='page_tags')
    op.drop_index('ix_page_tags_page_id', table_name='page_tags')
    op.drop_table('page_tags')

    # Drop tags table and its indexes
    op.drop_index('ix_tags_workspace_id_name', table_name='tags')
    op.drop_index('ix_tags_workspace_id', table_name='tags')
    op.drop_index('ix_tags_name', table_name='tags')
    op.drop_table('tags')
