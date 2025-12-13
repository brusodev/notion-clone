"""add comments system

Revision ID: e89164725865
Revises: d127b877fd3a
Create Date: 2025-12-05 15:04:56.995257

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.core.types import GUID

# revision identifiers, used by Alembic.
revision = 'e89164725865'
down_revision = 'd127b877fd3a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add comments system with 4 tables"""
    # Create comments table with polymorphic linking and threading
    op.create_table('comments',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('page_id', GUID(), nullable=True),
    sa.Column('block_id', GUID(), nullable=True),
    sa.Column('parent_comment_id', GUID(), nullable=True),
    sa.Column('thread_depth', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('author_id', GUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_by', GUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('(page_id IS NOT NULL AND block_id IS NULL) OR (page_id IS NULL AND block_id IS NOT NULL)', name='check_comment_target'),
    sa.CheckConstraint('thread_depth >= 0 AND thread_depth <= 5', name='check_thread_depth'),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['block_id'], ['blocks.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_comment_id'], ['comments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comments_author_id'), ['author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_comments_block_id'), ['block_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_comments_is_deleted'), ['is_deleted'], unique=False)
        batch_op.create_index(batch_op.f('ix_comments_page_id'), ['page_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_comments_parent_comment_id'), ['parent_comment_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_comments_thread_depth'), ['thread_depth'], unique=False)

    # Create comment_attachments table
    op.create_table('comment_attachments',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('comment_id', GUID(), nullable=False),
    sa.Column('file_name', sa.String(length=500), nullable=False),
    sa.Column('file_url', sa.String(length=1000), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('mime_type', sa.String(length=100), nullable=True),
    sa.Column('uploaded_by', GUID(), nullable=False),
    sa.Column('order_index', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('comment_attachments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comment_attachments_comment_id'), ['comment_id'], unique=False)

    # Create comment_mentions table
    op.create_table('comment_mentions',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('comment_id', GUID(), nullable=False),
    sa.Column('mentioned_user_id', GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mentioned_user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('comment_id', 'mentioned_user_id', name='uq_comment_mention')
    )
    with op.batch_alter_table('comment_mentions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comment_mentions_comment_id'), ['comment_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_comment_mentions_mentioned_user_id'), ['mentioned_user_id'], unique=False)

    # Create comment_reactions table
    op.create_table('comment_reactions',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('comment_id', GUID(), nullable=False),
    sa.Column('user_id', GUID(), nullable=False),
    sa.Column('reaction_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('comment_id', 'user_id', 'reaction_type', name='uq_comment_user_reaction')
    )
    with op.batch_alter_table('comment_reactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comment_reactions_comment_id'), ['comment_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_comment_reactions_user_id'), ['user_id'], unique=False)


def downgrade() -> None:
    """Remove comments system tables"""
    # Drop comment_reactions table
    with op.batch_alter_table('comment_reactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comment_reactions_user_id'))
        batch_op.drop_index(batch_op.f('ix_comment_reactions_comment_id'))
    op.drop_table('comment_reactions')

    # Drop comment_mentions table
    with op.batch_alter_table('comment_mentions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comment_mentions_mentioned_user_id'))
        batch_op.drop_index(batch_op.f('ix_comment_mentions_comment_id'))
    op.drop_table('comment_mentions')

    # Drop comment_attachments table
    with op.batch_alter_table('comment_attachments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comment_attachments_comment_id'))
    op.drop_table('comment_attachments')

    # Drop comments table
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comments_thread_depth'))
        batch_op.drop_index(batch_op.f('ix_comments_parent_comment_id'))
        batch_op.drop_index(batch_op.f('ix_comments_page_id'))
        batch_op.drop_index(batch_op.f('ix_comments_is_deleted'))
        batch_op.drop_index(batch_op.f('ix_comments_block_id'))
        batch_op.drop_index(batch_op.f('ix_comments_author_id'))
    op.drop_table('comments')
