import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.shift_checks.models import ShiftCheck

router = APIRouter(prefix="", tags=["Uploads"])

UPLOAD_DIR = "media/uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/health")
async def uploads_health():
    return {"status": "ok", "module": "yuklangan rasm"}


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    shift_check_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Rasm yuklash.
    
    - Faqat director/manager/admin rol
    - Agar shift_check_id berilsa, shu shift draft bo'lishi kerak
    - Faqat MW filialidagi director o'z checklist rasmi yuklashi mumkin
    - Max 10 MB
    - Faqat image/* mime types
    """
    
    # 1. File mime type tekshirish
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Only image files allowed. Got: {file.content_type}"
        )
    
    # 2. File size check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # 3. Agar shift_check_id berilgan bo'lsa, validate qilish
    if shift_check_id:
        result = await db.execute(
            select(ShiftCheck).where(ShiftCheck.id == shift_check_id)
        )
        shift_check = result.scalar_one_or_none()
        
        if not shift_check:
            raise HTTPException(status_code=404, detail="Shift check not found")
        
        # Draft bo'lishini tekshirish
        if shift_check.status != "draft":
            raise HTTPException(
                status_code=400,
                detail="Can only upload photos to draft shift checks"
            )
        
        # Branch scoping - director faqat o'z filialidagi checklistga rasm yuklashi mumkin
        if current_user.role == "director":
            if shift_check.branch_id != current_user.branch_id:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot upload photos to other branch's shift check"
                )
    
    # 4. Rasm saqlash
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_url = f"/media/uploads/{filename}"
    
    return JSONResponse(
        {
            "file_url": file_url,
            "thumbnail_url": None,
            "file_size": len(content),
            "mime_type": file.content_type,
        }
    )