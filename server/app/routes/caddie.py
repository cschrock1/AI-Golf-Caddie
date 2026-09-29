import logging
from urllib.error import URLError

from fastapi import APIRouter, Depends
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.routes.recommendations import recommend_shot
from app.schemas.caddie import CaddieExplainRequest, CaddieExplainResponse
from app.schemas.recommendation import RecommendationRequest
from app.services.caddie import explain_recommendation
from app.models.hole import Hole
from app.services.weather import get_current_weather


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/caddie", tags=["Caddie"])


@router.post("/explain", response_model=CaddieExplainResponse)
def explain_shot(
    request: CaddieExplainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recommendation_request = RecommendationRequest(
        hole_id=request.hole_id,
        player_location=request.player_location,
    )
    recommendation = recommend_shot(recommendation_request, db, current_user)
    weather = None
    hole = db.query(Hole).filter(Hole.id == request.hole_id).first()
    location = (hole.pin_location or hole.tee_location) if hole else None
    if location:
        point = to_shape(location)
        try:
            weather = get_current_weather(point.y, point.x)
        except (URLError, TimeoutError, OSError, ValueError):
            logger.info("Live conditions were unavailable for the caddie explanation")
    explanation, source = explain_recommendation(request.question, recommendation, weather)
    if source == "rules":
        logger.info("Using deterministic caddie explanation fallback")
    return {
        "recommendation": recommendation,
        "explanation": explanation,
        "explanation_source": source,
    }
