from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1)
    city: str | None = None
    state: str | None = None


class CourseImport(BaseModel):
    course: CourseCreate
    holes: list["HoleImport"] = Field(..., min_length=1, max_length=18)


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
    tee_location: dict[str, Any] | None = None
    pin_location: dict[str, Any] | None = None
    green_geometry: dict[str, Any] | None = None
    fairway_geometry: dict[str, Any] | None = None
    bunker_geometry: dict[str, Any] | None = None
    water_geometry: dict[str, Any] | None = None


class HoleImport(BaseModel):
    hole_number: int = Field(..., ge=1, le=18)
    par: int = Field(..., ge=3, le=5)
    yardage: int = Field(..., gt=0)
    tee_location: dict[str, Any] | None = None
    pin_location: dict[str, Any] | None = None
    green_geometry: dict[str, Any] | None = None
    fairway_geometry: dict[str, Any] | None = None
    bunker_geometry: dict[str, Any] | None = None
    water_geometry: dict[str, Any] | None = None


class CourseImportResponse(BaseModel):
    course: CourseResponse
    imported_holes: int


class ProviderCourseImport(BaseModel):
    name: str = Field(..., min_length=1)
    city: str | None = None
    state: str | None = None


class HoleResponse(BaseModel):
    id: int
    course_id: int
    hole_number: int
    par: int
    yardage: int
    tee_location: dict[str, Any] | None = None
    pin_location: dict[str, Any] | None = None
    green_geometry: dict[str, Any] | None = None
    fairway_geometry: dict[str, Any] | None = None
    bunker_geometry: dict[str, Any] | None = None
    water_geometry: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
