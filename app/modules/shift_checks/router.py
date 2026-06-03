"""
SHIFT CHECK ROUTER
"""

from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, case
from datetime import datetime
import app.models, calendar

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.shift_checks.models import ShiftCheck
from app.modules.shift_checks.models import ShiftCheck, CheckAnswer
from app.modules.users.models import User
from app.modules.shift_checks.schemas import (
    ShiftCheckListOut,
    ShiftCheckStartRequest,
    ShiftCheckStartResponse,
    SaveAnswersRequest,
    ShiftCheckSubmitResponse,
)
from app.modules.shift_checks.service import (
    get_shift_check_detail,
    get_shift_checks_service,
    start_shift_check,
    get_shift_check_for_user,
    save_shift_check_answers,
    submit_shift_check,
)



router = APIRouter()


@router.post(
    "/start",
    response_model=ShiftCheckStartResponse,
    summary="Начать проверку смены",
)
async def start_check(
    payload: ShiftCheckStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Director checklist boshlaydi.

    Endi requestda user_id va branch_id yo‘q.
    Backend ularni token orqali current_user dan oladi.
    """

    try:
        shift_check = await start_shift_check(
            db=db,
            current_user=current_user,
            shift_type=payload.shift_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return shift_check


@router.post(
    "/{shift_check_id}/answers",
    summary="Сохранить ответы чек-листа",
)
async def save_answers(
    shift_check_id: int,
    payload: SaveAnswersRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Director faqat o‘z filialidagi checklist javoblarini saqlay oladi.
    """

    shift_check = await get_shift_check_for_user(
        db=db,
        shift_check_id=shift_check_id,
        current_user=current_user,
    )

    if not shift_check:
        raise HTTPException(status_code=404, detail="Shift check not found")

    try:
        await save_shift_check_answers(
            db=db,
            shift_check=shift_check,
            payload=payload,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "status": "ok",
        "message": "Answers saved successfully",
    }

@router.post(
    "/{shift_check_id}/submit",
    summary="Отправить чек-лист",
)
async def submit_check(
    shift_check_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Director faqat o‘z filialidagi checklistni submit qila oladi.
    Foydalanuvchi profil keshini buzmaslik uchun xavfsiz holatga keltirildi.
    """

    shift_check = await get_shift_check_for_user(
        db=db,
        shift_check_id=shift_check_id,
        current_user=current_user,
    )

    if not shift_check:
        raise HTTPException(status_code=404, detail="Shift check not found")

    try:
        # Servis orqali faqat status 'submitted' qilinadi
        await submit_shift_check(db, shift_check)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    # ⚠️ MUHIM YAKUN: Hech qanday chalkash model yoki user ob'ektini qaytarmaymiz!
    # Faqatgina muvaffaqiyatli bajarilganini tasdiqlovchi xabar ketadi.
    return {
        "status": "success",
        "message": "Чек-лист успешно отправлен",
        "shift_check_id": shift_check_id
    }



@router.get("/health")
async def shift_checks_health():
    return {"module": "shift_checks", "status": "ok"}




@router.get("/dashboard-stats", summary="Быстрая статистика филиалов по дням месяца")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.modules.branches.models import Branch  

    # 1. Joriy vaqtni aniqlaymiz (Masalan: 2026-06-02)
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # 2. Dinamik tarzda shu oyda nechta kun borligini topamiz (Iyun uchun jami 30 kun)
    # calendar.monthrange() funksiyasi oydagi kunlar sonini qaytaradi (masalan, 30)
    _, total_days_in_month = calendar.monthrange(current_year, current_month)

    # 3. Bazadan faqat MW bilan boshlanadigan BARCHA filiallarni olamiz
    result = await db.execute(
        select(Branch)
        .options(selectinload(Branch.shift_checks))
        .where(Branch.name.like("MW%"))
        .order_by(Branch.name.asc())
    )
    branches = result.scalars().all()

    output = []
    for branch in branches:
        all_checks = branch.shift_checks or []
        
        # Faqat shu joriy oyga tegishli cheklistlarni filtrlaymiz
        monthly_checks = [
            c for c in all_checks 
            if c.started_at and c.started_at.year == current_year and c.started_at.month == current_month
        ]
        
        total = len(monthly_checks)
        submitted = len([c for c in monthly_checks if c.status in ["submitted", "completed", "finished"]])
        draft = len([c for c in monthly_checks if c.status == "draft"])
        
        # 4. SIZ SO'RAGAN MATEMATIK LOGIKA:
        # Oylik umumiy foiz = (Yuborilganlar soni / Oydagi jami kunlar soni) * 100
        # Masalan: (1 ta yuborilgan / 30 kun) * 100 = 3.33% -> round() orqali 3% yoki float qilsa bo'ladi
        if total_days_in_month > 0:
            # round(..., 1) qilsangiz 3.3% chiqadi, round(..., 0) yoki oddiy round() butun son qiladi (3%)
            completion = round((submitted / total_days_in_month) * 100)
        else:
            completion = 0
            
        # Foiz 100% dan oshib ketmasligi uchun cheklov
        if completion > 100:
            completion = 100

        output.append({
            "id": branch.id,
            "name": branch.name,
            "total": total,          # Shu oyda ochilgan jami cheklistlar soni
            "submitted": submitted,  # 1 ta
            "draft": draft,          # 0 ta
            "completion": completion # Natija: 3% (Agarda butun son kerak bo'lsa)
        })
        
    return output




    

@router.get("/branches/{branch_id}/shift-checks")
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
            selectinload(ShiftCheck.branch),
        )
        .where(ShiftCheck.branch_id == branch_id)
        .order_by(ShiftCheck.id.desc())
    )
    checks = result.scalars().all()
    print(f"✅ checks soni: {len(checks)}")
    print(f"✅ birinchi check answers: {checks[0].answers if checks else 'YOQ'}")

    return [
        {
            "id": check.id,
            "status": check.status,
            "shift_type": check.shift_type,
            "comment": check.comment,
            "started_at": check.started_at,
            "submitted_at": check.submitted_at,
            "answers": [
                {
                    "id": answer.id,
                    "item_id": answer.item_id,
                    # ChecklistItem dan savol nomini olamiz
                    "item_title_ru": answer.item.title_ru if answer.item else None,
                    "status": answer.status,
                    "comment": answer.comment,
                    "photos": [
                        {
                            "file_url": photo.file_url,
                            "thumbnail_url": photo.thumbnail_url,
                            "file_size": photo.file_size,
                            "mime_type": photo.mime_type,
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

@router.get("", response_model=list[ShiftCheckListOut])
async def get_shift_checks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_shift_checks_service(db, current_user) 




@router.get("/{shift_check_id}")
async def get_shift_check_detail_endpoint(
    shift_check_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await get_shift_check_detail(db, current_user, shift_check_id)

    if not data:
        raise HTTPException(status_code=404, detail="Shift check not found")

    return data


