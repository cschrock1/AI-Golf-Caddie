from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class RoundCreate(BaseModel):
    user_id: int
    course_id: int
    date: date
    score: int | None = Field(default=None, ge=0)


class RoundResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    date: date
    score: int | None

    model_config = ConfigDict(from_attributes=True)
