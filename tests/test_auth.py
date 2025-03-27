from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# test with valid  credentials.
def test_get_account_valid_credentials():
    response = client.get("/accounts/1000", auth=("1000", "securepassword"))
    assert response.status_code == 200
    # Optionally, verify content in response.json()

# test with invalid credentials.
def test_get_account_invalid_credentials():
    response = client.get("/accounts/1000", auth=("1000", "wrongpassword"))
    assert response.status_code == 401

# test with missing credentials.
def test_get_account_wrong_user():
    # If user 123 is valid but you try to access a different user's account (e.g., 456)
    response = client.get("/accounts/456", auth=("123", "yourpassword"))
    assert response.status_code == 403
