from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1)
    city: str | None = None
    state: str | None = None


class CourseResponse(BaseModel):
    id: int
    name: str
    city: str | None
    state: str | None

    model_config = ConfigDict(from_attributes=True)


class HoleCreate(BaseModel):
    course_id: int
    hole_number: int = Field(..., ge=1, le=18)
    par: int = Field(..., ge=3, le=5)
    yardage: int = Field(..., gt=0)


class HoleResponse(BaseModel):
    id: int
    course_id: int
    hole_number: int
    par: int
    yardage: int

    model_config = ConfigDict(from_attributes=True)
