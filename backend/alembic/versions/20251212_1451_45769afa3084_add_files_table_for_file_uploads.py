"""add files table for file uploads

Revision ID: 45769afa3084
Revises: 7adef4018204
Create Date: 2025-12-12 14:51:30.310567

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '45769afa3084'
down_revision = '7adef4018204'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create files table
    op.create_table('files',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.Enum('IMAGE', 'VIDEO', 'DOCUMENT', 'AUDIO', 'OTHER', name='filetype', create_type=False), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('storage_provider', sa.String(length=50), nullable=False),
        sa.Column('storage_url', sa.String(length=500), nullable=False),
        sa.Column('storage_id', sa.String(length=255), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('block_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['block_id'], ['blocks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_files_block', 'files', ['block_id'])
    op.create_index('ix_files_page', 'files', ['page_id'])
    op.create_index('ix_files_uploaded_by', 'files', ['uploaded_by'])
    op.create_index('ix_files_workspace_id', 'files', ['workspace_id'])
    op.create_index('ix_files_workspace_type', 'files', ['workspace_id', 'file_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_files_workspace_type', table_name='files')
    op.drop_index('ix_files_workspace_id', table_name='files')
    op.drop_index('ix_files_uploaded_by', table_name='files')
    op.drop_index('ix_files_page', table_name='files')
    op.drop_index('ix_files_block', table_name='files')

    # Drop table
    op.drop_table('files')

    # Drop enum
    file_type_enum = postgresql.ENUM('IMAGE', 'VIDEO', 'DOCUMENT', 'AUDIO', 'OTHER', name='filetype')
    file_type_enum.drop(op.get_bind(), checkfirst=True)
