from pydantic import BaseModel, Field


class RoundScoreBase(BaseModel):
    round_id: int | None = None
    hole_id: int | None = None
    hole_number: int | None = None
    strokes: int = Field(..., ge=1, le=20)


class RoundScoreCreate(RoundScoreBase):
    pass


class RoundScoreResponse(RoundScoreBase):
    id: int

    class Config:
        orm_mode = True
