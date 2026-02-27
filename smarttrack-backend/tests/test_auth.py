import pytest
import uuid

@pytest.mark.asyncio
async def test_register_and_login(client):
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    password = "password123"
    full_name = "Test User"

    # 1. Register
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name}
    )
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # 2. Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."
