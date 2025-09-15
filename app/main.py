from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import sse 
from .config import settings
from .database import init_db
from .routers import ingest, terrariums, health,ui,admin

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
    app.include_router(ui.router)
    app.include_router(sse.router)
    app.include_router(admin.router)

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    return app

app = create_app()

try:
    init_db()
except Exception:
    pass
