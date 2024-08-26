import decimal
from time import time
import pytest
from fastapi.testclient import TestClient
from app import app, EventState, Event  # Adjust the import based on your file structure
from database import init_db, SessionLocal, Event as EventModel

# Initialize the database for testing
@pytest.fixture(scope="module")
def test_app():
    init_db()  # Initialize the database
    client = TestClient(app)
    yield client

@pytest.fixture(scope="function", autouse=True)
def clear_db():
    yield
    # Clear the database before each test
    db = SessionLocal()
    db.query(EventModel).delete()  # Clear the Event table
    db.commit()
    db.close()



def test_create_event(test_app):
    response = test_app.put("/event", json={
        "event_id": "event_1",
        "coefficient": str(decimal.Decimal("1.5")),
        "deadline": 1700000000,  # Example timestamp
        "state": EventState.NEW.value
    })
    assert response.status_code == 200
    assert response.json()["event_id"] == "event_1"

def test_get_event(test_app):
    # First create an event
    test_app.put("/event", json={
        "event_id": "event_2",
        "coefficient": str(decimal.Decimal("2.0")),
        "deadline": 1700000000,
        "state": EventState.NEW.value
    })

    response = test_app.get("/event/event_2")
    assert response.status_code == 200
    assert response.json()["event_id"] == "event_2"

def test_update_event(test_app):
    # Create an event to update
    test_app.put("/event", json={
        "event_id": "event_3",
        "coefficient": str(decimal.Decimal("2.5")),
        "deadline": 1700000000,
        "state": EventState.NEW.value
    })

    response = test_app.put("/events/event_3", json={
        "state": EventState.FINISHED_WIN.value
    })
    assert response.status_code == 200
    assert response.json()["state"] == EventState.FINISHED_WIN.value

def test_get_events(test_app):
    # Create multiple events
    test_app.put("/event", json={
        "event_id": "event_4",
        "coefficient": str(decimal.Decimal("3.0")),
        "deadline": int(time())+1000,
        "state": EventState.NEW.value
    })
    test_app.put("/event", json={
        "event_id": "event_5",
        "coefficient": str(decimal.Decimal("4.0")),
        "deadline": int(time())+1000,
        "state": EventState.NEW.value
    })

    response = test_app.get("/events")
    assert response.status_code == 200
    assert len(response.json()) >= 2  # Ensure we have at least 2 events

if __name__ == "__main__":
    pytest.main()
