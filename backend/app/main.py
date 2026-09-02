from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.models import User
from app.routers import agent, auth, notes, users
from app.security import hash_password

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def seed_default_users() -> None:
    db = SessionLocal()
    try:
        seeds = [
            ("demo", "demo@example.com", "demopass", "user"),
            ("admin", "admin@example.com", "adminpass", "admin"),
        ]
        for username, email, password, role in seeds:
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                continue
            db.add(
                User(
                    username=username,
                    email=email,
                    password_hash=hash_password(password),
                    role=role,
                )
            )
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_default_users()
    yield


app = FastAPI(
    title="NotesLab API",
    description="Auth, notes CRUD, and SerpAPI research agent for Arbisoft Internship 2026",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(agent.router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
