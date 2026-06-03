"""
CHECKLIST SCHEMAS

Bu faylda frontendga qaytadigan response formatlari yoziladi.
"""

from pydantic import BaseModel


class ChecklistItemResponse(BaseModel):
    """
    Bitta checklist savoli.
    """

    id: int
    title_ru: str
    requires_photo: bool
    sort_order: int

    class Config:
        from_attributes = True


class ChecklistSectionResponse(BaseModel):
    """
    Bitta checklist bo‘limi va uning savollari.
    """

    id: int
    title_ru: str
    sort_order: int
    items: list[ChecklistItemResponse]

    class Config:
        from_attributes = True