"""
SHIFT CHECK SCHEMAS
"""

from datetime import datetime

from pydantic import BaseModel


class ShiftCheckStartRequest(BaseModel):
    """
    Endi user_id va branch_id kerak emas.
    Ular current_user dan olinadi.
    """

    shift_type: str = "day"


class ShiftCheckStartResponse(BaseModel):
    id: int
    user_id: int
    branch_id: int
    shift_type: str
    status: str

    class Config:
        from_attributes = True


class AnswerPhotoInput(BaseModel):
    file_url: str
    thumbnail_url: str | None = None
    file_size: int | None = None
    mime_type: str | None = None


class AnswerInput(BaseModel):
    item_id: int
    status: str
    comment: str | None = None
    photos: list[AnswerPhotoInput] = []
    photo_url: str | None = None


class SaveAnswersRequest(BaseModel):
    answers: list[AnswerInput]


class ShiftCheckSubmitResponse(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True




class ShiftCheckListOut(BaseModel):
    id: int
    branch_id: int
    # checklist_id: int
    status: str
    started_at: datetime | None = None
    submitted_at: datetime | None = None

    class Config:
        from_attributes = True