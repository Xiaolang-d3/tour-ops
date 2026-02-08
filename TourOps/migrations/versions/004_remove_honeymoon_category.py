"""remove honeymoon category from template enum

Revision ID: 004
Revises: 003
Create Date: 2026-02-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove 'honeymoon' from ENUM values
    op.execute(
        "ALTER TABLE templates MODIFY COLUMN category "
        "ENUM('family','business','team_building','adventure') NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE templates MODIFY COLUMN category "
        "ENUM('family','honeymoon','business','team_building','adventure') NULL"
    )

