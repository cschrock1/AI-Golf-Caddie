# AI Golf Caddie

AI Golf Caddie is a golf app for saving clubs and carry distances, exploring course data, logging shots, and getting club recommendations. It has a Vue web app, a FastAPI API, and a PostgreSQL database with PostGIS.

## Use the hosted website

The deployed website is:

- **Frontend:** <https://ai-golf-caddie-web-77sj.onrender.com>
- **API health check:** <https://ai-golf-caddie-api-77sj.onrender.com/api/health>

Open the frontend link in a browser and register an account. The frontend talks to the hosted API and Supabase database. Accounts created on a local development database are separate from hosted accounts; register again on the hosted site.

The same frontend link works in a phone browser. The separate Capacitor iOS app uses `VITE_MOBILE_API_URL`; for a hosted iOS build, set it to the hosted API URL with `/api` and rebuild/sync the iOS app. A local iOS development build can use the computer's LAN address instead.

## Start locally on a new computer

You do not need Python, PostgreSQL, or the app's JavaScript/Python packages installed ahead of time. The first setup needs an internet connection so Docker, Node.js, and project dependencies can be downloaded.

### Requirements

- A supported 64-bit Windows, macOS, or Linux computer. About 8 GB of memory and several GB of free disk space are recommended for a local development setup.
- Docker Desktop on Windows/macOS, or Docker Engine with the Compose plugin on Linux.
- Node.js LTS, which includes npm.
- Internet access for initial downloads.

Download and extract the project ZIP from its GitHub repository. Open a terminal in the extracted `AI-Golf-Caddie` folder. No Git installation is required if you use the ZIP download.

### Start the API and database

Copy `.env.example` to `.env` in the project root. Its database settings are configured for the local Compose database.

```bash
docker compose up --build
```

On the first run Docker downloads the database image and builds the API image. The API applies database migrations and loads development sample data. Keep this terminal open.

### Start the web frontend

Install Node.js LTS if needed. Open a second terminal in the project folder and run:

```bash
cd client
npm install
npm run dev
```

Keep this terminal open and visit <http://localhost:5173>.

Local addresses:

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- API health: <http://localhost:8000/api/health>

Press `Ctrl+C` in each terminal to stop its service. Docker stores the local database in a named volume, so it remains when the containers stop.

## Deploy or update the hosted website

The repository includes [`render.yaml`](render.yaml), a Render Blueprint for the static frontend and Docker API. Supabase hosts the PostgreSQL/PostGIS database.

### Supabase database

1. Create a Supabase project and keep its database password private.
2. Enable the `postgis` extension under **Database → Extensions**.
3. In the Supabase **Connect** panel, copy the **Session pooler** connection string (port `5432`).
4. In Render's API service environment, set `DATABASE_URL` to that URI. Replace the prefix `postgresql://` with `postgresql+psycopg://`, and replace `[YOUR-PASSWORD]` with the actual password. Preserve the project reference, host, port, and database name from the copied URI. URL-encode special characters in the password.

For example, the value has this form:

```text
postgresql+psycopg://postgres.PROJECT_REF:ENCODED_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require
```

Do not copy this placeholder literally. Use the current URI shown by your Supabase project's **Connect** panel. The API's Psycopg 3 driver uses the `+psycopg` URL prefix.

### Render settings

Connect the GitHub repository in Render and create or sync a Blueprint from `render.yaml`. Render provides the public service URLs. If Render assigns URLs with generated suffixes, use the actual URLs shown in the dashboard, not the unsuffixed examples in `render.yaml`.

For the currently deployed services, the environment values are:

- In the **frontend static site → Environment**, set `VITE_API_BASE_URL` to `https://ai-golf-caddie-api-77sj.onrender.com/api`.
- In the **API web service → Environment**, set `CORS_ORIGINS` to `https://ai-golf-caddie-web-77sj.onrender.com`.
- In the **API web service → Environment**, set `DATABASE_URL` to the Supabase connection string described above. Render generates `JWT_SECRET_KEY` through the Blueprint.

Enter only the value in Render's value field, without text like `VITE_API_BASE_URL=`. `VITE_API_BASE_URL` includes `/api`; `CORS_ORIGINS` is just the frontend origin, with no path and no trailing slash. After changing environment values, redeploy both services: the frontend URL is embedded at build time, and the API loads CORS/database settings at startup. Use **Manual Deploy → Deploy latest commit** in each service if it does not deploy automatically.

Check deployment with:

- Frontend: <https://ai-golf-caddie-web-77sj.onrender.com>
- API health: <https://ai-golf-caddie-api-77sj.onrender.com/api/health>

If Render assigns different URLs in a future deployment, update these two environment values to match the new frontend and API origins, then redeploy.

## Environment variables and optional integrations

`.env.example` is for local development. In Render, configure variables on the matching service instead of uploading or committing `.env`:

- API service: `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, optional `GOLF_API_KEY`, and optional `OPENAI_API_KEY`.
- Frontend static site: `VITE_API_BASE_URL` and optional `VITE_MAPBOX_TOKEN`.
- Native iOS app: `VITE_MOBILE_API_URL` is compiled into the app; rebuild/sync the app after changing it.

Course search/data from the Golf API requires `GOLF_API_KEY`. Maps require a public Mapbox token in `VITE_MAPBOX_TOKEN`; restrict the token to the website's domain. AI-written recommendation explanations can use `OPENAI_API_KEY`; without it, the app uses its built-in explanation. Weather lookup uses Open-Meteo and needs internet access.

Keep `DATABASE_URL`, `JWT_SECRET_KEY`, and provider API secrets private. Variables beginning with `VITE_` are included in the browser build and must not contain secrets.

## Troubleshooting

- **Registration or login shows “Unable to reach the server”:** This message is a generic frontend fallback and can mean a network, CORS, or API/database error. Confirm the frontend `VITE_API_BASE_URL` ends in `/api`, confirm API `CORS_ORIGINS` exactly matches the frontend origin, and redeploy both services. If it still fails, check the API logs at the time of the request for `POST /api/auth/register` or `/api/auth/token`.
- **API health works but registration fails:** Health does not verify a registration database query. Check the API logs for the request error and verify that `DATABASE_URL` is the current Supabase session-pooler URI, with the correct password and database name.
- **Phone says it cannot reach the server:** Open the hosted frontend in Safari. If using the installed iOS app, set `VITE_MOBILE_API_URL` to the hosted API URL plus `/api`, then rebuild and reinstall the app.
- **`docker` or `npm` is not recognized:** Install Docker Desktop (or Docker Engine plus Compose) or Node.js LTS, then reopen the terminal.
- **A course or feature is missing:** The included course dataset is limited. Stonehenge Hole 1 is mapped; other holes are not synthesized. Some course data features also require a Golf API key.

Free hosting is suitable for a small demo, not a production service. Render's free API may sleep when idle, and Supabase free projects have usage limits and may pause after inactivity. Review [Render's current free-tier limits](https://render.com/docs/free) and [Supabase pricing and limits](https://supabase.com/pricing); back up user data you need to keep.

## Project structure

```text
AI-Golf-Caddie/
├── client/              # Vue 3 + Vite web app
├── server/              # FastAPI API and database migrations
├── database/            # PostgreSQL/PostGIS initialization and seed SQL
├── docker-compose.yml   # Local database and API
├── render.yaml          # Render deployment Blueprint
└── .env.example         # Local environment example
```

## Tech stack

- Frontend: Vue 3, Vite, TypeScript, Tailwind CSS, Capacitor
- Backend: Python, FastAPI
- Database: PostgreSQL + PostGIS
- Weather: Open-Meteo
- Mapping: Mapbox
- Optional AI explanation: OpenAI API

## License

This project is for educational purposes.
