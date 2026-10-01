# AI Golf Caddie

AI Golf Caddie is a full-stack golf application for tracking clubs, logging shots, reviewing course data, and getting helpful club recommendations. The app includes a Vue frontend, a Python FastAPI backend, and PostgreSQL/PostGIS for the data layer.

## What this app includes

- User registration and login
- Golfer profile and saved clubs with carry distances
- Course and hole data with mapped locations where available
- Shot logging during a round
- Personalized club recommendations based on distance to the target and the golfer's bag
- Current weather lookup for a mapped course hole
- Optional AI explanation for a recommendation when an OpenAI key is configured
- Mobile-friendly frontend with Capacitor support

## Project structure
# AI Golf Caddie ⛳

An AI-powered golf caddie that helps golfers make smarter club and shot decisions based on their personal performance, course conditions, and shot history.

## Overview

The system will allow golfers to:

* Create a personal golf profile
* Add clubs and average distances
* See GPS map of course
* Receive club and shot recommendations
* Track shots and round results
* Analyze personal performance
* Use AI to explain recommendations

The goal is to create a caddie that learns how an individual golfer plays and provides personalized recommendations.

## Planned Features

* [ ] User authentication
* [ ] Golfer profile
* [ ] Club and distance tracking
* [ ] Golf course/hole information
* [ ] Club recommendations
* [ ] Shot tracking
* [ ] Round tracking
* [ ] Performance dashboard
* [ ] AI-powered recommendations
* [ ] AI post-round analysis
* [ ] Weather integration
* [ ] GPS/course maps

## Roadmap

This project follows an iterative roadmap focused on delivering a working MVP, then progressively adding features and polish. Key milestones:

1. Project setup & infrastructure — frontend, backend, database, and developer tooling.
2. User accounts & golfer profiles — registration, authentication, club management.
3. Courses & rounds — course data, hole mapping, round creation, and scorecards.
4. Caddie recommendations — deterministic recommendation engine, then AI explanations.
5. Analytics & deployment — player statistics, dashboard views, and production deployment.

Work will continue iteratively; specific tasks are tracked in the project board and issue tracker rather than here.

## Tech Stack

### Frontend

* Vue 3
* Typescript
* Tailwind CSS
* Capacitor (by Ionic)

### Backend

* Python
* FastAPI
* 

### Database

* PostgreSQL + PostGIS

### AI

* OpenAI API

### GPS
* Mapbox

### Weather
* OpenMeteo

### Deployment

* Docker
* GitHub Actions
* Google Cloud Run

## How It Works

```text
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

## Project Structure

```text
ai-golf-caddie/
├── client/              # Vue 3 frontend
├── server/              # FastAPI backend
├── database/            # PostgreSQL/PostGIS setup
├── docker-compose.yml   # Local database and backend stack
├── .env.example         # Example local environment file
├── README.md
└── package.json
```

## Quick start

1. Copy `.env.example` to `.env`.
2. Update the environment values for your local setup.
3. Start the app:

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Local development

### Frontend

```bash
cd client
npm install
npm run dev
```

### Backend

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docker (database + backend):

```bash
docker compose up --build
```

API Docs: http://localhost:8000/docs
Health: http://localhost:8000/api/health

Security: Do not commit `.env` with secrets. Use `.env.example` as a template.

## Current live round features

Copy `.env.example` to `.env` and set the database URL, JWT secret, Mapbox token, and (optionally) the server-side `OPENAI_API_KEY`. For the iOS app, set `VITE_MOBILE_API_URL` to the backend address reachable from the phone. Never put the OpenAI key in a `VITE_` variable.

The frontend course picker lists saved backend courses and shows how many holes are mapped. Hole navigation and scorecards include mapped holes only. Stonehedge currently has Hole 1 mapped; holes 2–18 are intentionally not synthesized. The map's Locate action supplies the position used by the deterministic recommendation endpoint. Current weather is requested for the mapped hole location. Shot logging records the selected bag club, distance to the target before/after the shot when available, and the golfer-selected result.

`POST /api/recommendations/` computes a club suggestion from the golfer's saved carry distances, current GPS position, pin, and mapped bunker geometry. `GET /api/weather/current` returns current Open-Meteo conditions for a course/hole with a mapped point. `POST /api/caddie/explain` explains the computed recommendation through the OpenAI Responses API when `OPENAI_API_KEY` is configured; otherwise it returns a deterministic explanation. The API key remains server-side. See the [OpenAI text generation guide](https://developers.openai.com/api/docs/guides/text) for the Responses API behavior used by this integration.
