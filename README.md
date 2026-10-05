# AI Golf Caddie

AI Golf Caddie is a golf app for saving clubs and carry distances, exploring course data, logging shots, and getting club recommendations. It has a Vue web app, a FastAPI API, and a PostgreSQL database with PostGIS.

## Start the app on a new computer

You do not need Python, PostgreSQL, or the app's JavaScript/Python packages installed ahead of time. The first setup needs an internet connection so Docker, Node.js, and the project dependencies can be downloaded.

### What you need

- A Windows, macOS, or Linux computer with a supported 64-bit operating system. For a usable local development setup, allow roughly 8 GB of memory and several GB of free disk space for Docker images and packages.
- An internet connection for the initial installs and downloads.
- Docker Desktop on Windows or macOS (or Docker Engine with the Compose plugin on Linux).
- Node.js LTS, which includes npm.

If Docker Desktop asks to enable virtualization or install its system service, follow its setup prompts and restart the computer if requested. No Git installation is required if you download the project as a ZIP.

### 1. Get the project files

Download the project ZIP from its repository page and extract it. Open a terminal (PowerShell on Windows, Terminal on macOS/Linux) and change to the extracted `AI-Golf-Caddie` folder. For example:

```bash
cd path/to/AI-Golf-Caddie
```

### 2. Start the database and API

Make sure Docker is running, then run this from the project folder:

```bash
docker compose up --build
```

On the first run Docker downloads the database image and builds the API image, so it can take a few minutes. The API applies database migrations and loads the development seed data when it starts. Keep this terminal open while using the app.

### 3. Install and start the web app

Install Node.js LTS if it is not already installed. Open a second terminal in the project folder and run:

```bash
cd client
npm install
npm run dev
```

`npm install` downloads the web app packages the first time. Leave this terminal open too, then open <http://localhost:5173> in a browser.

### Useful local addresses

- Web app: <http://localhost:5173>
- API: <http://localhost:8000>
- Interactive API docs: <http://localhost:8000/docs>
- API health check: <http://localhost:8000/api/health>

To stop the web app, press `Ctrl+C` in its terminal. To stop the API and database, press `Ctrl+C` in the Docker terminal. Start again later with the same commands; Docker keeps the database in a named volume.

## Publish a free demo website

The included [`render.yaml`](render.yaml) describes a Render static site for the frontend and a Render Docker web service for the API. The database is hosted separately on Supabase because the app needs PostgreSQL with PostGIS. The free plans are suitable for a small demo, not a reliable production service: Render's free API sleeps when idle, and its free PostgreSQL database expires after 30 days. Supabase's free database can pause after inactivity and has a 500 MB database limit. Check the providers' current [Render free service limits](https://render.com/docs/free) and [Supabase pricing and limits](https://supabase.com/pricing) before relying on the site.

### 1. Put the code on GitHub

Create a GitHub repository and push this project to it. Keep `.env` out of the repository; it contains private settings. Render will read `render.yaml` from the repository when you create a Blueprint.

### 2. Create the hosted database

1. Create a Supabase project and save its database password somewhere private.
2. In Supabase, open **Database → Extensions**, find `postgis`, and enable it. The app's migrations create the database tables and also request PostGIS, but enabling it in the dashboard first avoids permission surprises.
3. Open **Connect** in the project dashboard and copy the **Session pooler** PostgreSQL connection string. Use the session pooler (not the transaction pooler) for this SQLAlchemy app.
4. For Render's `DATABASE_URL`, change the beginning of the copied URL from `postgresql://` to `postgresql+psycopg://`. Keep the host, port, database, and password from Supabase. If the URL does not specify TLS, add `?sslmode=require` (or `&sslmode=require` if it already has query parameters). URL-encode special characters in the password.

The Python dependencies include Psycopg 3, which is why the `+psycopg` driver name matters.

### 3. Create the Render services

1. Create a Render account and choose **New → Blueprint**. Connect the GitHub repository and deploy the Blueprint. It reads `render.yaml` and creates the API and static frontend services.
2. When prompted, enter the Supabase connection string as `DATABASE_URL`. Render generates `JWT_SECRET_KEY` for you.
3. Wait for both services to deploy. The API deployment applies database migrations. The API's health check is `https://ai-golf-caddie-api.onrender.com/api/health`.
4. Open the static site's URL, normally `https://ai-golf-caddie-web.onrender.com`, and register an account.

If Render assigns different service URLs, update `VITE_API_BASE_URL` on the static site to `<API URL>/api`, and update `CORS_ORIGINS` on the API to the exact frontend origin (scheme and hostname, with no trailing slash). Then redeploy both services so the frontend is rebuilt with the API URL and the backend accepts that site's requests.

### 4. Set optional integrations and protect secrets

- `DATABASE_URL`, `JWT_SECRET_KEY`, `GOLF_API_KEY`, and `OPENAI_API_KEY` belong only in the API service's Render environment settings. Do not expose them as `VITE_` variables.
- `VITE_MAPBOX_TOKEN` is included in the downloaded browser code by design. Use a public Mapbox token and restrict it to the deployed website's domain in Mapbox settings.
- The demo does not need Golf API, Mapbox, or OpenAI keys to deploy, but features that depend on them will be limited without those keys.

To enable an integration, open the matching Render service's **Environment** settings and add `GOLF_API_KEY` or `OPENAI_API_KEY` to the API service, or `VITE_MAPBOX_TOKEN` to the static site. After changing a `VITE_` value, trigger a new static-site deploy so it is embedded in the browser build.

Free services may sleep, restart, pause, or have limited backups and storage. Supabase free projects that are paused may need to be resumed in its dashboard. Back up any user data you care about before changing plans or deleting the database.

## Optional configuration

The app can start locally without configuring third-party API keys. Some features need their own configuration:

- Course search/data from the Golf API requires `GOLF_API_KEY`.
- Course maps require `VITE_MAPBOX_TOKEN`.
- AI-written recommendation explanations can use `OPENAI_API_KEY`; without it, the app uses its built-in explanation.
- Weather lookup uses Open-Meteo and needs an internet connection.

For local customization, copy `.env.example` to `.env` in the project root. The example uses the local Compose database URL. Keep secrets private and do not commit `.env`. Vite reads frontend `VITE_` values from this root `.env` file; restart the web dev server after changing them.

## Troubleshooting

- **`docker` is not recognized / command not found:** Install and start Docker Desktop, or install Docker Engine and the Compose plugin on Linux. Reopen the terminal after installation.
- **`npm` is not recognized / command not found:** Install Node.js LTS, then reopen the terminal.
- **Port 5173, 5432, or 8000 is already in use:** Stop the other program using that port, then retry.
- **The browser cannot reach the API:** Check that the Docker terminal shows the backend started successfully and that <http://localhost:8000/api/health> loads.
- **A mapped course or feature is missing:** The included course data is limited. Stonehenge Hole 1 is mapped; other holes are not synthesized. Some course data features also require a Golf API key.

## Project structure

```text
AI-Golf-Caddie/
├── client/              # Vue 3 + Vite web app
├── server/              # FastAPI API and database migrations
├── database/            # PostgreSQL/PostGIS initialization and seed SQL
├── docker-compose.yml   # Local database and API
├── .env.example         # Example environment settings
└── package.json
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
