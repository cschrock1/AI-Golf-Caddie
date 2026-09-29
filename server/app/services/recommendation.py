from math import atan2, cos, radians, sin, sqrt


EARTH_RADIUS_METERS = 6_371_000
METERS_TO_YARDS = 1.0936133


def distance_yards(start: tuple[float, float], end: tuple[float, float]) -> int:
    longitude1, latitude1 = start
    longitude2, latitude2 = end
    latitude_delta = radians(latitude2 - latitude1)
    longitude_delta = radians(longitude2 - longitude1)
    latitude1 = radians(latitude1)
    latitude2 = radians(latitude2)
    a = sin(latitude_delta / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(longitude_delta / 2) ** 2
    return round(2 * EARTH_RADIUS_METERS * atan2(sqrt(a), sqrt(1 - a)) * METERS_TO_YARDS)


def choose_clubs(clubs: list, target_yards: int) -> tuple[object | None, object | None]:
    candidates = [
        (club, getattr(club, "carry_distance", None) or getattr(club, "total_distance", None))
        for club in clubs
    ]
    candidates = [(club, float(distance)) for club, distance in candidates if distance and float(distance) > 0]
    if not candidates:
        return None, None

    candidates.sort(key=lambda candidate: candidate[1])
    suitable = [candidate for candidate in candidates if candidate[1] >= target_yards]
    primary = min(suitable, key=lambda candidate: candidate[1]) if suitable else candidates[-1]
    alternatives = [candidate for candidate in candidates if candidate[0].id != primary[0].id]
    alternative = min(alternatives, key=lambda candidate: abs(candidate[1] - target_yards)) if alternatives else None
    return primary, alternative
