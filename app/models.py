"""
ALL MODELS IMPORT

Bu fayl barcha SQLAlchemy modellarni bir joyga yig‘adi.

Nima uchun kerak?
Alembic migration qilganda barcha modellarni ko‘rishi kerak.

Muhim:
Bu importlarni app/core/database.py ichiga yozmang.
Aks holda circular import chiqadi.
"""

from app.modules.branches.models import Branch  # noqa
from app.modules.users.models import User, UserPasskey  # noqa
from app.modules.workly.models import WorklyEmployee  # noqa
from app.modules.checklist.models import ChecklistSection, ChecklistItem  # noqa
from app.modules.shift_checks.models import ShiftCheck, CheckAnswer, AnswerPhoto  # noqa