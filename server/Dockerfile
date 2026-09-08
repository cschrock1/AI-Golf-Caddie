FROM python:3.11-slim

WORKDIR /app/server

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential libpq-dev gcc --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY server /app/server

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && if [ \"$APP_ENV\" = \"development\" ]; then python -m app.seed.seed; fi && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
