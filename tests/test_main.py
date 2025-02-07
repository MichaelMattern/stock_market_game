# File: stock_market_game/tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    # No root endpoint is defined, so expect a 404.
    response = client.get("/")
    assert response.status_code == 404
