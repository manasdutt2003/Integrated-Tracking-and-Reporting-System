"""Tests for the Flask app. No network access or real credentials are used."""

import sys
import types
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as app_module  # noqa: E402


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(app_module, "USERS", {"user1": generate_password_hash("pw")})
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


@pytest.mark.parametrize("path", ["/home", "/about", "/services", "/search", "/chat", "/feedback", "/login"])
def test_public_pages_render(client, path):
    assert client.get(path).status_code == 200


def test_root_redirects_home(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/home")


def test_buses_api_returns_all_without_query(client):
    data = client.get("/api/buses").get_json()
    assert len(data) == len(app_module.BUSES)


def test_buses_api_filters_by_query(client):
    data = client.get("/api/buses?q=redhills").get_json()
    assert data
    assert all(bus["route"] == "Redhills" for bus in data)


def test_search_buses_matches_vehicle_and_route_number():
    buses = [
        {"route_number": "2", "route": "A", "vehicle_number": "TN 1", "tracking_link": None},
        {"route_number": "3", "route": "B", "vehicle_number": "TN 2", "tracking_link": None},
    ]
    assert app_module.search_buses(buses, "tn 2") == [buses[1]]
    assert app_module.search_buses(buses, "2") == buses
    assert app_module.search_buses(buses, "zzz") == []
    assert app_module.search_buses(buses, "  ") == buses


def test_validate_buses_rejects_bad_data():
    with pytest.raises(ValueError):
        app_module.validate_buses({})
    with pytest.raises(ValueError):
        app_module.validate_buses([{"route_number": "1"}])
    assert app_module.validate_buses([]) == []


def test_login_success_and_logout(client):
    response = client.post("/login", data={"username": "user1", "password": "pw"})
    assert response.status_code == 302
    assert client.get("/profile").status_code == 200
    client.get("/logout")
    assert client.get("/profile").status_code == 302


def test_login_failure(client):
    response = client.post("/login", data={"username": "user1", "password": "wrong"})
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


def test_profile_requires_login(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_send_notification_rejects_bad_email(client, monkeypatch):
    calls = []
    monkeypatch.setattr(app_module, "send_email_notification", lambda *a: calls.append(a) or True)
    client.post("/send_notification", data={"email": "not-an-email"})
    assert calls == []


def test_send_notification_sends_for_valid_email(client, monkeypatch):
    calls = []
    monkeypatch.setattr(app_module, "send_email_notification", lambda *a: calls.append(a) or True)
    client.post("/send_notification", data={"email": "a@b.co"})
    assert len(calls) == 1
    assert calls[0][0] == "a@b.co"


def test_chat_rejects_empty_and_long_messages(client):
    assert client.post("/api/chat", json={"message": "  "}).status_code == 400
    too_long = "x" * (app_module.MAX_CHAT_MESSAGE_LENGTH + 1)
    assert client.post("/api/chat", json={"message": too_long}).status_code == 400


def test_chat_without_api_key_returns_503(client):
    assert client.post("/api/chat", json={"message": "hi"}).status_code == 503


def test_chat_hides_internal_errors(client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake")

    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail")

    fake_genai = types.SimpleNamespace(configure=boom, GenerativeModel=boom)
    google = types.ModuleType("google")
    google.generativeai = fake_genai
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.generativeai", fake_genai)

    response = client.post("/api/chat", json={"message": "hi"})
    assert response.status_code == 502
    assert b"secret internal detail" not in response.data
