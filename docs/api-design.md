# API Design (High Level)

Base path: `/api/v1`

Planned endpoints (Phase 2 will implement most):

- `GET /api/v1/health` — service health
- `POST /api/v1/auth` — authentication endpoints (login/register/token)
- `GET/POST /api/v1/users` — user management
- `GET/POST /api/v1/profile` — golfer profile endpoints
- `GET/POST /api/v1/clubs` — club management
- `GET/POST /api/v1/courses` — course catalog
- `GET/POST /api/v1/holes` — hole details
- `GET/POST /api/v1/rounds` — start/view rounds
- `GET/POST /api/v1/shots` — record shots
- `GET /api/v1/weather` — weather data for a given location/time
- `GET /api/v1/analytics` — golfer analytics (summary endpoints)
- `POST /api/v1/recommendations` — request recommendation from engine
- `POST /api/v1/caddie` — higher‑level caddie actions (composite endpoints)

Typical HTTP methods:

- `GET` — read resources
- `POST` — create resources or request actions (recommendation requests)
- `PATCH` — partial updates
- `PUT` — full replace (used sparingly)
- `DELETE` — delete resources

Security & versioning:

- All API routes are prefixed with `/api/v1` to allow future versioning.
- Authentication will be token‑based (JWT or similar) with HTTPS required in production.

Health endpoint (Phase 1 implementation):

- `GET /api/v1/health`

Response (200):

```json
{
  "status": "ok",
  "service": "ai-golf-caddie-api"
}
```

Note: Do not implement full auth or protected routes in Phase 1. Phase 1 will implement only the health endpoint and structural routing.
