"""add fulltext search

Revision ID: d127b877fd3a
Revises: 17bdb28430d1
Create Date: 2025-12-04 16:47:42.979195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd127b877fd3a'
down_revision = '17bdb28430d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add full-text search columns and indexes for PostgreSQL"""
    # Check if PostgreSQL (skip for SQLite)
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':

        # 1. Add tsvector column to pages table
        #    - Generated from title field
        #    - Weight 'A' for highest ranking (titles are more important)
        #    - Portuguese text search configuration
        op.execute("""
            ALTER TABLE pages
            ADD COLUMN title_search tsvector
            GENERATED ALWAYS AS (
                setweight(to_tsvector('portuguese', coalesce(title, '')), 'A')
            ) STORED;
        """)

        # 2. Add tsvector column to blocks table
        #    - Generated from content JSON field (extracts 'text' property)
        #    - Weight 'B' for secondary ranking (content is less important than titles)
        #    - Portuguese text search configuration
        op.execute("""
            ALTER TABLE blocks
            ADD COLUMN content_search tsvector
            GENERATED ALWAYS AS (
                setweight(to_tsvector('portuguese', coalesce(content->>'text', '')), 'B')
            ) STORED;
        """)

        # 3. Create GIN indexes for fast full-text search
        #    GIN (Generalized Inverted Index) is optimal for tsvector columns
        op.create_index(
            'ix_pages_title_search_gin',
            'pages',
            ['title_search'],
            postgresql_using='gin'
        )

        op.create_index(
            'ix_blocks_content_search_gin',
            'blocks',
            ['content_search'],
            postgresql_using='gin'
        )

        # 4. Optional: Composite index for common query patterns
        #    Speeds up searches filtered by workspace + non-archived
        op.create_index(
            'ix_pages_workspace_archived',
            'pages',
            ['workspace_id', 'is_archived'],
            postgresql_where=sa.text("is_archived = false")
        )


def downgrade() -> None:
    """Remove full-text search columns and indexes"""
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # Drop indexes
        op.drop_index('ix_pages_workspace_archived', 'pages')
        op.drop_index('ix_blocks_content_search_gin', 'blocks')
        op.drop_index('ix_pages_title_search_gin', 'pages')

        # Drop columns
        op.execute("ALTER TABLE blocks DROP COLUMN content_search")
        op.execute("ALTER TABLE pages DROP COLUMN title_search")
