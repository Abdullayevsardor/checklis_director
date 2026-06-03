"""add_user_passkey_sign_count

Revision ID: 3c4d5e6f7a8b
Revises: 2aedf2a75c45
Create Date: 2026-05-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c4d5e6f7a8b'
down_revision: Union[str, Sequence[str], None] = '17827dc086ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_passkeys', sa.Column('sign_count', sa.Integer(), nullable=False, server_default='0'))
    op.alter_column('user_passkeys', 'sign_count', server_default=None)


def downgrade() -> None:
    op.drop_column('user_passkeys', 'sign_count')
