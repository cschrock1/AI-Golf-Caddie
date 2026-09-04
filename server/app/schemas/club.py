from pydantic import BaseModel, ConfigDict, Field


class ClubCreate(BaseModel):
    name: str = Field(..., min_length=1)
    carry_distance: float | None = Field(default=None, ge=0)
    total_distance: float | None = Field(default=None, ge=0)


class ClubResponse(BaseModel):
    id: int
    user_id: int
    name: str
    carry_distance: float | None
    total_distance: float | None

    model_config = ConfigDict(from_attributes=True)
