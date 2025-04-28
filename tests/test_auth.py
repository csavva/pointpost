import pytest, asyncio
from httpx import AsyncClient
from fastapi import status

test_user = {
    "email": "user@exampler.com",
    "password": "password123",
}

@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """Test successful registration"""
    response = await async_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "User registered successfully"
    assert response.json()["user"]["email"] == test_user["email"]

@pytest.mark.asyncio
async def test_register_existing_email(async_client: AsyncClient):
    """Test registration with already registered email"""
    # First, register the user
    response = await async_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED

    # Then, try to register the same user again
    response = await async_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    """Test successful login"""
    # First, register the user
    response = await async_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED

    # Then, try to login
    response = await async_client.post("/auth/login", json=test_user)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    """Test login with invalid credentials"""
    # First, register the user
    response = await async_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED

    # Then, try to login with invalid credentials
    test_user["password"] = "<PASSWORD>"
    response = await async_client.post("/auth/login", json=test_user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_current_user_success(async_client: AsyncClient):
    """Test fetching current user with valid token"""
    # First, register the user
    response = await async_client.post("/auth/register", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED

    # Then, login to get the token
    response = await async_client.post("/auth/login", json=test_user)
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]

    # Now, use the token to get the current user
    response = await async_client.get(f"/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == test_user["email"]

    # Check if hashed_password is just asterisks, indicating it's not returned
    assert response.json().get("hashed_password") is None

@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(async_client: AsyncClient):
    """Test fetching current user without token"""
    # This test should fail because the user is not authenticated
    response = await async_client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]