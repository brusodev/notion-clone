"""add page permissions table

Revision ID: daed445bc4cd
Revises: 45769afa3084
Create Date: 2025-12-12 15:54:35.344949

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'daed445bc4cd'
down_revision = '45769afa3084'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create page_permissions table
    op.create_table('page_permissions',
    sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('permission_level', sa.Enum('VIEW', 'COMMENT', 'EDIT', name='permissionlevel'), nullable=False),
    sa.Column('granted_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('page_id', 'user_id', name='uq_page_user_permission')
    )

    # Create indexes
    op.create_index('ix_page_permissions_page_id', 'page_permissions', ['page_id'])
    op.create_index('ix_page_permissions_user_id', 'page_permissions', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_page_permissions_user_id', table_name='page_permissions')
    op.drop_index('ix_page_permissions_page_id', table_name='page_permissions')

    # Drop table
    op.drop_table('page_permissions')

    # Drop enum
    permission_level_enum = postgresql.ENUM('VIEW', 'COMMENT', 'EDIT', name='permissionlevel')
    permission_level_enum.drop(op.get_bind(), checkfirst=True)
