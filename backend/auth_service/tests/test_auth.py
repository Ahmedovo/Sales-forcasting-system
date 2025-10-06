import os
import pytest
from app import create_app


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    monkeypatch.setenv("DB_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("DB_SCHEMA", "")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "testsecret")


@pytest.fixture
def client():
    app = create_app()
    app.config.update({"TESTING": True})
    return app.test_client()


def test_register_and_login_and_me(client):
    # register
    r = client.post("/api/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "pass1234",
        "role": "admin",
    })
    assert r.status_code == 201, r.data

    # login
    r = client.post("/api/auth/login", json={
        "email": "alice@example.com",
        "password": "pass1234",
    })
    assert r.status_code == 200, r.data
    access = r.get_json()["access_token"]
    refresh = r.get_json()["refresh_token"]

    # me
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    assert r.get_json()["email"] == "alice@example.com"

    # refresh
    r = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    assert "access_token" in r.get_json()
