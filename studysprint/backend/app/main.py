from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

import app.ai.tools  # noqa: F401  (registers tools)
from app.ai.registry import registry
from app.ai.router import AIUnavailableError
from app.config import settings
from app.db import Base, SessionLocal, engine
from app.demo import SAMPLE_FILENAME, sample_pdf
from app.models import Course, User
from app.routers import ai, auth, courses, study
from app.security import hash_password
from app.services.ingest import IngestError
from app.services.scheduler import today_utc


def seed_demo() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.username == "demo")):
            return
        user = User(
            username="demo",
            email="demo@studysprint.dev",
            password_hash=hash_password("demopass123"),
        )
        db.add(user)
        db.flush()
        course = Course(
            owner_id=user.id,
            title="Operating Systems (demo)",
            exam_date=today_utc() + timedelta(days=10),
        )
        db.add(course)
        db.flush()
        registry.call(
            "ingest_document", db=db, course=course, filename=SAMPLE_FILENAME, data=sample_pdf()
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.seed_demo_user:
        seed_demo()
    yield


app = FastAPI(
    title="StudySprint API",
    version="1.0.0",
    description=(
        "Upload course PDFs; agents extract topics, write page-cited questions, grade free-text "
        "answers against the source and schedule weak topics first."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IngestError)
async def ingest_error(_: Request, exc: IngestError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(AIUnavailableError)
async def ai_unavailable(_: Request, exc: AIUnavailableError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": f"AI models unavailable: {exc}"})


for module in (auth, courses, study, ai):
    app.include_router(module.router, prefix="/api")


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


dist = settings.frontend_dist
if (dist / "index.html").is_file():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        target = (dist / path).resolve()
        if target.is_file() and Path(dist.resolve()) in target.parents:
            return FileResponse(target)
        return FileResponse(dist / "index.html")
