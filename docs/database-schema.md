# Database Schema (Design only)

This document outlines the planned relational schema and PostGIS fields for Phase 2. Use UUID primary keys where appropriate.

Entities (high level):

- users
- golfer_profiles
- clubs
- courses
- holes
- tees
- rounds
- shots
- weather_data

Example relationships:

```
User
  |
  v
Golfer Profile
  |
  +---- Clubs
  |
  +---- Rounds
          |
          v
        Shots

Course
  |
  v
Holes
  |
  v
Tees
```

Table sketches:

1) users
- pk: id (UUID)
- email (unique)
- hashed_password
- created_at, updated_at

2) golfer_profiles
- pk: id (UUID)
- user_id (UUID) FK -> users.id
- display_name
- handicap_index
- preferred_tees (FK to tees or simple enum)
- timezone
- created_at, updated_at

3) clubs
- pk: id (UUID)
- golfer_profile_id (UUID) FK -> golfer_profiles.id
- name (e.g., "7-iron")
- loft
- type (iron/wood/putter/wedge)
- average_distance
- distance_stddev (optional)
- created_at, updated_at

4) courses
- pk: id (UUID)
- name
- location (Point) -- PostGIS geography
- par_total
- created_at, updated_at

5) holes
- pk: id (UUID)
- course_id FK -> courses.id
- hole_number (1..18)
- par
- stroke_index
- tee_box_geoms (optional)
- green_geom (Polygon)
- fairway_geom (Polygon)
- bunkers_geom (MultiPolygon)
- water_geom (MultiPolygon)
- out_of_bounds_geom (MultiPolygon)
- pin_positions (could be separate table for daily pins)
- created_at, updated_at

6) tees
- pk: id (UUID)
- hole_id FK -> holes.id
- tee_name (e.g., "Blue", "White")
- tee_location (Point)
- tee_yards
- created_at, updated_at

7) rounds
- pk: id (UUID)
- golfer_profile_id FK -> golfer_profiles.id
- course_id FK -> courses.id
- tee_set_id FK -> tees (or reference tee group)
- started_at, completed_at
- score_total
- created_at, updated_at

8) shots
- pk: id (UUID)
- round_id FK -> rounds.id
- hole_id FK -> holes.id
- club_id FK -> clubs.id (optional)
- shot_number (stroke index within hole)
- start_location (Point) -- PostGIS
- end_location (Point) -- PostGIS
- distance_meters (computed or stored)
- result (enum: in_play, green, bunker, water, penalty, out_of_bounds)
- lie (text)
- penalties (int)
- created_at, updated_at

9) weather_data
- pk: id (UUID)
- course_id FK -> courses.id (or lat/lon)
- captured_at (timestamp)
- temperature_c
- wind_speed_mps
- wind_direction_degrees
- precipitation
- raw_payload (json)
- created_at, updated_at

Notes on spatial fields (PostGIS):

- Use `geography(Point,4326)` for single locations (tee, pin, shot locations) where accurate distance calculation is important.
- Use `geometry(MultiPolygon,4326)` for course features (fairways, bunkers, water) to allow spatial queries and intersection tests.
- Consider spatial indexes (GIST) on geometry/geography columns for performance.

Timestamps:

- All tables should include `created_at` and `updated_at` timestamps (UTC) and use database defaults where possible.

Foreign keys & constraints:

- Enforce FK constraints between users -> golfer_profiles -> rounds -> shots.
- Courses -> holes -> tees relationships are enforced.

This document is a design artifact. Actual SQLAlchemy models and migrations will be created in Phase 2.
