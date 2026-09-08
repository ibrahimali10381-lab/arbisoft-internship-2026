from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.agent.memory import memory_store
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
    memory_store.clear("test-session")
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _register(client: TestClient, username: str, email: str, password: str = "secret12"):
    return client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client: TestClient) -> None:
    register = _register(client, "alice", "alice@example.com")
    assert register.status_code == 201
    assert register.json()["access_token"]
    assert register.json()["user"]["role"] == "user"

    bad_login = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "wrongpass"},
    )
    assert bad_login.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "secret12"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["username"] == "alice"


def test_notes_require_auth(client: TestClient) -> None:
    response = client.get("/api/notes")
    assert response.status_code == 401


def test_authenticated_note_crud(client: TestClient) -> None:
    token = _register(client, "bob", "bob@example.com").json()["access_token"]
    headers = _auth_header(token)

    create = client.post(
        "/api/notes",
        headers=headers,
        json={"title": "First note", "content": "Hello from pytest"},
    )
    assert create.status_code == 201
    note_id = create.json()["id"]

    listed = client.get("/api/notes", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(
        f"/api/notes/{note_id}",
        headers=headers,
        json={"title": "Updated", "content": "Changed"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"

    deleted = client.delete(f"/api/notes/{note_id}", headers=headers)
    assert deleted.status_code == 204


def test_validation_and_not_found_errors(client: TestClient) -> None:
    token = _register(client, "carol", "carol@example.com").json()["access_token"]
    headers = _auth_header(token)

    invalid = client.post(
        "/api/notes",
        headers=headers,
        json={"title": "", "content": "x"},
    )
    assert invalid.status_code == 422

    missing = client.get("/api/notes/999", headers=headers)
    assert missing.status_code == 404


def test_rbac_user_cannot_list_all_users(client: TestClient) -> None:
    token = _register(client, "dave", "dave@example.com").json()["access_token"]
    response = client.get("/api/users", headers=_auth_header(token))
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin role required"


def test_rbac_cannot_delete_another_users_note(client: TestClient) -> None:
    owner_token = _register(client, "owner1", "owner1@example.com").json()["access_token"]
    other_token = _register(client, "other1", "other1@example.com").json()["access_token"]

    note_id = client.post(
        "/api/notes",
        headers=_auth_header(owner_token),
        json={"title": "Private", "content": "Only mine"},
    ).json()["id"]

    forbidden = client.delete(
        f"/api/notes/{note_id}",
        headers=_auth_header(other_token),
    )
    assert forbidden.status_code == 403


def test_integration_happy_path_auth_crud(client: TestClient) -> None:
    """End-to-end happy path: register → login → CRUD → me."""
    register = _register(client, "erin", "erin@example.com", password="happy123")
    assert register.status_code == 201

    login = client.post(
        "/api/auth/login",
        json={"username": "erin", "password": "happy123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = _auth_header(token)

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["username"] == "erin"

    created = client.post(
        "/api/notes",
        headers=headers,
        json={"title": "Ship it", "content": "Integration path works"},
    )
    assert created.status_code == 201
    note_id = created.json()["id"]

    fetched = client.get(f"/api/notes/{note_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["content"] == "Integration path works"

    client.put(
        f"/api/notes/{note_id}",
        headers=headers,
        json={"content": "Updated on happy path"},
    )
    listed = client.get("/api/notes", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["content"] == "Updated on happy path"

    assert client.delete(f"/api/notes/{note_id}", headers=headers).status_code == 204


def test_research_agent_uses_memory(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)

    token = _register(client, "frank", "frank@example.com").json()["access_token"]
    headers = _auth_header(token)
    session_id = "test-session"

    remember = client.post(
        "/api/agent/memory",
        headers=headers,
        json={
            "session_id": session_id,
            "fact": "The user's favorite topic is renewable energy",
        },
    )
    assert remember.status_code == 200
    assert any("renewable energy" in fact for fact in remember.json()["facts"])

    first = client.post(
        "/api/agent/research",
        headers=headers,
        json={"query": "solar panel efficiency", "session_id": session_id},
    )
    assert first.status_code == 200
    body = first.json()
    assert body["plan"]
    assert body["sources"]
    assert any("renewable energy" in fact for fact in body["memory_used"])

    second = client.post(
        "/api/agent/research",
        headers=headers,
        json={"query": "battery storage trends", "session_id": session_id},
    )
    assert second.status_code == 200
    assert any("solar panel efficiency" in fact for fact in second.json()["memory_used"])


def test_supervisor_routes_to_multiple_workers(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    from app.agent.tracing import trace_store

    trace_store.clear()
    token = _register(client, "gina", "gina@example.com").json()["access_token"]
    headers = _auth_header(token)

    client.post(
        "/api/notes",
        headers=headers,
        json={"title": "MCP notes", "content": "Remember to wire the search tool"},
    )

    response = client.post(
        "/api/orchestration/supervise",
        headers=headers,
        json={
            "query": "search notes about MCP and research latest MCP news",
            "session_id": "orch-test",
            "file_path": "internship-brief.txt",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["route"]) >= 2
    assert len(body["handoffs"]) >= 2
    assert body["traces"]
    assert any(event["phase"] == "pre" for event in body["traces"])
    assert any(event["phase"] == "post" for event in body["traces"])


def test_multi_hop_and_file_plugin(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    token = _register(client, "hank", "hank@example.com").json()["access_token"]
    headers = _auth_header(token)

    response = client.post(
        "/api/orchestration/multi-hop",
        headers=headers,
        json={
            "question": "What should Phase 3 focus on for NotesLab?",
            "session_id": "multi-test",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "file-read" in " ".join(body["steps"]).lower() or any(
        "brief" in step.lower() for step in body["steps"]
    )
    assert body["answer"]
    assert body["traces"]


def test_trace_listing(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    from app.agent.tracing import trace_store

    trace_store.clear()
    token = _register(client, "ivy", "ivy@example.com").json()["access_token"]
    headers = _auth_header(token)
    client.post(
        "/api/orchestration/multi-hop",
        headers=headers,
        json={"question": "summarize internship brief goals", "session_id": "trace-test"},
    )
    traces = client.get("/api/orchestration/traces", headers=headers)
    assert traces.status_code == 200
    assert len(traces.json()["events"]) >= 2
