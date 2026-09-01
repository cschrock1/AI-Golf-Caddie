# AI Golf Caddie — Functional & Non‑Functional Requirements

Phase 1 is setup and planning only. This document lists the intended functional and non‑functional requirements for the full project scope. Implementation is deferred to later phases.

## Functional Requirements (planned)

- User registration and login (email/password; later OAuth)
- Golfer profiles (display name, handicap, preferred tees, bio)
- Handicap calculation and storage
- Preferred tees per course and per round
- Club management (add/edit clubs, loft, type)
- Average club distances per golfer
- Golf courses (course metadata and geographic data)
- Golf holes (par, hole index, length)
- Tee locations (multiple sets per course)
- Greens (geometry, location)
- Fairways (geometry)
- Bunkers (geometry)
- Water hazards (geometry)
- Out‑of‑bounds areas (geometry)
- Pin locations (per hole and per day)
- GPS golfer location capture (mobile device)
- Weather information per location/time
- Round tracking (start round, holes, completion)
- Shot tracking (record shots during rounds)
  - Club used
  - Shot distance
  - Shot start / end location (geographic)
  - Shot result (e.g., landed, penalty, green in regulation)
  - Penalties and lie information
- Golf analytics and reporting
  - Scoring averages
  - Fairway percentage
  - Greens in regulation (GIR) percentage
  - Putting averages
  - Club distance averages and dispersion
  - Accuracy and miss tendencies
- Personalized club recommendations (per shot / per hole)
- Personalized target recommendations (aim points, layups)
- Recommendation confidence and risk indicators
- AI recommendation explanations (natural language reasoning)
- Pre‑round strategy generation
- Post‑round analysis and insights
- Round history and searchable records
- Performance dashboard (charts, summaries)

## Non‑Functional Requirements

- Responsive design (desktop & mobile)
- Mobile‑friendly UI (prioritize touch UX)
- Maintainable architecture and modular code
- Secure authentication and session management
- Secure password storage (bcrypt / Argon2) and salts
- Input validation on all APIs (Pydantic and client validation)
- API security (CORS, rate limiting considered later)
- Environment variable configuration and secret management
- Docker support for development and deployment
- Testability: unit and integration tests for backend and critical frontend logic
- Reasonable API performance and low latency for core paths
- HTTPS in production (TLS termination at load balancer)
- Scalable deployment (containerized services, stateless backend)
- Clear, versioned documentation

## Constraints & Notes

- Phase 1 focuses on documentation and scaffolding only; no database schemas or business logic will be implemented beyond the health endpoint and structural placeholders.
- Use UUIDs for primary keys where appropriate in Phase 2 design.
- Geographic data will use PostGIS types (Point, Geometry, MultiPolygon) for course and shot location fields.
