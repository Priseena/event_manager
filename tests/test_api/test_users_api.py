import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db  # ✅ Correct import path
from app.models.user_model import User


@pytest.fixture
async def client_with_db(db_session):
    """Creates an AsyncClient using the test database session."""
    app.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_user_registration_success(client_with_db, user_create_data):
    response = await client_with_db.post("/api/users/register", json=user_create_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_create_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_user_registration_invalid_email(client_with_db, user_base_data_invalid):
    data = {**user_base_data_invalid, "password": "SecurePassword123!"}
    response = await client_with_db.post("/api/users/register", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_login_success(client_with_db, verified_user):
    payload = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await client_with_db.post("/api/users/login", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_login_locked_user(client_with_db, locked_user):
    payload = {
        "username": locked_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await client_with_db.post("/api/users/login", data=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Account is locked."


@pytest.mark.asyncio
async def test_user_login_invalid_password(client_with_db, verified_user):
    payload = {
        "username": verified_user.email,
        "password": "WrongPassword123!"
    }
    response = await client_with_db.post("/api/users/login", data=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password."

