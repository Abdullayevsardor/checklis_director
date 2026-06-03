from datetime import datetime

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Branch(Base):
    """
    BRANCH MODEL

    Bu jadval filiallarni saqlaydi.

    Filiallar qo‘lda kiritilmaydi.
    Asosiy ma’lumot Workly API orqali keladi.

    Masalan:
    - Chilonzor filiali
    - Yunusobod filiali
    - Sergeli filiali

    Director filial tanlamaydi.
    Director qaysi filialga tegishli ekanini branch_id orqali bilamiz.
    """

    __tablename__ = "branches"

    # Ichki database ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Workly ichidagi filial ID
    # Shu orqali Workly filiali bilan bizning database filialini bog‘laymiz
    workly_branch_id: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
    )

    # Filial nomi
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Filial manzili
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Filial aktiv yoki aktiv emas
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Oxirgi yangilangan vaqt
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Shu filialga bog‘langan userlar
    users = relationship("User", back_populates="branch")

    # Shu filialga bog‘langan Workly xodimlar
    workly_employees = relationship("WorklyEmployee", back_populates="branch")

    # Shu filial bo‘yicha smena checklistlari
    shift_checks = relationship("ShiftCheck", back_populates="branch")