"""add questions table

Revision ID: add_questions_table
Revises: 5c95c5a86df5
Create Date: 2026-03-28 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'add_questions_table'
down_revision: Union[str, None] = '5c95c5a86df5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('options', postgresql.JSON(), nullable=False),
        sa.Column('correct_answer', sa.String(length=1), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_category'), 'questions', ['category'], unique=False)
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_category'), table_name='questions')
    op.drop_table('questions')
