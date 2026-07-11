"""add reviews table

Revision ID: 006
Revises: 005
Create Date: 2026-02-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('trip_id', sa.Integer(), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('share_code', sa.String(32), index=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('tags', sa.JSON()),
        sa.Column('comment', sa.Text()),
        sa.Column('reviewer_name', sa.String(50)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('reviews')
