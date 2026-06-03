from pydantic import BaseModel
from typing import List, Optional


# =====================================================================
# MAVJUD LOGIN VA PAROL SXEMALARI
# =====================================================================

class LoginRequest(BaseModel):
    username: str | None = None
    password: str
    branch_id: int | None = None


class LoginUserOut(BaseModel):
    id: int
    full_name: str
    role: str
    branch_id: int | None = None  # Admin uchun branch_id null bo'lishi mumkin
    branch_name: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: LoginUserOut


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# =====================================================================
# YANGI: FACE ID (WEBAUTHN / PASSKEYS) KIRISH SXEMALARI
# =====================================================================

class AllowedCredentialSchema(BaseModel):
    """
    Adminlarga tegishli ro'yxatdan o'tgan qurilmalar identifikatori.
    """
    id: str  # Qurilmaning unikal credential_id si
    type: str = "public-key"


class FaceIdChallengeResponse(BaseModel):
    """
    1-Bosqich (Challenge): Admin 'Face ID' tugmasini bosganda backend
    frontend brauzeriga yuboradigan xavfsizlik so'rovi.
    """
    challenge: str  # Replay attack'dan himoya qiluvchi tasodifiy unikal kod
    allowed_credentials: List[AllowedCredentialSchema]  # Faqat 3 ta adminning qurilmalar ro'yxati


class FaceIdVerifyRequest(BaseModel):
    """
    2-Bosqich (Verify): Telefon yuzni tanigach, brauzer generatsiya qiladigan
    va backendga tekshirish uchun yuboriladigan kriptografik imzo ma'lumotlari.
    """
    credential_id: str  # Aynan qaysi admin kirayotganini bildiruvchi ID
    challenge: str  # Avvalgi /face-id/challenge endpointidan olgan challenge kodi
    client_data_json: str  # Brauzerning xavfsizlik konteksti (base64 holatida)
    authenticator_data: str  # Qurilma metadata ma'lumotlari (base64)
    signature: str  # Telefon Face ID datchigi yordamida yaratgan raqamli imzo


class FaceIdAdminOut(BaseModel):
    id: int
    full_name: str
    username: str | None
    role: str
    face_id_allowed: bool


class FaceIdAdminUpdateRequest(BaseModel):
    face_id_allowed: bool


# =====================================================================
# YANGI: FACE ID QURILMASINI RO‘YXATDAN O‘TKAZISH (ULASH) SXEMALARI
# =====================================================================

class FaceIdRegisterChallengeResponse(BaseModel):
    """
    Ulash 1-Bosqich: Admin o'z profilida "Face ID ulash" tugmasini bosganda
    backend brauzerga beradigan yangi kalit yaratish so'rovi.
    """
    challenge: str
    user_id: str
    user_name: str
    user_display_name: str


class FaceIdRegisterVerifyRequest(BaseModel):
    """
    Ulash 2-Bosqich: Telefon yangi Face ID kaliti (Public Key) yaratgandan so'ng,
    frontend uni PostgreSQL bazasiga saqlash uchun yuboradigan ma'lumotlar formati.
    """
    credential_id: str  # Telefon generatsiya qilgan yangi qurilma ID si
    attestation_object: str  # Yangi yaratilgan Ommaviy kalitni (Public Key) ichiga olgan ob'ekt (base64)
    client_data_json: str  # Brauzer xavfsizlik tasdig'i (base64)
    device_name: Optional[str] = "Admin Phone"  # Qurilma nomi (ixtiyoriy)
