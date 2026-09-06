"""Cria a tabela extraction_records

Revision ID: 0001_initial
Revises: 
Create Date: 2026-08-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extraction_records",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
        ),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("cpfs", sa.Text(), nullable=True),
        sa.Column("cnpjs", sa.Text(), nullable=True),
        sa.Column("dates", sa.Text(), nullable=True),
        sa.Column("values", sa.Text(), nullable=True),
        sa.Column("boleto_lines", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("extraction_records")
