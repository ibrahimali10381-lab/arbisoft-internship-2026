import os
import tempfile
from pathlib import Path

_DB = Path(tempfile.mkdtemp()) / "test.db"
os.environ.update(
    {
        "DATABASE_URL": f"sqlite:///{_DB}",
        "SEED_DEMO_USER": "false",
        "MODEL_PRIORITY": "local-keyword",
        "JWT_SECRET": "test-secret-that-is-at-least-32-bytes-long",
    }
)
for key in ("OPENAI_API_KEY", "GROQ_API_KEY", "OLLAMA_BASE_URL"):
    os.environ.pop(key, None)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.ai.router import router as model_router  # noqa: E402
from app.ai.tracing import traces  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.demo import sample_pdf  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_state():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    model_router.clear_cache()
    traces.clear()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def register(client: TestClient, username: str = "alice") -> dict[str, str]:
    resp = client.post(
        "/api/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "password123"},
    )
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def auth(client):
    return register(client)


@pytest.fixture
def course_with_pdf(client, auth):
    course = client.post(
        "/api/courses", json={"title": "Operating Systems", "exam_date": "2099-01-10"}, headers=auth
    ).json()
    resp = client.post(
        f"/api/courses/{course['id']}/documents",
        files={"file": ("os.pdf", sample_pdf(), "application/pdf")},
        headers=auth,
    )
    assert resp.status_code == 201, resp.text
    return course["id"]
