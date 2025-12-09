"""add_page_versions_table

Revision ID: 9765bd696560
Revises: 8d29e3bec67a
Create Date: 2025-12-09 10:28:10.888941

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = '9765bd696560'
down_revision = '8d29e3bec67a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create page_versions table
    op.create_table(
        'page_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('cover_image', sa.String(length=500), nullable=True),
        sa.Column('content_snapshot', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )

    # Create indexes
    op.create_index('ix_page_versions_page_id', 'page_versions', ['page_id'])
    op.create_index('ix_page_versions_version_number', 'page_versions', ['version_number'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_page_versions_version_number', table_name='page_versions')
    op.drop_index('ix_page_versions_page_id', table_name='page_versions')

    # Drop table
    op.drop_table('page_versions')
