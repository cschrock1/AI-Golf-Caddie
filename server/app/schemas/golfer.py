from pydantic import BaseModel, ConfigDict, Field


class GolferProfileCreate(BaseModel):
    user_id: int
    handicap: float | None = Field(default=None, ge=0)
    preferred_tee: str | None = None


class GolferProfileResponse(BaseModel):
    id: int
    user_id: int
    handicap: float | None
    preferred_tee: str | None

    model_config = ConfigDict(from_attributes=True)
