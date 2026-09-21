from pydantic import BaseModel


class RoundScoreBase(BaseModel):
    round_id: int | None = None
    hole_id: int | None = None
    hole_number: int | None = None
    strokes: int


class RoundScoreCreate(RoundScoreBase):
    pass


class RoundScoreResponse(RoundScoreBase):
    id: int

    class Config:
        orm_mode = True
