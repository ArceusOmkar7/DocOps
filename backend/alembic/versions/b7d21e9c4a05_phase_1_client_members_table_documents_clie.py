"""phase 1: client_members table, documents.client_member_id, new document types

Revision ID: b7d21e9c4a05
Revises: e44ef8cbb30b
Create Date: 2026-08-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7d21e9c4a05'
down_revision: Union[str, Sequence[str], None] = 'e44ef8cbb30b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # New document type family values (native PG enum).
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'tds_form'")
    op.execute("ALTER TYPE document_type ADD VALUE IF NOT EXISTS 'investment_proof'")

    op.create_table('client_members',
    sa.Column('client_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('pan', sa.String(length=10), nullable=True),
    sa.Column('relation', sa.String(length=50), nullable=True,
              comment='e.g. self, spouse, son, father'),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_client_members_client_id'), 'client_members', ['client_id'], unique=False)
    op.create_index(op.f('ix_client_members_pan'), 'client_members', ['pan'], unique=False)

    # Link sub-documents to the individual taxpayer they belong to.
    op.add_column('documents',
        sa.Column('client_member_id', sa.UUID(), nullable=True,
                  comment='Individual family member this document belongs to (Phase 1.3 segregation)'),
    )
    op.create_foreign_key(
        'fk_documents_client_member_id', 'documents', 'client_members',
        ['client_member_id'], ['id'], ondelete='SET NULL',
    )
    op.create_index(op.f('ix_documents_client_member_id'), 'documents', ['client_member_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_documents_client_member_id'), table_name='documents')
    op.drop_constraint('fk_documents_client_member_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'client_member_id')
    op.drop_index(op.f('ix_client_members_pan'), table_name='client_members')
    op.drop_index(op.f('ix_client_members_client_id'), table_name='client_members')
    op.drop_table('client_members')
    # Native PG enums cannot drop values safely; tds_form / investment_proof stay.
