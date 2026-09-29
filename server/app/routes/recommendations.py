from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.shape import to_shape
from shapely.geometry import LineString, Point
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.club import Club
from app.models.hole import Hole
from app.models.user import User
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation import choose_clubs, distance_yards


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse)
def recommend_shot(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not -180 <= request.player_location[0] <= 180 or not -90 <= request.player_location[1] <= 90:
        raise HTTPException(status_code=422, detail="Player location must be longitude, latitude")

    hole = db.query(Hole).filter(Hole.id == request.hole_id).first()
    if not hole:
        raise HTTPException(status_code=404, detail="Hole not found")
    if not hole.pin_location:
        raise HTTPException(status_code=422, detail="A mapped pin location is required for a recommendation")

    pin = to_shape(hole.pin_location)
    player = Point(request.player_location)
    if not player.is_valid:
        raise HTTPException(status_code=422, detail="Invalid player location")

    target = pin
    target_name = "Pin"
    risk = "Low"
    rationale = "Club choice is based on the measured distance and your saved club carry distances."
    direct_line = LineString([player, pin])
    crosses_water = bool(hole.water_geometry and direct_line.intersects(to_shape(hole.water_geometry)))
    crosses_bunker = bool(hole.bunker_geometry and direct_line.intersects(to_shape(hole.bunker_geometry)))
    if crosses_water or crosses_bunker:
        risk = "High" if crosses_water else "Medium"
        hazard = "mapped water" if crosses_water else "a mapped bunker"
        rationale = f"The direct line to the pin crosses {hazard}. Favor a safer line toward the center of the green."
        if hole.green_geometry:
            target = to_shape(hole.green_geometry).representative_point()
            target_name = "Green center"

    yards = distance_yards(tuple(request.player_location), (target.x, target.y))
    clubs = db.query(Club).filter(Club.user_id == current_user.id).all()
    primary, alternative = choose_clubs(clubs, yards)
    if primary is None:
        raise HTTPException(status_code=422, detail="Add club carry distances to your bag before requesting a recommendation")

    chosen_club, carry = primary
    return {
        "club_id": chosen_club.id,
        "club_name": chosen_club.name,
        "carry_yards": round(carry),
        "target_yards": yards,
        "target_location": [target.x, target.y],
        "target_name": target_name,
        "risk": risk,
        "rationale": rationale,
        "alternative_club": alternative[0].name if alternative else None,
        "alternative_carry_yards": round(alternative[1]) if alternative else None,
    }
