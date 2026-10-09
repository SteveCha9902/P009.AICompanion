"""Add Companion and Persona

Revision ID: cade15971ddd
Revises: 12129cece0c8
Create Date: 2026-08-27 22:46:46.483084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cade15971ddd'
down_revision: Union[str, Sequence[str], None] = '12129cece0c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    op.create_table('companions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companions_user_id'), 'companions', ['user_id'], unique=True)

    op.create_table('personas',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('companion_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('personality', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('communication_style', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('behavior_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('boundaries', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['companion_id'], ['companions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personas_companion_id'), 'personas', ['companion_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_personas_companion_id'), table_name='personas')
    op.drop_table('personas')
    op.drop_index(op.f('ix_companions_user_id'), table_name='companions')
    op.drop_table('companions')
