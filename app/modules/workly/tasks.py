from app.core.database import AsyncSessionLocal
from app.modules.workly.client import get_workly_employees
from app.modules.workly.service import sync_workly_employee_batch


async def auto_sync_workly_employees():
    async with AsyncSessionLocal() as db:
        try:
            print("WORKLY AUTO SYNC STARTED")

            employees_data = await get_workly_employees()

            if not employees_data:
                print("WORKLY AUTO SYNC: API'dan ma'lumot kelmadi")
                return

            if isinstance(employees_data, dict):
                employees_list = employees_data.get("items", [])
            elif isinstance(employees_data, list):
                employees_list = employees_data
            else:
                print("WORKLY AUTO SYNC: Ma'lumot formati noto'g'ri")
                return

            synced = await sync_workly_employee_batch(db, employees_list)

            await db.commit()

            print(f"WORKLY AUTO SYNC SUCCESS: synced={synced}")

        except Exception as e:
            await db.rollback()
            print(f"WORKLY AUTO SYNC ERROR: {e}")