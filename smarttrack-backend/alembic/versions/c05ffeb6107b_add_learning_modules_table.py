"""add_learning_modules_table

Revision ID: c05ffeb6107b
Revises: add_user_assessments
Create Date: 2026-05-01 15:34:23.511108
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c05ffeb6107b'
down_revision: Union[str, None] = 'add_user_assessments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Create academic_records (new table) ---
    op.create_table('academic_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=False),
        sa.Column('grade', sa.String(length=10), nullable=False),
        sa.Column('exam_type', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_academic_records_id'), 'academic_records', ['id'], unique=False)
    op.create_index(op.f('ix_academic_records_user_id'), 'academic_records', ['user_id'], unique=False)

    # --- Drop legacy tables ---
    op.drop_index('ix_user_assessments_id', table_name='user_assessments', if_exists=True)
    op.drop_index('ix_user_assessments_user_id', table_name='user_assessments', if_exists=True)
    op.execute('DROP TABLE IF EXISTS user_assessments CASCADE')
    op.drop_index('ix_questions_category', table_name='questions', if_exists=True)
    op.drop_index('ix_questions_id', table_name='questions', if_exists=True)
    op.execute('DROP TABLE IF EXISTS questions CASCADE')

    # --- Add columns to users ---
    op.add_column('users', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('school', sa.String(length=255), nullable=True))

    # --- Recreate questions with new domain-based schema ---
    op.create_table('questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('options', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('correct_answer', sa.String(length=1), nullable=False),
        sa.Column('difficulty_a', sa.Float(), nullable=False),
        sa.Column('difficulty_b', sa.Float(), nullable=False),
        sa.Column('difficulty_c', sa.Float(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_index(op.f('ix_questions_domain'), 'questions', ['domain'], unique=False)

    # --- Create user_skill_estimates ---
    op.create_table('user_skill_estimates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('theta', sa.Float(), nullable=False),
        sa.Column('standard_error', sa.Float(), nullable=False),
        sa.Column('last_updated', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_skill_estimates_id'), 'user_skill_estimates', ['id'], unique=False)
    op.create_index(op.f('ix_user_skill_estimates_user_id'), 'user_skill_estimates', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_skill_estimates_domain'), 'user_skill_estimates', ['domain'], unique=False)

    # --- Create responses ---
    op.create_table('responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('correct', sa.Boolean(), nullable=False),
        sa.Column('time_taken_seconds', sa.Float(), nullable=False),
        sa.Column('hints_used', sa.Integer(), nullable=False),
        sa.Column('timestamp', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_responses_id'), 'responses', ['id'], unique=False)
    op.create_index(op.f('ix_responses_user_id'), 'responses', ['user_id'], unique=False)
    op.create_index(op.f('ix_responses_question_id'), 'responses', ['question_id'], unique=False)

    # --- Create behavioral_profiles ---
    op.create_table('behavioral_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('trait', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('last_updated', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_behavioral_profiles_id'), 'behavioral_profiles', ['id'], unique=False)

    # --- Create leaderboards ---
    op.create_table('leaderboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('last_updated', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leaderboards_id'), 'leaderboards', ['id'], unique=False)
    op.create_index(op.f('ix_leaderboards_domain'), 'leaderboards', ['domain'], unique=False)
    op.create_index(op.f('ix_leaderboards_category'), 'leaderboards', ['category'], unique=False)
    op.create_index(op.f('ix_leaderboards_user_id'), 'leaderboards', ['user_id'], unique=False)

    # --- Create learning_modules ---
    op.create_table('learning_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('difficulty_level', sa.Float(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_modules_id'), 'learning_modules', ['id'], unique=False)
    op.create_index(op.f('ix_learning_modules_domain'), 'learning_modules', ['domain'], unique=False)



def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'school')
    op.drop_column('users', 'category')
    op.create_table('questions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('category', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('question', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('options', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('correct_answer', sa.VARCHAR(length=1), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='questions_pkey')
    )
    op.create_index('ix_questions_id', 'questions', ['id'], unique=False)
    op.create_index('ix_questions_category', 'questions', ['category'], unique=False)
    op.create_table('user_assessments',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('academic_completed', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('psychometric_completed', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('academic_answers', postgresql.JSON(astext_type=sa.Text()), server_default=sa.text("'{}'::json"), autoincrement=False, nullable=False),
    sa.Column('psychometric_answers', postgresql.JSON(astext_type=sa.Text()), server_default=sa.text("'{}'::json"), autoincrement=False, nullable=False),
    sa.Column('academic_score', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recommendations', postgresql.JSON(astext_type=sa.Text()), server_default=sa.text("'{}'::json"), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('completed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_assessments_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='user_assessments_pkey')
    )
    op.create_index('ix_user_assessments_user_id', 'user_assessments', ['user_id'], unique=False)
    op.create_index('ix_user_assessments_id', 'user_assessments', ['id'], unique=False)
    op.drop_index(op.f('ix_academic_records_user_id'), table_name='academic_records')
    op.drop_index(op.f('ix_academic_records_id'), table_name='academic_records')
    op.drop_table('academic_records')
    # ### end Alembic commands ###
