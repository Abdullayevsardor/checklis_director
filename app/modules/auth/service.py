import os
import secrets
import base64
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# WebAuthn kutubxonasidan enterprise tekshiruv asboblari
from webauthn import verify_authentication_response, verify_registration_response
from webauthn.helpers.structs import (
    AuthenticationCredential,
    RegistrationCredential,
    AuthenticatorAssertionResponse,
    AuthenticatorAttestationResponse,
)

from app.core.security import verify_password, hash_password 
from app.modules.users.models import User, UserPasskey
from app.modules.workly.service import get_allowed_workly_admins


def decode_base64url(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)

# Tizim xavfsizlik parametrlari
RP_NAME = "Shift Checklist System"
# WebAuthn RP_ID: exact hostname (no port!) - must match frontend's window.location.hostname
RP_ID = os.getenv("RP_ID", "localhost")
# ORIGIN: complete URL with protocol - must match window.location.origin exactly
ORIGIN = os.getenv("ORIGIN", "http://localhost:5173")

# Vaqtinchalik challenge kodlarini xotirada saqlash
CHALLENGE_STORE = {}


def get_branch_password(branch_id: int) -> str | None:
    """Branch login password formulasini qaytaradi."""
    if 1 <= branch_id <= 9:
        return str(2020 + branch_id)
    if 10 <= branch_id <= 49:
        return str(2000 + branch_id)
    return None


 
async def authenticate_user(
    db: AsyncSession,
    password: str,
    branch_id: int | None = None,
    username: str | None = None,
) -> User | None:
    """Admin login (parol orqali kimligini avtomat aniqlash) va Director login."""
    
    # 1. ADMIN LOGINI (Branch ID 0 bo'lsa yoki frontenddan so'rov kelganda)
    if branch_id == 0 or username:
        # Bazadan barcha faol adminlarni yuklab olamiz
        stmt = select(User).options(selectinload(User.branch)).where(
            (User.role == "admin") & (User.is_active == True)
        )
        result = await db.execute(stmt)
        admins = result.scalars().all()

        # Har bir adminning parolini kiritilgan parol bilan solishtiramiz
        for admin in admins:
            if verify_password(password, admin.hashed_password):
                return admin  # To'g'ri kelgan birinchi adminni (Sardor, Anton yoki Asliddin) qaytaramiz
        
        return None  # Hech biri to'g'ri kelmasa

    # 2. DIRECTOR / MANAGER LOGINI (Branch bo'yicha)
    if branch_id is None:
        return None

    expected_password = get_branch_password(branch_id)
    if expected_password is None or password != expected_password:
        return None

    result = await db.execute(
        select(User)
        .options(selectinload(User.branch))
        .where(
            (User.branch_id == branch_id) &
            (User.role.in_(["director", "manager", "admin"])) &
            (User.is_active == True)
        )
    )

    users = result.scalars().all()
    if not users:
        return None

    for role in ["director", "manager", "admin"]:
        for user in users:
            if user.role == role:
                return user

    return users[0]
 


async def change_password_service(user, data, db):
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong old password")

    user.hashed_password = hash_password(data.new_password)
    await db.commit()
    await db.refresh(user)
    return {"message": "Password changed successfully"}

 

async def generate_face_id_challenge_service(db: AsyncSession):
    """
    1-Bosqich: Faqat Workly'dan kelgan va ruxsat berilgan 3 ta adminning 
    Face ID kalitlarini yig'adi va challenge beradi.
    """
    # 1. Workly ma'lumotiga asoslangan ruxsat etilgan 3 ta adminni aniqlaymiz
    allowed_users = await get_allowed_workly_admins(db)
    admin_ids = [user.id for user in allowed_users if user.id]

    if not admin_ids:
        raise HTTPException(
            status_code=404,
            detail="Tizimda Workly tomonidan ruxsat etilgan faol adminlar topilmadi"
        )

    # 3. Shu 3 ta adminga tegishli ro'yxatdan o'tgan Face ID datchik kalitlarini olish
    stmt_keys = select(UserPasskey).where(UserPasskey.user_id.in_(admin_ids))
    db_passkeys = (await db.execute(stmt_keys)).scalars().all()

    challenge_code = secrets.token_urlsafe(32)
    CHALLENGE_STORE[challenge_code] = True

    allowed_credentials = [
        {"id": pkey.credential_id, "type": "public-key"} 
        for pkey in db_passkeys
    ]

    return {
        "challenge": challenge_code,
        "allowed_credentials": allowed_credentials
    }




async def verify_face_id_signature_service(db: AsyncSession, payload) -> User:
    """2-Bosqich (Login): Telefon yuzni tanigach jo'natgan raqamli imzoni tekshiradi."""
    stmt = select(UserPasskey).options(selectinload(UserPasskey.user)).where(
        UserPasskey.credential_id == payload.credential_id
    )
    result = await db.execute(stmt)
    user_passkey = result.scalar_one_or_none()

    if not user_passkey or not user_passkey.user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Ushbu Face ID qurilmasi tizimda ro'yxatdan o'tmagan"
        )

    allowed_users = await get_allowed_workly_admins(db)
    allowed_workly_ids = {user.workly_employee_id for user in allowed_users if user.workly_employee_id}
    if user_passkey.user.workly_employee_id not in allowed_workly_ids:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ushbu foydalanuvchi Workly orqali ruxsat etilmagan"
        )
    
    if not CHALLENGE_STORE.pop(payload.challenge, None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired Face ID challenge")

    try:
        assertion_response = AuthenticatorAssertionResponse(
            client_data_json=decode_base64url(payload.client_data_json),
            authenticator_data=decode_base64url(payload.authenticator_data),
            signature=decode_base64url(payload.signature),
            user_handle=None,
        )

        verify_authentication_response(
            credential=AuthenticationCredential(
                id=payload.credential_id,
                raw_id=decode_base64url(payload.credential_id),
                type="public-key",
                response=assertion_response,
            ),
            expected_challenge=decode_base64url(payload.challenge),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=user_passkey.public_key,
            credential_current_sign_count=0
        )
    except Exception as e:
        print(f"WebAuthn Datchik tekshiruvi ogohlantirishi: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Face ID autentifikatsiyasi muvaffaqiyatsiz bo'ldi")

    return user_passkey.user
 


async def verify_and_save_registration_service(db: AsyncSession, current_user: User, payload):
    """
    Ulash 2-Bosqich: Qurilma skanerlangandan keyin kelgan ochiq kalitni 
    kriptografik tekshiradi va PostgreSQL bazasiga muvaffaqiyatli saqlaydi.
    Kutubxona bilan dict muloqoti to'liq to'g'rilandi.
    """
    # Ma'lumotlarni dict ko'rinishiga keltirib olamiz
    data = payload if isinstance(payload, dict) else payload.model_dump()

    # 1. Challenge kodini xotiradan tekshirib olamiz
    active_challenges = list(CHALLENGE_STORE.keys())
    if not active_challenges:
        raise HTTPException(status_code=400, detail="Xavfsizlik kodi (challenge) topilmadi yoki eskirgan")
    
    current_challenge = active_challenges[-1]
    CHALLENGE_STORE.pop(current_challenge, None)

    try:
        # 2. WebAuthn datchik kutubxonasi uchun ob'ektni xatosiz tayyorlaymiz
        attestation_response = AuthenticatorAttestationResponse(
            client_data_json=decode_base64url(data.get("client_data_json")),
            attestation_object=decode_base64url(data.get("attestation_object")),
        )

        credential_obj = RegistrationCredential(
            id=data.get("credential_id"),
            raw_id=decode_base64url(data.get("credential_id")),
            type="public-key",
            response=attestation_response,
        )

        # 3. Kriptografik haqiqiyligini tekshirish
        verification = verify_registration_response(
            credential=credential_obj,
            expected_challenge=decode_base64url(current_challenge),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN
        )

        # 4. Yangi kalit ob'ektini foydalanuvchiga bog'lab yaratish
        new_passkey = UserPasskey(
            user_id=current_user.id,
            credential_id=data.get("credential_id"),
            public_key=verification.credential_public_key,
            sign_count=0
        )
        
        db.add(new_passkey)
        await db.commit()

        return {"status": "success", "message": "Face ID (Passkey) muvaffaqiyatli ulandi"}

    except Exception as e:
        print(f"❌ Kriptografik tekshiruvda xatolik: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Datchik kalitini tasdiqlashda xatolik: {str(e)}"
        )


# =====================================================================
# 2. FACE ID QURILMASINI RO‘YXATDAN O‘TKAZISH (ULASH FLOW)
# =====================================================================
 
async def generate_registration_challenge_service(current_user: User):
    """Ulash 1-Bosqich: Challenge hosil qiladi va xotiraga yozadi."""
    challenge_code = secrets.token_urlsafe(32)
    
    # Faqat True emas, aynan shu admin nomini belgilab saqlaymiz
    CHALLENGE_STORE[challenge_code] = current_user.id

    user_id_str = str(current_user.id)

    return {
        "challenge": challenge_code,
        "user_id": user_id_str,
        "user_name": current_user.username or f"user_{current_user.id}",
        "user_display_name": current_user.full_name or f"Admin_{current_user.id}"
    }


async def verify_registration_response_service(db: AsyncSession, current_user: User, payload):
    """Ulash 2-Bosqich: Brauzerdan kelgan yangi ochiq kalitni tekshiradi va bazaga saqlaydi."""
    if not CHALLENGE_STORE.pop(payload.challenge, None):
        raise HTTPException(status_code=400, detail="Invalid or expired registration challenge")

    try:
        attestation_response = AuthenticatorAttestationResponse(
            client_data_json=decode_base64url(payload.client_data_json),
            attestation_object=decode_base64url(payload.attestation_object),
        )

        verification = verify_registration_response(
            credential=RegistrationCredential(
                id=payload.credential_id,
                raw_id=decode_base64url(payload.credential_id),
                type="public-key",
                response=attestation_response,
            ),
            expected_challenge=decode_base64url(payload.challenge),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN
        )

        # Yangi kalitni bazaga saqlash
        new_passkey = UserPasskey(
            user_id=current_user.id,
            credential_id=payload.credential_id,
            public_key=verification.credential_public_key,
            sign_count=0
        )
        db.add(new_passkey)
        await db.commit()

        return {"status": "success", "message": "Face ID (Passkey) muvaffaqiyatli ulandi"}

    except Exception as e:
        print(f"Registration Error: {e}")
        raise HTTPException(status_code=400, detail="Face ID qurilmasini ro'yxatdan o'tkazishda xatolik")
