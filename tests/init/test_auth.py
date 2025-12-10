import pytest


@pytest.mark.unit
def test_login_success(client):
    response = client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.unit
def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
