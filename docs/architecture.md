# System Architecture

Overview (Phase 1): the application will be split between a Vue 3 + Capacitor client and a FastAPI backend with a PostgreSQL + PostGIS data store. External services will be used for maps, weather, and AI explanations.

High level diagram:

```
Vue 3 / Capacitor Client
          |
          | HTTPS / JSON
          v
     FastAPI API
          |
          +---------------------------+
          |                           |
          v                           v
PostgreSQL + PostGIS          External Services
                                  |
                         +--------+--------+
                         |        |        |
                      Mapbox  Open-Meteo OpenAI
```

Application flow (future):

```
Golfer Data
     ↓
Course Information
     ↓
Shot History
     ↓
Recommendation Engine
     ↓
Club / Shot Recommendation
     ↓
AI Explanation
     ↓
Shot Result
     ↓
Updated Golfer Data
```

Notes:

- The Recommendation Engine (structured algorithmic layer) and the AI layer (natural language explanation and reasoning) are separate. The recommendation engine should compute recommended clubs and targets deterministically using golfer data and course geometry. The AI layer should primarily explain the already‑computed recommendation in human‑readable terms.
- Communication between client and API uses HTTPS+JSON. API will be versioned under `/api/v1`.
- PostGIS handles spatial data (course geometry, pins, hazards, shot locations). Keep spatial queries primarily in the backend service.
- External integrations (Mapbox, Open‑Meteo, OpenAI) should be accessed from the backend when API keys must be protected; the frontend may access map tiles or public endpoints directly where appropriate.
