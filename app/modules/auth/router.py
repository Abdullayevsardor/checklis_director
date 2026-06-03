from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.modules.auth.schemas import (
    ChangePasswordRequest, 
    LoginResponse, 
    LoginRequest,
    FaceIdChallengeResponse, 
    FaceIdVerifyRequest,
    FaceIdRegisterChallengeResponse,
    FaceIdRegisterVerifyRequest
)
from app.modules.auth.service import (
    authenticate_user, 
    change_password_service,
    generate_face_id_challenge_service,  # YANGI ULANGAN XIZMAT
    verify_face_id_signature_service ,    # YANGI ULANGAN XIZMAT
    generate_registration_challenge_service,
    verify_and_save_registration_service

)
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/token")
async def login_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
    }



# @router.post("/login", response_model=LoginResponse)
# async def login(
#     payload: LoginRequest,
#     db: AsyncSession = Depends(get_db),
# ):
#     """
#     Directorlar uchun: Password + branch_id bilan login qilish.
#     """
#     user = await authenticate_user(
#         db=db,
#         password=payload.password,
#         branch_id=payload.branch_id,
#     )

#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials or branch")

#     token = create_access_token({"sub": str(user.id)})

#     return {
#         "access_token": token,
#         "token_type": "bearer",
#         "user": {
#             "id": user.id,
#             "full_name": user.full_name,
#             "role": user.role,
#             "branch_id": user.branch_id,
#             "branch_name": user.branch.name if user.branch else None,
#         }
#     }


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Directorlar va Admin'lar login qilishlari.
    - Director: password + branch_id bilan
    - Admin: username + password yoki faqat password bilan
    """
    user = await authenticate_user(
        db=db,
        password=payload.password,
        branch_id=payload.branch_id,
        username=payload.username,
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials or branch")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
            "branch_id": user.branch_id,
            "branch_name": user.branch.name if user.branch else "HQ",
        }
    }




@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await change_password_service(current_user, data, db)


# =====================================================================
# YANGI ENTERPRISE FACE ID (WEBAUTHN / PASSKEYS) ENDPOINTLARI
# =====================================================================

@router.post("/face-id/challenge", response_model=FaceIdChallengeResponse)
async def get_face_id_challenge(
    db: AsyncSession = Depends(get_db)
):
    """
    1-QADAM: Admin "Face ID" tugmasini bosganda chaqiriladi.
    Tizimdagi faqat ruxsat etilgan 3 ta adminning qurilma ID (Passkey) ro'yxatini va
    unikal challenge kodini qaytaradi.
    """
    # Servis qatlamidan bazadagi admin qurilmalarini yig'ib qaytaramiz
    challenge_data = await generate_face_id_challenge_service(db=db)
    return challenge_data


@router.post("/face-id/verify", response_model=LoginResponse)
async def verify_face_id(
    payload: FaceIdVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    2-QADAM: Telefon yuzni tanigach, frontend raqamli imzoni yuboradi.
    Backend imzoni apparat darajasida tekshirib, Admin kimligini aniqlaydi va unga 
    barcha filiallarni ko'rish huquqini beruvchi Global JWT Token qaytaradi.
    """
    # Kriptografik raqamli imzoni tekshirib, admin ob'ektini olamiz (Rasm ishlatilmaydi!)
    admin_user = await verify_face_id_signature_service(db=db, payload=payload)
    
    # Muvaffaqiyatli tekshiruvdan so'ng unikal JWT Token yaratamiz
    token = create_access_token({"sub": str(admin_user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": admin_user.id,
            "full_name": admin_user.full_name,
            "role": admin_user.role,
            "branch_id": admin_user.branch_id,  # Admin uchun NULL yoki 0 qaytadi
            "branch_name": "Markaziy Ofis (HQ)",
        }
    }





# =====================================================================
# YANGI: FACE ID QURILMASINI RO‘YXATDAN O‘TKAZISH (ULASH) ENDPOINTLARI
# =====================================================================

@router.post("/face-id/register/challenge", response_model=FaceIdRegisterChallengeResponse)
async def get_registration_challenge(
    current_user = Depends(get_current_user)  # Faqat tizimga kirgan odam ulashi mumkin
):
    """
    ULASH 1-BOSQICH: Admin profiliga kirib "Face ID ulash" tugmasini bosganda chaqiriladi.
    Brauzer yangi kalit yaratishi uchun kerakli unikal so'rovni generatsiya qiladi.
    """
    return await generate_registration_challenge_service(current_user=current_user)


@router.post("/face-id/register/verify")
async def verify_and_save_registration(
    payload: FaceIdRegisterVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    ULASH 2-BOSQICH: Telefon yuzni skanerlab yangi kalit yaratgach, frontend buni yuboradi.
    Backend ommaviy kalitni (Public Key) ajratib oladi va PostgreSQL bazasiga xavfsiz yozadi.
    """
    return await verify_and_save_registration_service(
        db=db, 
        current_user=current_user, 
        payload=payload
    )
