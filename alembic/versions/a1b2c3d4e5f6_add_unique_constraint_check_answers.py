"""add unique constraint check_answers

Revision ID: a1b2c3d4e5f6
Revises: 0e848fcd9111
Create Date: 2026-05-17 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0e848fcd9111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Barcha shift_check_id+item_id juftliklari uchun faqat bitta answer bo'ladi
    op.create_unique_constraint(
        'uq_shift_check_item',
        'check_answers',
        ['shift_check_id', 'item_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_shift_check_item', 'check_answers', type_='unique')
