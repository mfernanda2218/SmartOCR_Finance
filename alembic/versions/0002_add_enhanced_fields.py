"""Add enhanced fields to extraction_records

Revision ID: 0002_add_enhanced_fields
Revises: 0001_initial
Create Date: 2026-09-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision: str = "0002_add_enhanced_fields"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adicionar novos campos
    op.add_column('extraction_records', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('extraction_records', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('extraction_records', sa.Column('document_type', sa.Enum('boleto', 'conta_energia', 'conta_agua', 'darf', 'outro', 'desconhecido', name='documenttype'), nullable=True))
    op.add_column('extraction_records', sa.Column('processing_status', sa.Enum('success', 'partial', 'failed', 'pending', name='processingstatus'), nullable=True))
    op.add_column('extraction_records', sa.Column('processing_time_ms', sa.Integer(), nullable=True))
    op.add_column('extraction_records', sa.Column('confidence_score', sa.Float(), nullable=True))
    op.add_column('extraction_records', sa.Column('additional_data', sa.Text(), nullable=True))
    op.add_column('extraction_records', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('extraction_records', sa.Column('warnings', sa.Text(), nullable=True))
    op.add_column('extraction_records', sa.Column('is_validated', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('extraction_records', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remover os campos adicionados
    op.drop_column('extraction_records', 'is_archived')
    op.drop_column('extraction_records', 'is_validated')
    op.drop_column('extraction_records', 'warnings')
    op.drop_column('extraction_records', 'error_message')
    op.drop_column('extraction_records', 'additional_data')
    op.drop_column('extraction_records', 'confidence_score')
    op.drop_column('extraction_records', 'processing_time_ms')
    op.drop_column('extraction_records', 'processing_status')
    op.drop_column('extraction_records', 'document_type')
    op.drop_column('extraction_records', 'updated_at')
    op.drop_column('extraction_records', 'file_size')