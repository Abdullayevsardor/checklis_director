from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.workly.client import get_workly_employees
from app.modules.workly.service import sync_workly_employee_batch


router = APIRouter(
    tags=["Workly"],
)
"""
WORKLY CLIENT

Bu fayl Workly API bilan to‘g‘ridan-to‘g‘ri ishlaydi.

Vazifalari:
- Workly API ga HTTP request yuborish
- employees endpointdan xodimlarni olish
- branches endpointdan filiallarni olish
- token bilan ishlash (agar kerak bo‘lsa)

BU YERDA:
❌ business logic yozilmaydi
❌ databasega yozilmaydi

FAKT:
Bu faqat "API wrapper"
"""

@router.get("/health")
async def workly_health():
    """
    Workly moduli ishlayotganini tekshiradi.
    Bu endpoint Workly API bilan real sync qilmaydi,
    faqat modul ulanganini test qiladi.
    """
    return {"module": "workly", "status": "ok"}



@router.post("/sync")
async def sync_workly(db: AsyncSession = Depends(get_db)):
    try:
        employees_data = await get_workly_employees()
        synced = 0

        if not employees_data:
            return {"success": False, "message": "API'dan ma'lumot kelmadi", "synced": 0}

        if isinstance(employees_data, dict):
            employees_list = employees_data.get("items", [])
        elif isinstance(employees_data, list):
            employees_list = employees_data
        else:
            return {"success": False, "message": "Ma'lumot formati noto'g'ri", "synced": 0}

        # Barcha employee'larni bir xil batch'da sync qilamiz
        synced = await sync_workly_employee_batch(db, employees_list)
        
        await db.commit()  # ✅ hammasi bir commit
        
        return {
            "success": True,
            "synced": synced,
        }

    except Exception as e:
        await db.rollback()  # ✅ xato bo'lsa bekor qilish
        print(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))