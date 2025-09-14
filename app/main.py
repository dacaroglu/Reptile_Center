from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .routers import ingest, terrariums, health

def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(terrariums.router)
    return app

app = create_app()

# Ensure tables exist on first run
try:
    init_db()
except Exception:
    # Avoid crashing in read-only environments; handle via CLI if needed
    pass
