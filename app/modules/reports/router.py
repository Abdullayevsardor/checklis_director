from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models import User

from app.modules.reports.schemas import ShiftCheckReportOut
from app.modules.reports.service import get_shift_checks_report_service


router = APIRouter()


@router.get("/shift-checks", response_model=list[ShiftCheckReportOut])
async def get_shift_checks_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    branch_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_shift_checks_report_service(
        db=db,
        current_user=current_user,
        date_from=date_from,
        date_to=date_to,
        branch_id=branch_id,
    )