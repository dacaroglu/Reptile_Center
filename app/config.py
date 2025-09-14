from pydantic_settings import BaseSettings
from pydantic import AnyUrl, Field

class Settings(BaseSettings):
    app_name: str = "HA Reptile Dashboard"
    # Simple API key for HA -> FastAPI pushes
    reptile_api_key: str = Field(..., alias="REPTILE_API_KEY")
    # SQLite by default; override with Postgres for production
    database_url: str = Field(default="sqlite:///./reptile.db", alias="DATABASE_URL")
    # CORS
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
