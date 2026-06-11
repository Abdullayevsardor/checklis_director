import asyncio
# Import all models first
import app.models

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.modules.users.models import User

async def create_face_id_admins():
    """Sardor, Anton, Asliddin admin users yaratish"""
    
    admins_data = [
        {
            "full_name": "Sardor",
            "username": "sardor",
            "phone": "+998901234567",
            # "password": "Sardor@2026"
            "password": "1431"
        },
        {
            "full_name": "Anton",
            "username": "anton",
            "phone": "+998902345678",
            "password": "Anton@2026"
        },
        {
            "full_name": "A.Ruzikulov",
            "username": "a.ruzikulov",
            "phone": "+998903456789",
            "password": "a.ruzikulov@maxway.uz"
        }
    ]
    
    async with AsyncSessionLocal() as db:
        print("\n🔧 Face ID Admin Foydalanuvchilari Yaratilmoqda...\n")
        
        for admin_data in admins_data:
            # Check if user already exists
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.username == admin_data["username"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⚠️  {admin_data['full_name']} allaqachon mavjud (ID: {existing.id})")
                continue
            
            # Create new admin user
            user = User(
                full_name=admin_data["full_name"],
                username=admin_data["username"],
                phone=admin_data["phone"],
                hashed_password=hash_password(admin_data["password"]),
                role="admin",
                branch_id=None,
                is_active=True,
                face_id_allowed=True  # ✅ Face ID ruxsat etilgan
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            print(f"✅ {user.full_name} yaratildi!")
            print(f"   └─ ID: {user.id}")
            print(f"   └─ Username: {user.username}")
            print(f"   └─ Role: admin")
            print(f"   └─ Face ID Allowed: {user.face_id_allowed}")
            print(f"   └─ Password: {admin_data['password']}\n")
        
        print("\n✨ Hammasi tayyor!")

if __name__ == "__main__":
    asyncio.run(create_face_id_admins())
