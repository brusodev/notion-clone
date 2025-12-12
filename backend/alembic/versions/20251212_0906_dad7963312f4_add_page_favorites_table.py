"""add_page_favorites_table

Revision ID: dad7963312f4
Revises: 9765bd696560
Create Date: 2025-12-12 09:06:15.764819

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dad7963312f4'
down_revision = '9765bd696560'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create page_favorites table
    op.create_table(
        'page_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'page_id', name='uq_user_page_favorite')
    )

    # Create indexes
    op.create_index('ix_page_favorites_user_id', 'page_favorites', ['user_id'])
    op.create_index('ix_page_favorites_page_id', 'page_favorites', ['page_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_page_favorites_page_id', table_name='page_favorites')
    op.drop_index('ix_page_favorites_user_id', table_name='page_favorites')

    # Drop table
    op.drop_table('page_favorites')
