from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.course import Course
from app.models.hole import Hole
from app.schemas.course import (
    CourseCreate,
    CourseImport,
    CourseImportResponse,
    CourseResponse,
    HoleCreate,
    HoleResponse,
    ProviderCourseImport,
)
from app.services.golf_api import GolfApiError, import_course as import_provider_course

router = APIRouter(prefix="/courses", tags=["Courses"])

GEOMETRY_FIELDS = (
    "tee_location",
    "pin_location",
    "green_geometry",
    "fairway_geometry",
    "bunker_geometry",
    "water_geometry",
)

GEOMETRY_TYPES = {
    "tee_location": "Point",
    "pin_location": "Point",
    "green_geometry": "Polygon",
    "fairway_geometry": "Polygon",
    "bunker_geometry": "MultiPolygon",
    "water_geometry": "MultiPolygon",
}


def _geometry_from_geojson(value: dict | None):
    if value is None:
        return None
    return from_shape(shape(value), srid=4326)


def _validated_geometry(value: dict | None, field: str):
    if value is None:
        return None

    try:
        geometry = shape(value)
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=f"Invalid GeoJSON for {field}") from error

    expected_type = GEOMETRY_TYPES[field]
    if geometry.geom_type != expected_type:
        raise HTTPException(
            status_code=422,
            detail=f"{field} must be a GeoJSON {expected_type}"
        )
    if not geometry.is_valid:
        raise HTTPException(status_code=422, detail=f"Invalid geometry for {field}")

    return from_shape(geometry, srid=4326)


def _hole_response(hole: Hole) -> dict:
    response = {
        "id": hole.id,
        "course_id": hole.course_id,
        "hole_number": hole.hole_number,
        "par": hole.par,
        "yardage": hole.yardage,
    }
    for field in GEOMETRY_FIELDS:
        geometry = getattr(hole, field)
        response[field] = mapping(to_shape(geometry)) if geometry is not None else None
    return response


@router.get("/", response_model=list[CourseResponse])
def get_courses(
    db: Session = Depends(get_db)
):
    return db.query(Course).all()


@router.post("/import", response_model=CourseImportResponse)
def import_course(
    payload: CourseImport,
    db: Session = Depends(get_db)
):
    hole_numbers = [hole.hole_number for hole in payload.holes]
    if len(set(hole_numbers)) != len(hole_numbers):
        raise HTTPException(status_code=422, detail="Each hole number must be unique")

    converted_holes = []
    for imported_hole in payload.holes:
        geometry_values = {
            field: _validated_geometry(getattr(imported_hole, field), field)
            for field in GEOMETRY_FIELDS
        }
        converted_holes.append((imported_hole, geometry_values))

    course = db.query(Course).filter(
        Course.name == payload.course.name,
        Course.city == payload.course.city,
        Course.state == payload.course.state,
    ).first()
    if course is None:
        course = Course(
            name=payload.course.name,
            city=payload.course.city,
            state=payload.course.state,
        )
        db.add(course)
        db.flush()
    else:
        course.holes.clear()

    for imported_hole, geometry_values in converted_holes:
        db.add(Hole(
            course_id=course.id,
            hole_number=imported_hole.hole_number,
            par=imported_hole.par,
            yardage=imported_hole.yardage,
            **geometry_values,
        ))

    db.commit()
    db.refresh(course)
    return {
        "course": course,
        "imported_holes": len(converted_holes),
    }


@router.post("/import/provider", response_model=CourseImportResponse)
def import_course_from_provider(
    payload: ProviderCourseImport,
    db: Session = Depends(get_db),
):
    try:
        imported_course = import_provider_course(payload.name, payload.city, payload.state)
        return import_course(CourseImport.model_validate(imported_course), db)
    except GolfApiError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db)
):
    db_course = Course(
        name=course.name,
        city=course.city,
        state=course.state
    )

    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    return db_course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course: CourseCreate,
    db: Session = Depends(get_db)
):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    db_course.name = course.name
    db_course.city = course.city
    db_course.state = course.state

    db.commit()
    db.refresh(db_course)
    return db_course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    db.delete(db_course)
    db.commit()
    return None


@router.get(
    "/{course_id}/holes",
    response_model=list[HoleResponse]
)
def get_holes(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    holes = db.query(Hole).filter(
        Hole.course_id == course_id
    ).all()
    return [_hole_response(hole) for hole in holes]


@router.get(
    "/{course_id}/holes/{hole_number}",
    response_model=HoleResponse
)
def get_hole(
    course_id: int,
    hole_number: int,
    db: Session = Depends(get_db)
):
    hole = db.query(Hole).filter(
        Hole.course_id == course_id,
        Hole.hole_number == hole_number
    ).first()
    if not hole:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hole not found")
    return _hole_response(hole)


@router.post(
    "/holes",
    response_model=HoleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_hole(
    hole: HoleCreate,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == hole.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    db_hole = Hole(
        course_id=hole.course_id,
        hole_number=hole.hole_number,
        par=hole.par,
        yardage=hole.yardage,
        **{
            field: _geometry_from_geojson(getattr(hole, field))
            for field in GEOMETRY_FIELDS
        }
    )

    db.add(db_hole)
    db.commit()
    db.refresh(db_hole)

    return _hole_response(db_hole)
