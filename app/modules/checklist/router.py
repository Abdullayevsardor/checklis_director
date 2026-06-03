import app.models

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.checklist.schemas import ChecklistSectionResponse
from app.modules.checklist.service import get_checklist_template
import pandas as pd
import io

from app.core.database import get_db
from app.modules.checklist.service import (
    add_checklist_from_excel,
    update_checklist_from_excel,
    clear_checklist,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[ChecklistSectionResponse],
    summary="Получить шаблон чек-листа",
)
async def get_checklist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_checklist_template(db)


@router.get("/health")
async def checklist_health():
    return {"module": "checklist", "status": "ok"}






@router.post("/import/add")
async def import_add_checklist(
    file: UploadFile = File(...),
    replace: bool = False,
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel file allowed")

    result = await add_checklist_from_excel(db, file, replace=replace)
    return result


@router.delete("/clear")
async def clear_all_checklist(
    db: AsyncSession = Depends(get_db),
):
    """
    Barcha checklist sectionlarini va itemlarini o'chiradi.
    """
    result = await clear_checklist(db)
    return result


@router.put("/import/update")
async def import_update_checklist(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel file allowed")

    result = await update_checklist_from_excel(db, file)
    return result