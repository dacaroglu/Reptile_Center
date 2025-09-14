# HA → FastAPI Reptile Dashboard (Skeleton)

A production-ready **skeleton** for pushing sensor data from your **local Home Assistant OS (HAOS)** (running on your Lenovo ThinkCentre M700) to a **FastAPI** service running on **AWS Lightsail**.

**Design (push-first):**
- HA is on your LAN and **not publicly reachable**. So, **HA pushes** to your Lightsail API when sensor values change.
- FastAPI stores readings and serves a simple JSON API for your future dashboard.
- Auth uses an `X-API-Key` header (keep it secret in HA secrets). Run FastAPI over HTTPS (use Nginx/Caddy + Let's Encrypt).

**What’s included:**
- Minimal FastAPI app with `/api/v1/ingest` to receive readings, `/api/v1/summary` to return latest temp/humidity per terrarium, and `/api/v1/readings` for timeseries.
- SQLAlchemy models for `Terrarium` and `Reading` (SQLite by default; swap to Postgres via `DATABASE_URL`).
- Simple API-key dependency.
- Example Home Assistant YAML for `rest_command` + `automation` to push readings.

## Quickstart (local/dev)

```bash
python -m venv .venv
source .venv/bin/activate  # (Windows) .venv\Scripts\activate
pip install -r requirements.txt

# Create .env from example and set values
cp .env.example .env
# Edit .env: REPTILE_API_KEY=super-secret-key

# Initialize DB (SQLite by default)
python -c "from app.database import init_db; init_db()"

# Run
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs to test.

## Deploy on Lightsail (outline)
1. Create Ubuntu instance (2 vCPU / 4GB is plenty for this).
2. Install system packages and Python 3.11+.
3. Clone this project, create `.env` (put your real `REPTILE_API_KEY`), and initialize DB (or point `DATABASE_URL` to Postgres).
4. Run behind **Caddy** or **Nginx** with HTTPS and a systemd service (gunicorn+uvicorn workers).
5. Lock down firewall to only allow 80/443 (and optionally restrict `/api/v1/ingest` by IP allowlist).

## Home Assistant (push) — example

Two steps:

1) **`rest_command:`** — one reusable service that posts to Lightsail.
2) **`automation:`** — triggers on sensor state change and calls the command with templated data.

> Replace entity IDs with your real ones for each terrarium.

See `sample_ha/ha_rest_command.yaml` and `sample_ha/ha_automations.yaml` for copy‑pasteable snippets.

## API

- `POST /api/v1/ingest` — Body: `{"terrarium_slug": "...","sensor_type": "temperature|humidity","value": 25.4,"unit": "°C","entity_id":"sensor.x","ts":"2025-09-14T16:00:00Z"}`
- `GET /api/v1/summary` — Latest temp/humidity per terrarium.
- `GET /api/v1/readings?terrarium=gecko-1&hours=24` — Timeseries for last N hours.

## Swap DB to Postgres

In `.env`, set:

```
DATABASE_URL=postgresql+psycopg2://USER:PASS@HOST:5432/DBNAME
```

Re-run `init_db()` once on the target DB (or manage with Alembic later).

---

**Next steps you can add:**
- JWT or HMAC signing if you want stronger auth than API key.
- Rate limiting / IP allowlist on ingest.
- A small React/Vite dashboard (or integrate with your existing frontend).
