from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChecklistSection(Base):
    """
    CHECKLIST SECTION MODEL

    Bu jadval checklist bo‘limlarini saqlaydi.

    Masalan:
    - Внешняя территория
    - Зал
    - Гостевой туалет
    - Кухня
    - Склад
    - Холодильники

    Loyiha rus tilida bo‘lgani uchun title_ru ishlatiladi.
    """

    __tablename__ = "checklist_sections"

    # Ichki database ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Bo‘lim nomi rus tilida
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)

    # Ekranda tartib bilan chiqishi uchun
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Bo‘lim aktiv yoki aktiv emas
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Oxirgi yangilangan vaqt
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Shu bo‘lim ichidagi checklist savollar
    items = relationship(
        "ChecklistItem",
        back_populates="section",
        cascade="all, delete-orphan",
    )


class ChecklistItem(Base):
    """
    CHECKLIST ITEM MODEL

    Bu jadval har bir bo‘lim ichidagi savollarni saqlaydi.

    Masalan:
    Section: Зал

    Items:
    - Пол чистый
    - Столы чистые
    - Мусорные урны не переполнены

    Director shu itemlarga javob beradi:
    Да / Нет / Не применимо
    """

    __tablename__ = "checklist_items"

    # Ichki database ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Item qaysi bo‘limga tegishli
    section_id: Mapped[int] = mapped_column(
        ForeignKey("checklist_sections.id"),
        nullable=False,
        index=True,
    )

    # Savol matni rus tilida
    title_ru: Mapped[str] = mapped_column(String(500), nullable=False)

    # Bu savol uchun rasm majburiymi yoki yo‘q
    requires_photo: Mapped[bool] = mapped_column(Boolean, default=False)

    # Savollar tartibi
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Savol aktiv yoki aktiv emas
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Oxirgi yangilangan vaqt
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Item bog‘langan section
    section = relationship("ChecklistSection", back_populates="items")

    # Shu item bo‘yicha berilgan javoblar
    answers = relationship("CheckAnswer", back_populates="item")