from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ShiftCheck(Base):
    """
    SHIFT CHECK MODEL

    Bu jadval bitta smena tekshiruvini saqlaydi.

    Masalan:
    Director bugun ertalab checklist ochdi.
    Shu bitta ochilgan checklist — ShiftCheck hisoblanadi.

    Unda:
    - qaysi filial
    - qaysi director
    - qaysi smena
    - status
    - boshlanish va yuborilish vaqti saqlanadi.
    """

    __tablename__ = "shift_checks"

    # Ichki database ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Checklist qaysi filial uchun to‘ldirilgan
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id"),
        nullable=False,
        index=True,
    )

    # Checklistni kim to‘ldirgan
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Smena turi
    # Masalan: morning / day / night
    shift_type: Mapped[str] = mapped_column(
        String(50),
        default="day",
    )

    # Checklist statusi
    # draft / submitted / approved / rejected
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        index=True,
    )

    # Umumiy izoh
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tekshiruv boshlangan vaqt
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Director submit qilgan vaqt
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Oxirgi yangilangan vaqt
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ShiftCheck bog‘langan filial
    branch = relationship("Branch", back_populates="shift_checks")

    # ShiftCheckni yaratgan user
    user = relationship("User", back_populates="shift_checks")

    # Shu checklist ichidagi javoblar
    answers = relationship(
        "CheckAnswer",
        back_populates="shift_check",
        cascade="all, delete-orphan",
    )


class CheckAnswer(Base):
    """
    CHECK ANSWER MODEL

    Bu jadval checklist ichidagi har bir savolga berilgan javobni saqlaydi.

    Masalan:
    Item: Пол чистый?
    Answer: Да

    Yoki:
    Item: Мусорная урна чистая?
    Answer: Нет
    Comment: Урна переполнена
    Photo: rasm URL
    """

    __tablename__ = "check_answers"

    # Ichki database ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Javob qaysi ShiftCheck ichida
    shift_check_id: Mapped[int] = mapped_column(
        ForeignKey("shift_checks.id"),
        nullable=False,
        index=True,
    )

    # Javob qaysi checklist itemga tegishli
    item_id: Mapped[int] = mapped_column(
        ForeignKey("checklist_items.id"),
        nullable=False,
        index=True,
    )

    # Javob statusi
    # not_checked / yes / no / na
    status: Mapped[str] = mapped_column(
        String(50),
        default="not_checked",
    )

    # Shu savolga izoh
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Oxirgi yangilangan vaqt
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Javob bog‘langan ShiftCheck
    shift_check = relationship("ShiftCheck", back_populates="answers")

    # Javob bog‘langan checklist item
    item = relationship("ChecklistItem", back_populates="answers")

    # Shu javobga biriktirilgan rasmlar
    photos = relationship(
        "AnswerPhoto",
        back_populates="answer",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint('shift_check_id', 'item_id', name='uq_shift_check_item'),
    )


class AnswerPhoto(Base):
    """
    ANSWER PHOTO MODEL

    Bu jadval javobga biriktirilgan rasmlarni saqlaydi.

    MUHIM:
    Rasmning o‘zi databasega saqlanmaydi.
    Databasega faqat rasm URL saqlanadi.

    Rasm S3 yoki MinIO ichida turadi.

    Masalan:
    file_url:
    https://storage.domain.com/checks/15/item-2/photo.jpg
    """

    __tablename__ = "answer_photos"

    # Ichki database ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Rasm qaysi javobga tegishli
    answer_id: Mapped[int] = mapped_column(
        ForeignKey("check_answers.id"),
        nullable=False,
        index=True,
    )

    # Original rasm URL
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Kichik preview rasm URL
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Rasm hajmi
    file_size: Mapped[int | None] = mapped_column(nullable=True)

    # Rasm turi
    # image/jpeg, image/png, image/webp
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Rasm aktiv yoki o‘chirilgan
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Yuklangan vaqt
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Rasm bog‘langan javob
    answer = relationship("CheckAnswer", back_populates="photos")