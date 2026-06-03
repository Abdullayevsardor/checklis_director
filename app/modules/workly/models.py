from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WorklyEmployee(Base):
    """
    WORKLY EMPLOYEE MODEL

    Bu jadval Workly API dan kelgan xodimlarni saqlaydi.

    Nima uchun alohida jadval kerak?

    Chunki Worklydagi barcha xodimlar bizning tizimga login qilmasligi mumkin.
    Lekin biz Worklydagi xodimlarni saqlab,
    ulardan directorlarni ajratib olishimiz kerak.

    Keyin director uchun User yaratiladi yoki mavjud userga bog‘lanadi.
    """

    __tablename__ = "workly_employees"

    # Ichki database ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Workly ichidagi xodim ID
    workly_employee_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # Xodim qaysi filialga biriktirilgan
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id"),
        nullable=True,
        index=True,
    )

    # Xodim to‘liq ismi
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Telefon raqam
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    # Lavozim
    # Masalan: Директор филиала
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Bu xodim director ekanini belgilaydi
    is_director: Mapped[bool] = mapped_column(Boolean, default=False)

    # Worklyda aktiv yoki aktiv emas
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Oxirgi yangilangan vaqt
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Xodim bog‘langan filial
    branch = relationship("Branch", back_populates="workly_employees")