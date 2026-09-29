import logging

from urllib.error import URLError
from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.course import Course
from app.models.hole import Hole
from app.services.weather import get_current_weather


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current")
def current_course_weather(
    course_id: int,
    hole_number: int = Query(default=1, ge=1, le=18),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    hole = db.query(Hole).filter(Hole.course_id == course_id, Hole.hole_number == hole_number).first()
    if not hole:
        raise HTTPException(status_code=404, detail=f"Hole {hole_number} is not mapped for this course")

    location = hole.pin_location or hole.tee_location
    if not location:
        raise HTTPException(status_code=422, detail=f"Hole {hole_number} has no mapped location for weather lookup")

    point = to_shape(location)
    try:
        return get_current_weather(point.y, point.x)
    except (URLError, TimeoutError, OSError, ValueError):
        logger.exception("Weather provider request failed for course_id=%s hole_number=%s", course_id, hole_number)
        raise HTTPException(status_code=503, detail="Current weather is temporarily unavailable")
