# File: stock_market_game/tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_stocks():
    response = client.get("/stocks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Additional assertions can be added.

def test_get_account():
    response = client.get("/accounts/1")
    assert response.status_code == 200
    data = response.json()
    assert "cash" in data

def test_get_leaderboard():
    response = client.get("/leaderboard/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_orderbook():
    response = client.get("/orderbook/")
    assert response.status_code == 200
    data = response.json()
    assert "bids" in data and "asks" in data
