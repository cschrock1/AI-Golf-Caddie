from typing import Any

import httpx

from app.core.config import GOLF_API_BASE_URL, GOLF_API_KEY


class GolfApiError(Exception):
    pass


def _resources(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("resources", "courses", "data", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise GolfApiError("Golf API returned an unexpected list response")


def _resource(payload: Any) -> dict[str, Any] | list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("resource", "course", "data"):
            value = payload.get(key)
            if isinstance(value, dict):
                return value
        return payload
    raise GolfApiError("Golf API returned an unexpected object response")


def _course_id(course: dict[str, Any]) -> Any:
    return (
        course.get("id")
        or course.get("courseId")
        or course.get("courseID")
        or course.get("course_id")
    )


def _course_name(course: dict[str, Any]) -> str:
    return str(course.get("courseName") or course.get("clubName") or course.get("name") or "")


def _first_value(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if item.get(key) is not None:
            return item[key]
    return None


def _point(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if not item:
        return None
    longitude = _first_value(item, "longitude", "long", "lon", "lng")
    latitude = _first_value(item, "latitude", "lat")
    if longitude is None or latitude is None:
        return None
    return {"type": "Point", "coordinates": [float(longitude), float(latitude)]}


def _polygon(item: Any) -> dict[str, Any] | None:
    if isinstance(item, dict) and item.get("type") in {"Polygon", "MultiPolygon"}:
        return item
    if not isinstance(item, list) or not item:
        return None

    coordinates = []
    for point in item:
        longitude = _first_value(point, "longitude", "long", "lon", "lng")
        latitude = _first_value(point, "latitude", "lat")
        if longitude is None or latitude is None:
            return None
        coordinates.append([float(longitude), float(latitude)])

    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])
    return {"type": "Polygon", "coordinates": [coordinates]}


def _geometry_for_surface(polygons: list[dict[str, Any]], surface: str) -> dict[str, Any] | None:
    matches = [item.get("polygon") for item in polygons if str(item.get("surfacetype", item.get("surfaceType", ""))).lower() == surface]
    converted = [_polygon(item) for item in matches]
    converted = [item for item in converted if item is not None]
    if not converted:
        return None
    if len(converted) == 1:
        return converted[0]
    return {"type": "MultiPolygon", "coordinates": [item["coordinates"] for item in converted]}


def _point_from_coordinate(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "Point",
        "coordinates": [float(item["longitude"]), float(item["latitude"])],
    }


def _normalize_golfapi_coordinates(course: dict[str, Any], coordinates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pars = course.get("parsMen") or []
    tees = course.get("tees") or []
    white_tee = next((tee for tee in tees if str(tee.get("teeName", "")).lower() == "white"), tees[0] if tees else {})
    holes = []

    for hole_number in range(1, int(course.get("numHoles") or 18) + 1):
        hole_coordinates = [item for item in coordinates if int(item.get("hole", 0)) == hole_number]
        tee_points = [item for item in hole_coordinates if int(item.get("poi", 0)) == 1]
        green_points = [item for item in hole_coordinates if int(item.get("poi", 0)) in {11, 12}]
        tee_point = next((item for item in tee_points if int(item.get("location", 0)) == 2), tee_points[0] if tee_points else None)
        green_point = green_points[0] if green_points else None
        yardage = white_tee.get(f"length{hole_number}")

        holes.append({
            "hole_number": hole_number,
            "par": int(pars[hole_number - 1]) if len(pars) >= hole_number else 4,
            "yardage": int(yardage or 0),
            "tee_location": _point_from_coordinate(tee_point) if tee_point else None,
            "pin_location": _point_from_coordinate(green_point) if green_point else None,
            "green_geometry": None,
            "fairway_geometry": None,
            "bunker_geometry": None,
            "water_geometry": None,
        })
    return holes


def _normalize_holes(course: dict[str, Any], coordinates: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(coordinates, dict) and isinstance(coordinates.get("coordinates"), list):
        return _normalize_golfapi_coordinates(course, coordinates["coordinates"])
    if isinstance(coordinates, list):
        raw_holes = coordinates
    else:
        raw_holes = coordinates.get("holes") or coordinates.get("resources") or coordinates.get("data") or course.get("holes")
    if not isinstance(raw_holes, list):
        raise GolfApiError("Golf API response did not include hole coordinates")

    holes = []
    for index, raw_hole in enumerate(raw_holes, start=1):
        number = int(_first_value(raw_hole, "hole_number", "holeNumber", "number") or index)
        polygons = raw_hole.get("polygons") or raw_hole.get("features") or []
        holes.append({
            "hole_number": number,
            "par": int(_first_value(raw_hole, "par") or 4),
            "yardage": int(_first_value(raw_hole, "yardage", "yards", "distance") or 0),
            "tee_location": _point(_first_value(raw_hole, "tee", "tee_location", "teeLocation")),
            "pin_location": _point(_first_value(raw_hole, "pin", "flag", "pin_location", "pinLocation")),
            "green_geometry": _geometry_for_surface(polygons, "green"),
            "fairway_geometry": _geometry_for_surface(polygons, "fairway"),
            "bunker_geometry": _geometry_for_surface(polygons, "bunker"),
            "water_geometry": _geometry_for_surface(polygons, "water"),
        })
    return holes


def import_course(course_name: str, city: str | None = None, state: str | None = None) -> dict[str, Any]:
    if not GOLF_API_KEY:
        raise GolfApiError("GOLF_API_KEY is not configured")

    headers = {"Authorization": f"Bearer {GOLF_API_KEY}"}
    base_url = GOLF_API_BASE_URL.rstrip("/")
    try:
        with httpx.Client(headers=headers, timeout=20) as client:
            response = client.get(
                f"{base_url}/courses",
                params={
                    "city": city,
                    "state": state,
                    "country": "usa",
                },
            )
            response.raise_for_status()
            matches = _resources(response.json())
            if not matches:
                raise GolfApiError("No matching course found")
            requested_name = course_name.lower()
            selected = next(
                (
                    item for item in matches
                    if requested_name in _course_name(item).lower()
                    or _course_name(item).lower() in requested_name
                ),
                matches[0],
            )
            provider_id = _course_id(selected)
            if provider_id is None:
                raise GolfApiError("Golf API course result has no identifier")

            course_response = client.get(f"{base_url}/courses/{provider_id}")
            course_response.raise_for_status()
            course = _resource(course_response.json())
            coordinates_response = client.get(f"{base_url}/coordinates/{provider_id}")
            coordinates_response.raise_for_status()
            coordinates = _resource(coordinates_response.json())
    except httpx.HTTPError as error:
        raise GolfApiError("Golf API request failed") from error

    return {
        "course": {
            "name": _first_value(course, "name", "courseName") or course_name,
            "city": _first_value(course, "city") or city,
            "state": _first_value(course, "state") or state,
        },
        "holes": _normalize_holes(course, coordinates),
    }