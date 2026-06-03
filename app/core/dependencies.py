"""
DEPENDENCIES

Token orqali current user olish.
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.modules.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        raw_user_id = payload.get("sub")

        if raw_user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = int(raw_user_id)

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: AsyncSession = Depends(get_db),
# ) -> User:
#     # VAQTINCHALIK — hardcoded user
#     result = await db.execute(select(User).where(User.username == "sardor"))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user