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

1. Copy `.env.example` then create and paste into `.env` file.
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

## Environment variables

The app expects a local `.env` file with values such as:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- `VITE_API_BASE_URL`
- `VITE_MOBILE_API_URL`
- `VITE_MAPBOX_TOKEN`
- Optional `OPENAI_API_KEY`

Do not commit secrets to the repository. Keep API keys on the server side and use `.env` only for local development.

## Notes

- Recommendations and weather checks work best when a course hole has mapped geometry.
- The included sample course data is limited. In the current dataset, Stonehenge Hole 1 is mapped, while the other holes are not synthesized.
- The OpenAI explanation endpoint is optional. If no key is set, the app still provides a deterministic explanation.

## Tech stack

- Frontend: Vue 3, Vite, TypeScript, Tailwind CSS, Capacitor
- Backend: Python, FastAPI
- Database: PostgreSQL + PostGIS
- Weather: Open-Meteo
- Mapping: Mapbox
- Optional AI explanation: OpenAI API

## License

This project is for educational purposes.

