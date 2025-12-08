"""add_comments_performance_indexes

Revision ID: 8d29e3bec67a
Revises: e89164725865
Create Date: 2025-12-08 11:41:28.428115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d29e3bec67a'
down_revision = 'e89164725865'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Composite indexes for efficient listing with ordering
    # These improve queries like: SELECT * FROM comments WHERE page_id = X ORDER BY created_at DESC
    op.create_index(
        'ix_comments_page_created',
        'comments',
        ['page_id', 'created_at'],
        unique=False
    )

    op.create_index(
        'ix_comments_block_created',
        'comments',
        ['block_id', 'created_at'],
        unique=False
    )

    # Composite index for efficient reaction aggregation
    # Improves queries like: SELECT reaction_type, COUNT(*) FROM comment_reactions WHERE comment_id = X GROUP BY reaction_type
    op.create_index(
        'ix_comment_reactions_comment_type',
        'comment_reactions',
        ['comment_id', 'reaction_type'],
        unique=False
    )

    # Composite index for efficient attachment ordering
    # Improves queries like: SELECT * FROM comment_attachments WHERE comment_id = X ORDER BY order_index
    op.create_index(
        'ix_comment_attachments_comment_order',
        'comment_attachments',
        ['comment_id', 'order_index'],
        unique=False
    )

    # Partial index for non-deleted comments (most common filter)
    # SQLite doesn't support partial indexes, so we skip it there
    op.create_index(
        'ix_comments_not_deleted',
        'comments',
        ['page_id', 'created_at'],
        unique=False,
        postgresql_where=sa.text('is_deleted = false')
    )


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('ix_comments_not_deleted', table_name='comments')
    op.drop_index('ix_comment_attachments_comment_order', table_name='comment_attachments')
    op.drop_index('ix_comment_reactions_comment_type', table_name='comment_reactions')
    op.drop_index('ix_comments_block_created', table_name='comments')
    op.drop_index('ix_comments_page_created', table_name='comments')
