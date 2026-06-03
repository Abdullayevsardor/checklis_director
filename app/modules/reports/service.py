from datetime import date, time, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.shift_checks.models import ShiftCheck


async def get_shift_checks_report_service(
    db: AsyncSession,
    current_user: User,
    date_from: date | None = None,
    date_to: date | None = None,
    branch_id: int | None = None,
):
    query = select(ShiftCheck).order_by(ShiftCheck.id.desc())

    # director faqat o‘z filialini ko‘radi
    if current_user.role == "director":
        query = query.where(ShiftCheck.branch_id == current_user.branch_id)

    # admin/supervisor branch bo‘yicha filter qila oladi
    elif branch_id:
        query = query.where(ShiftCheck.branch_id == branch_id)

    if date_from:
        start_dt = datetime.combine(date_from, time.min)
        query = query.where(ShiftCheck.started_at >= start_dt)

    if date_to:
        end_dt = datetime.combine(date_to, time.max)
        query = query.where(ShiftCheck.started_at <= end_dt)

    result = await db.execute(query)
    return result.scalars().all()