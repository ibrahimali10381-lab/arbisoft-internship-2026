from tests.conftest import register


def test_register_login_and_me(client):
    headers = register(client, "bob")
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["username"] == "bob"

    login = client.post("/api/auth/login", json={"username": "bob", "password": "password123"})
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "bob@example.com"


def test_duplicate_registration_rejected(client):
    register(client, "bob")
    resp = client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "other@example.com", "password": "password123"},
    )
    assert resp.status_code == 409


def test_register_validation(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "x", "email": "not-an-email", "password": "short"},
    )
    assert resp.status_code == 422


def test_bad_login_and_missing_or_invalid_token(client):
    register(client, "bob")
    assert (
        client.post(
            "/api/auth/login", json={"username": "bob", "password": "wrongpass"}
        ).status_code
        == 401
    )
    assert client.get("/api/auth/me").status_code == 401
    bad = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert bad.status_code == 401


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}
