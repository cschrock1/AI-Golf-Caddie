from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.course import Course
from app.models.hole import Hole
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    HoleCreate,
    HoleResponse,
)

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=list[CourseResponse])
def get_courses(
    db: Session = Depends(get_db)
):
    return db.query(Course).all()


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
    return db.query(Hole).filter(
        Hole.course_id == course_id
    ).all()


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
        yardage=hole.yardage
    )

    db.add(db_hole)
    db.commit()
    db.refresh(db_hole)

    return db_hole
