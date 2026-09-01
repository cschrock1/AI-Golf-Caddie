# PostgreSQL + PostGIS (Local Development)

This directory includes initialization SQL and notes for running a local PostgreSQL database with PostGIS enabled.

Quick start (Docker):

```bash
docker compose up --build db
```

This will start a Postgres container with PostGIS. The `database/init` folder is mounted into the container's `docker-entrypoint-initdb.d` so the `01-enable-postgis.sql` script runs on first initialization.

Connection info (from `.env.example`):

- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DATABASE_URL (example): postgresql+psycopg://golf_user:change_me@db:5432/ai_golf_caddie

Notes:

- For production, do not run initialization SQL in this way; use migrations and careful upgrade paths (e.g., Alembic).
- Ensure backups and migrations are in place before altering spatial tables in production.
