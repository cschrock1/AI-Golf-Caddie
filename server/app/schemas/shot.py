from pydantic import BaseModel, ConfigDict, Field


class ShotCreate(BaseModel):
    round_id: int
    hole_id: int
    club_id: int
    start_distance: float | None = Field(default=None, ge=0)
    end_distance: float | None = Field(default=None, ge=0)
    result: str | None = Field(default=None, max_length=40)


class ShotResponse(BaseModel):
    id: int
    round_id: int
    hole_id: int
    club_id: int
    start_distance: float | None
    end_distance: float | None
    result: str | None

    model_config = ConfigDict(from_attributes=True)
