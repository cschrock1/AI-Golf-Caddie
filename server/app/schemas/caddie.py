from pydantic import BaseModel, Field

from app.schemas.recommendation import RecommendationRequest, RecommendationResponse


class CaddieExplainRequest(RecommendationRequest):
    question: str = Field(..., min_length=1, max_length=500)


class CaddieExplainResponse(BaseModel):
    recommendation: RecommendationResponse
    explanation: str
    explanation_source: str
