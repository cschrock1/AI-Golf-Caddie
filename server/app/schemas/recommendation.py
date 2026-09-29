from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    hole_id: int
    player_location: list[float] = Field(..., min_length=2, max_length=2)


class RecommendationResponse(BaseModel):
    club_id: int
    club_name: str
    carry_yards: int
    target_yards: int
    target_location: list[float]
    target_name: str
    risk: str
    rationale: str
    alternative_club: str | None = None
    alternative_carry_yards: int | None = None
