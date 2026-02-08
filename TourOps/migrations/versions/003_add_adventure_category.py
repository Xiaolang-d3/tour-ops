"""add adventure category to template enum

Revision ID: 003
Revises: 002
Create Date: 2024-08-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # MySQL ALTER TABLE to expand ENUM values
    op.execute(
        "ALTER TABLE templates MODIFY COLUMN category "
        "ENUM('family','honeymoon','business','team_building','adventure') NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE templates MODIFY COLUMN category "
        "ENUM('family','honeymoon','business','team_building') NULL"
    )

