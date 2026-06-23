"""add user assessments table

Revision ID: add_user_assessments
Revises: add_questions_table
Create Date: 2026-03-29 12:00:00.000000

This migration creates the user_assessments table to store:
- User assessment completion status (academic, psychometric)
- Assessment answers and scores
- Computed recommendations
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'add_user_assessments'
down_revision: Union[str, None] = 'add_questions_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_assessments table
    op.create_table(
        'user_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('academic_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('psychometric_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('academic_answers', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('psychometric_answers', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('academic_score', sa.Integer(), nullable=True),
        sa.Column('recommendations', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_user_assessments_id'), 'user_assessments', ['id'], unique=False)
    op.create_index(op.f('ix_user_assessments_user_id'), 'user_assessments', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_assessments_user_id'), table_name='user_assessments')
    op.drop_index(op.f('ix_user_assessments_id'), table_name='user_assessments')
    op.drop_table('user_assessments')
