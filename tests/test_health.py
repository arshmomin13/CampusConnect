import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# An isolated in-memory database for tests.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    # Create a fresh schema before each test.
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def sample_event():
    return {
        "title": "Hackathon",
        "description": "Build something cool.",
        "date": "2026-11-15T10:00:00",
        "location": "Engineering Building",
        "category": "Technology",
        "source_url": "https://example.com/hackathon",
    }


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_event(client):
    response = client.post("/api/events", json=sample_event())

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hackathon"
    assert data["location"] == "Engineering Building"
    assert "id" in data


def test_list_events(client):
    client.post("/api/events", json=sample_event())

    response = client.get("/api/events")

    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["title"] == "Hackathon"


def test_get_event(client):
    create_response = client.post("/api/events", json=sample_event())
    event_id = create_response.json()["id"]

    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["id"] == event_id
    assert response.json()["title"] == "Hackathon"


def test_update_event(client):
    create_response = client.post("/api/events", json=sample_event())
    event_id = create_response.json()["id"]

    response = client.patch(
        f"/api/events/{event_id}",
        json={"title": "Updated Hackathon"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Hackathon"
    assert response.json()["description"] == "Build something cool."
    assert response.json()["location"] == "Engineering Building"


def test_delete_event(client):
    create_response = client.post("/api/events", json=sample_event())
    event_id = create_response.json()["id"]

    response = client.delete(f"/api/events/{event_id}")

    assert response.status_code in (200, 204)

    get_response = client.get(f"/api/events/{event_id}")
    assert get_response.status_code == 404


def test_get_missing_event_returns_404(client):
    response = client.get("/api/events/99999")
    assert response.status_code == 404


def test_delete_missing_event_returns_404(client):
    response = client.delete("/api/events/99999")
    assert response.status_code == 404


def test_search_events_by_title(client):
    client.post("/api/events", json=sample_event())

    another_event = sample_event()
    another_event["title"] = "Art Exhibition"
    another_event["category"] = "Arts"
    client.post("/api/events", json=another_event)

    response = client.get("/api/events", params={"q": "Hackathon"})

    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["title"] == "Hackathon"


def test_filter_events_by_category(client):
    client.post("/api/events", json=sample_event())

    another_event = sample_event()
    another_event["title"] = "Art Exhibition"
    another_event["category"] = "Arts"
    client.post("/api/events", json=another_event)

    response = client.get(
        "/api/events",
        params={"category": "Arts"},
    )

    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["title"] == "Art Exhibition"
