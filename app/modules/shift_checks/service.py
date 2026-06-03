"""
SHIFT CHECK SERVICE
"""

from datetime import datetime

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.modules.shift_checks.models import ShiftCheck, CheckAnswer, AnswerPhoto
from app.modules.shift_checks.schemas import AnswerPhotoInput, SaveAnswersRequest
from app.modules.users.models import User
from app.modules.checklist.models import ChecklistItem

async def start_shift_check(
    db: AsyncSession,
    current_user: User,
    shift_type: str = "day",
) -> ShiftCheck:
    """
    Director uchun yangi shift check yaratadi.

    Muhim:
    branch_id requestdan olinmaydi.
    branch_id current_user.branch_id dan olinadi.
    """

    if not current_user.branch_id:
        raise ValueError("User has no branch assigned")

    shift_check = ShiftCheck(
        user_id=current_user.id,
        branch_id=current_user.branch_id,
        shift_type=shift_type,
        status="draft",
    )

    db.add(shift_check)
    await db.commit()
    await db.refresh(shift_check)

    return shift_check


async def get_shift_check_for_user(
    db: AsyncSession,
    shift_check_id: int,
    current_user: User,
) -> ShiftCheck | None:
    """
    ShiftCheck ni user huquqi bo‘yicha topadi.

    Admin hammasini ko‘radi.
    Director faqat o‘z filialidagi checklistni ko‘radi.
    """

    query = select(ShiftCheck).where(ShiftCheck.id == shift_check_id)

    if current_user.role == "director":
        query = query.where(ShiftCheck.branch_id == current_user.branch_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def save_shift_check_answers(
    db: AsyncSession,
    shift_check: ShiftCheck,
    payload: SaveAnswersRequest,
) -> ShiftCheck:
    """
    Javoblarni draft sifatida saqlaydi.
    """

    if shift_check.status != "draft":
        raise ValueError("Only draft shift checks can be edited")

    allowed_statuses = {"not_checked", "yes", "no", "na"}

    existing_answers_result = await db.execute(
        select(CheckAnswer).where(CheckAnswer.shift_check_id == shift_check.id)
    )
    existing_answers = {
        answer.item_id: answer
        for answer in existing_answers_result.scalars().all()
    }

    seen_item_ids = set()
    for answer_data in payload.answers:
        if answer_data.status not in allowed_statuses:
            raise ValueError(
                "Invalid answer status. Allowed: not_checked, yes, no, na"
            )

        if answer_data.item_id in seen_item_ids:
            raise ValueError("Duplicate answer for the same checklist item")
        seen_item_ids.add(answer_data.item_id)

        answer = existing_answers.get(answer_data.item_id)
        if answer is None:
            answer = CheckAnswer(
                shift_check_id=shift_check.id,
                item_id=answer_data.item_id,
                status=answer_data.status,
                comment=answer_data.comment,
            )
            db.add(answer)
            await db.flush()
        else:
            await db.execute(
                delete(AnswerPhoto).where(AnswerPhoto.answer_id == answer.id)
            )
            answer.status = answer_data.status
            answer.comment = answer_data.comment
            await db.flush()

        photos_data = list(answer_data.photos or [])
        if answer_data.photo_url and not any(
            photo.file_url == answer_data.photo_url for photo in photos_data
        ):
            photos_data.append(
                AnswerPhotoInput(
                    file_url=answer_data.photo_url,
                )
            )

        for photo_data in photos_data:
            # 🚀 ASOSIY TUZATISH: Agar file_url bo'sh bo'lsa yoki brauzer 'blob:' havolasi bo'lsa, uni bazaga YOZMAYMIZ
            if not photo_data.file_url or str(photo_data.file_url).startswith("blob:"):
                continue  # Keyingi rasmga o'tib ketadi, buni tashlab yuboradi

            photo = AnswerPhoto(
                answer_id=answer.id,
                file_url=photo_data.file_url,
                thumbnail_url=photo_data.thumbnail_url,
                file_size=photo_data.file_size,
                mime_type=photo_data.mime_type,
            )
            db.add(photo)

    await db.commit()
    await db.refresh(shift_check)

    return shift_check

async def submit_shift_check(
    db: AsyncSession,
    shift_check: ShiftCheck,
) -> ShiftCheck:

    # ✅ HTTPException emas ValueError ishlatamiz — router uni to'g'ri ushlaydi
    if shift_check.status != "draft":
        raise ValueError("Shift check already submitted")

    # ✅ ChecklistItem ni branch bo'yicha filter qilamiz
    # Agar ChecklistItem da branch_id yo'q bo'lsa — join orqali yoki
    # CheckAnswer.item_id DISTINCT hisoblaymiz
    total_items_result = await db.execute(
        select(func.count(ChecklistItem.id)).where(
            ChecklistItem.is_active == True
        )
    )
    total_items = total_items_result.scalar() or 0

    # ✅ Faqat shu shift_check ga tegishli UNIQUE item javoblarini hisoblaymiz
    answered_result = await db.execute(
        select(func.count(CheckAnswer.item_id.distinct())).where(
            CheckAnswer.shift_check_id == shift_check.id
        )
    )
    answered_count = answered_result.scalar() or 0

    if answered_count < total_items:
        raise ValueError(
            f"Checklist incomplete: {answered_count}/{total_items} answered"
        )

    shift_check.status = "submitted"
    shift_check.submitted_at = datetime.utcnow()

    await db.commit()
    await db.refresh(shift_check)

    return shift_check
 

async def get_shift_checks_service(
    db: AsyncSession,
    current_user: User,
):
    query = select(ShiftCheck).order_by(ShiftCheck.id.desc())

    if current_user.role != "admin":
        query = query.where(
            ShiftCheck.branch_id == current_user.branch_id
        )

    result = await db.execute(query)

    return result.scalars().all()


async def get_shift_check_detail(db, current_user, shift_check_id: int):
    query = (
        select(ShiftCheck)
        .where(ShiftCheck.id == shift_check_id)
        .options(
            selectinload(ShiftCheck.answers)
            .selectinload(CheckAnswer.photos),
            selectinload(ShiftCheck.branch),
        )
    )

    result = await db.execute(query)
    shift_check = result.scalar_one_or_none()

    if not shift_check:
        return None

    if current_user.role != "admin":
        if shift_check.branch_id != current_user.branch_id:
            raise ValueError("Access denied")

    return shift_check
