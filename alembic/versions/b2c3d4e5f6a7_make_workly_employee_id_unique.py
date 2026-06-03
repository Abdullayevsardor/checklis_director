"""make workly_employee_id unique

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-17 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Workly employee ID uchun unique constraint
    op.create_unique_constraint(
        'uq_users_workly_employee_id',
        'users',
        ['workly_employee_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_workly_employee_id', 'users', type_='unique')
