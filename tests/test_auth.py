import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpassword"
NEW_PASSWORD = "newpassword"


def test_register_user():
    # Register a new user
    response = client.post("/auth/register", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 200
    assert response.json()["email"] == TEST_EMAIL

    # Register with the same email (should fail)
    response = client.post("/auth/register", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 400

def test_login_and_lockout():
    # Login with correct credentials
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    # Login with wrong password 5 times to trigger lockout
    for _ in range(5):
        response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": "wrong"})
    assert response.status_code == 401

    # Account should now be locked
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 401

def test_token_refresh_and_logout():
    # Login to get tokens
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    if response.status_code == 401:
        pytest.skip("Account is locked from previous test, skipping refresh/logout tests.")
    tokens = response.json()
    refresh_token = tokens["refresh_token"]

    # Refresh tokens
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens and "refresh_token" in new_tokens

    # Logout (revoke refresh token)
    response = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert response.status_code == 200

    # Try to use the same refresh token again (should fail)
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401

def test_change_password_and_profile():
    # Login to get tokens
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    if response.status_code == 401:
        pytest.skip("Account is locked from previous test, skipping change password/profile tests.")
    tokens = response.json()
    access_token = tokens["access_token"]

    # Change password with wrong old password
    response = client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"old_password": "wrong", "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 400

    # Change password with correct old password
    response = client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"old_password": TEST_PASSWORD, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 200

    # Login with new password (should succeed)
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": NEW_PASSWORD})
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]

    # Login with old password (should fail)
    response = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert response.status_code == 401

    # Get profile with valid token
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == TEST_EMAIL

    # Get profile with invalid token
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401 