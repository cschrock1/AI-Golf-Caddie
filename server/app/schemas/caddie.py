from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.recommendation import RecommendationRequest, RecommendationResponse


class CaddieConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=2000)


class CaddieExplainRequest(RecommendationRequest):
    question: str = Field(..., min_length=1, max_length=500)
    conversation: list[CaddieConversationMessage] = Field(default_factory=list, max_length=20)


class CaddieChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    conversation: list[CaddieConversationMessage] = Field(default_factory=list, max_length=20)


class CaddieExplainResponse(BaseModel):
    recommendation: RecommendationResponse
    explanation: str
    explanation_source: str


class CaddieChatResponse(BaseModel):
    answer: str
    answer_source: str
