import decimal
import pytest
from fastapi.testclient import TestClient
from app import app, Bet, BetStatus # Adjust the import based on your file structure
from database import init_db, SessionLocal, Bet as BetModel

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
    db.query(BetModel).delete()  # Clear the Event table
    db.commit()
    db.close()

def test_get_bets(test_app):
    response = test_app.get('/bets')
    assert response.status_code == 200
