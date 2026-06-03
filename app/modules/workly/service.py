from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.workly.models import WorklyEmployee
from app.modules.branches.models import Branch


def detect_role_from_positions(positions: list) -> str:
    """
    Workly positions dan role aniqlash
    """

    if not positions:
        return "employee"

    titles = []

    for position in positions:

        if isinstance(position, dict):
            title = position.get("title", "")

        else:
            title = str(position)

        titles.append(title.lower().strip())

    positions_text = " ".join(titles)

    print("POSITIONS TEXT:", positions_text)

    # DIRECTOR
    director_keywords = [
        "директор",
        "операционный директор",
        "директор пбо",
        "branch director",
        "regional director",
    ]

    # MANAGER
    manager_keywords = [
        "менеджер",
        "менеджер смены",
        "управляющий",
        "начальник",
        "администратор",
        "supervisor",
        "manager",
    ]

    for keyword in director_keywords:
        if keyword in positions_text:
            return "director"

    for keyword in manager_keywords:
        if keyword in positions_text:
            return "manager"

    return "employee"

def normalize_branch_name(department) -> str:
    if isinstance(department, dict):
        department = department.get("name") or department.get("title") or ""

    if department is None:
        department = ""

    return str(department).strip().upper()


 


async def sync_workly_employee_batch(db, employees_data: list[dict]):
    """
    Barcha xodimlarni bir xil batch'da sync qiladi - N+1 query problemasini oldini oladi
    """
    employee_ids = [str(e["id"]) for e in employees_data]
    branch_names = [normalize_branch_name(e.get("department")) for e in employees_data]
    
    # 1️⃣ BARCHA BRANCH'LARNI BIR SATRIDA OLAMIZ
    existing_branches = await db.scalars(
        select(Branch).where(Branch.name.in_(branch_names))
    )
    branches_dict = {b.name: b for b in existing_branches}
    
    # 2️⃣ BARCHA EXISTING USER'LARNI BIR SATRIDA OLAMIZ
    existing_users = await db.scalars(
        select(User).where(User.workly_employee_id.in_(employee_ids))
    )
    users_dict = {u.workly_employee_id: u for u in existing_users}
    
    # 3️⃣ YO'Q BO'LGAN BRANCH'LARNI YARATAMIZ
    for employee in employees_data:
        branch_name = normalize_branch_name(employee.get("department"))
        
        if branch_name not in branches_dict:
            branch = Branch(name=branch_name)
            db.add(branch)
            branches_dict[branch_name] = branch
    
    # 4️⃣ FLUSH - yangi branch ID'larni olish uchun
    if any(b.id is None for b in branches_dict.values()):
        await db.flush()
    
    # 5️⃣ USER'LARNI SYNC QILAMIZ
    synced = 0

    for employee in employees_data:

        employee_id = str(employee["id"])
        full_name = employee["full_name"]

        branch_name = normalize_branch_name(
            employee.get("department")
        )

        if not branch_name:
            continue

        positions = employee.get("positions", [])

        role = detect_role_from_positions(positions)

        if role not in ["director", "manager"]:
            continue

        branch = branches_dict.get(branch_name)

        if not branch:
            continue

        if employee_id in users_dict:

            user = users_dict[employee_id]

            user.full_name = full_name
            user.branch_id = branch.id
            user.role = role
            user.is_active = True

        else:

            user = User(
                workly_employee_id=employee_id,
                full_name=full_name,
                branch_id=branch.id,
                role=role,
                is_active=True,
                hashed_password="",
            )

            db.add(user)

            users_dict[employee_id] = user

        synced += 1

    return synced


ALLOWED_WORKLY_ADMINS = ["Sardor", "Anton", "Asliddin"]


async def get_allowed_workly_admins(db: AsyncSession) -> list[User]:
    """Workly orqali faqat ruxsat etilgan 3 ta adminni aniqlaydi."""
    stmt = select(WorklyEmployee).where(
        WorklyEmployee.full_name.in_(ALLOWED_WORKLY_ADMINS),
        WorklyEmployee.is_active == True,
    )
    result = await db.execute(stmt)
    employees = result.scalars().all()

    if not employees:
        # Agar Workly sync hali yo'q bo'lsa yoki WorklyEmployee jadvali bo'sh bo'lsa,
        # fallback sifatida User jadvalidagi to'g'ridan-to'g'ri ism bo'yicha tekshiramiz.
        stmt_users = select(User).where(
            User.full_name.in_(ALLOWED_WORKLY_ADMINS),
            User.role == "admin",
            User.is_active == True,
        )
        result_users = await db.execute(stmt_users)
        return result_users.scalars().all()

    employee_ids = [employee.workly_employee_id for employee in employees]
    stmt_users = select(User).where(
        User.workly_employee_id.in_(employee_ids),
        User.role == "admin",
        User.is_active == True,
    )
    result_users = await db.execute(stmt_users)
    users = result_users.scalars().all()

    users_by_workly_id = {user.workly_employee_id: user for user in users if user.workly_employee_id}
    created_any = False

    # If Workly employee exists but User record does not, create a placeholder admin user.
    for employee in employees:
        if employee.workly_employee_id not in users_by_workly_id:
            user = User(
                workly_employee_id=employee.workly_employee_id,
                full_name=employee.full_name,
                branch_id=employee.branch_id,
                role="admin",
                is_active=True,
                hashed_password="",
            )
            db.add(user)
            users.append(user)
            users_by_workly_id[employee.workly_employee_id] = user
            created_any = True

    if created_any:
        await db.flush()

    return users
