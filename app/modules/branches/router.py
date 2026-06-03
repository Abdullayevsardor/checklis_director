from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.branches.models import Branch
from app.modules.branches.schemas import BranchOut
from app.modules.shift_checks.models import ShiftCheck, CheckAnswer
from app.modules.users.models import User

router = APIRouter()


@router.get("", response_model=list[BranchOut])
async def get_branches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Branch)
        .where(
            (Branch.is_active == True) &
            (Branch.name.like("MW%"))
        )
        .order_by(Branch.name)
    )
    return result.scalars().all()


# ✅ Statik routelar har doim dinamikdan OLDIN bo'lishi kerak
@router.get("/health")
async def branches_health():
    return {"module": "branches", "status": "ok"}


# ✅ Dinamik route eng oxirida
@router.get("/{branch_id}/shift-checks")
async def get_branch_shift_checks(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ShiftCheck)
        .options(
            selectinload(ShiftCheck.answers).selectinload(CheckAnswer.item),
            selectinload(ShiftCheck.answers).selectinload(CheckAnswer.photos),
        )
        .where(ShiftCheck.branch_id == branch_id)
        .order_by(ShiftCheck.id.desc())
    )
    checks = result.scalars().all()

    return [
        {
            "id": check.id,
            "status": check.status,
            "shift_type": check.shift_type,
            "started_at": check.started_at,
            "submitted_at": check.submitted_at,
            "answers": [
                {
                    "id": answer.id,
                    "item_id": answer.item_id,
                    "item_title_ru": answer.item.title_ru if answer.item else None,
                    "status": answer.status,
                    "comment": answer.comment,
                    "photos": [
                        {
                            "file_url": photo.file_url,
                            "thumbnail_url": photo.thumbnail_url,
                        }
                        for photo in answer.photos
                        if photo.is_active
                    ],
                }
                for answer in check.answers
            ],
        }
        for check in checks
    ]

