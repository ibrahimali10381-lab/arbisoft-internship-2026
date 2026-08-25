from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_and_list_notes(client: TestClient) -> None:
    user_response = client.post(
        "/api/users",
        json={"username": "alice", "email": "alice@example.com"},
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    create_response = client.post(
        "/api/notes",
        json={
            "title": "First note",
            "content": "Hello from pytest",
            "owner_id": user_id,
        },
    )
    assert create_response.status_code == 201
    note = create_response.json()
    assert note["title"] == "First note"
    assert note["owner_id"] == user_id

    list_response = client.get("/api/notes")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_get_update_delete_note(client: TestClient) -> None:
    user_id = client.post(
        "/api/users",
        json={"username": "bob", "email": "bob@example.com"},
    ).json()["id"]

    note_id = client.post(
        "/api/notes",
        json={"title": "Draft", "content": "WIP", "owner_id": user_id},
    ).json()["id"]

    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Draft"

    update_response = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Published", "content": "Done"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Published"

    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 204

    missing = client.get(f"/api/notes/{note_id}")
    assert missing.status_code == 404


def test_create_note_validation_error(client: TestClient) -> None:
    user_id = client.post(
        "/api/users",
        json={"username": "carol", "email": "carol@example.com"},
    ).json()["id"]

    response = client.post(
        "/api/notes",
        json={"title": "", "content": "x", "owner_id": user_id},
    )
    assert response.status_code == 422


def test_create_note_missing_owner(client: TestClient) -> None:
    response = client.post(
        "/api/notes",
        json={"title": "Orphan", "content": "No owner", "owner_id": 999},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Owner user not found"


def test_duplicate_user_conflict(client: TestClient) -> None:
    payload = {"username": "dave", "email": "dave@example.com"}
    assert client.post("/api/users", json=payload).status_code == 201
    conflict = client.post("/api/users", json=payload)
    assert conflict.status_code == 409
