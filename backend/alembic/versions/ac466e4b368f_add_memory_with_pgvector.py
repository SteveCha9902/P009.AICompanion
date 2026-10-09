"""Add Memory with pgvector

Revision ID: ac466e4b368f
Revises: cade15971ddd
Create Date: 2026-08-27 22:56:18.864569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac466e4b368f'
down_revision: Union[str, Sequence[str], None] = 'cade15971ddd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import pgvector
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create memory enums if they don't exist (assuming string enums here to simplify)
    # But usually we just use VARCHAR for enums to avoid complex migration
    
    op.create_table('memories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('companion_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('entity', sa.String(), nullable=True),
        sa.Column('polarity', sa.String(), nullable=True),
        sa.Column('importance', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('source_message_id', sa.String(), nullable=True),
        sa.Column('source_conversation_id', sa.String(), nullable=True),
        sa.Column('embedding', Vector(dim=1536), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['companion_id'], ['companions.id'], ),
        sa.ForeignKeyConstraint(['source_conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['source_message_id'], ['messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memories_companion_id'), 'memories', ['companion_id'], unique=False)
    
    # Optional: create hnsw index for pgvector
    # op.execute('CREATE INDEX ix_memories_embedding ON memories USING hnsw (embedding vector_cosine_ops)')

def downgrade() -> None:
    op.drop_index(op.f('ix_memories_companion_id'), table_name='memories')
    op.drop_table('memories')
    op.execute('DROP EXTENSION IF EXISTS vector')
