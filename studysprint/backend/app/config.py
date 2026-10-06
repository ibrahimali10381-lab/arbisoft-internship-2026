import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")


def _csv(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'studysprint.db'}")
    jwt_secret: str = os.getenv("JWT_SECRET", "studysprint-dev-secret-change-me")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
    cors_origins: list[str] = field(
        default_factory=lambda: _csv("CORS_ORIGINS", "http://localhost:5173")
    )
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    model_priority: list[str] = field(
        default_factory=lambda: _csv("MODEL_PRIORITY", "openai,groq,ollama,local-keyword")
    )
    seed_demo_user: bool = os.getenv("SEED_DEMO_USER", "true").lower() == "true"
    frontend_dist: Path = Path(
        os.getenv("FRONTEND_DIST", str(BACKEND_DIR.parent / "frontend" / "dist"))
    )


settings = Settings()
