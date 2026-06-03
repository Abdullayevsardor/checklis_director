from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """
    USER MODEL

    Bu jadval tizim foydalanuvchilarini saqlaydi:
    admin, director, supervisor.

    Director faqat o‘z filialini ko‘radi.
    Directorning filiali branch_id orqali aniqlanadi.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    workly_employee_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        unique=True,
    )

    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id"),
        nullable=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    phone: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )

    username: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, default="password")

    role: Mapped[str] = mapped_column(
        String(50),
        default="director",
        index=True,
    )

    face_id_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    branch = relationship("Branch", back_populates="users")
    shift_checks = relationship("ShiftCheck", back_populates="user")
    
    # YANGI: Foydalanuvchining Face ID (Passkey) qurilmalari bilan aloqasi
    passkeys = relationship("UserPasskey", back_populates="user", cascade="all, delete-orphan")


class UserPasskey(Base):
    """
    USER PASSKEY MODEL

    Adminlarning Face ID (WebAuthn) kriptografik kalitlarini saqlaydi.
    Rasm saqlanmaydi, faqat raqamli imzo tekshirish uchun ommaviy kalitlar saqlanadi.
    """

    __tablename__ = "user_passkeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Qurilma (telefon/kompyuter) Face ID yaratganda beradigan unikal identifikator
    credential_id: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    
    # Kriptografik Ommaviy Kalit (Public Key) - Raqamli imzolarni tekshirish uchun ishlatiladi
    public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    
    # Qurilma imzolash sanogʻi — WebAuthn `sign_count`.
    sign_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Qurilma nomi (Masalan: "Admin's iPhone 15 Pro" yoki "HQ MacBook")
    device_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="passkeys")
