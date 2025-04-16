import pytest
from sqlalchemy import select
from unittest.mock import AsyncMock

from app.dependencies import get_settings
from app.models.user_model import User
from app.services.user_service import UserService

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_email_service():
    # Mock only the send_email method
    mock = AsyncMock()
    mock.send_email = AsyncMock(return_value=True)
    return mock

# Test creating a user with valid data
async def test_create_user_with_valid_data(db_session, mock_email_service):
    user_data = {
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
    }
    user = await UserService.create(db_session, user_data, mock_email_service)
    assert user is not None
    assert user.email == user_data["email"]

async def test_create_user_with_invalid_data(db_session, mock_email_service):
    user_data = {
        "nickname": "",
        "email": "invalidemail",
        "password": "short",
    }
    user = await UserService.create(db_session, user_data, mock_email_service)
    assert user is None

async def test_get_by_id_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_id(db_session, user.id)
    assert retrieved_user.id == user.id

async def test_get_by_id_user_does_not_exist(db_session):
    retrieved_user = await UserService.get_by_id(db_session, "non-existent-id")
    assert retrieved_user is None

async def test_get_by_nickname_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_nickname(db_session, user.nickname)
    assert retrieved_user.nickname == user.nickname

async def test_get_by_nickname_user_does_not_exist(db_session):
    retrieved_user = await UserService.get_by_nickname(db_session, "non_existent_nickname")
    assert retrieved_user is None

async def test_get_by_email_user_exists(db_session, user):
    retrieved_user = await UserService.get_by_email(db_session, user.email)
    assert retrieved_user.email == user.email

async def test_get_by_email_user_does_not_exist(db_session):
    retrieved_user = await UserService.get_by_email(db_session, "non_existent_email@example.com")
    assert retrieved_user is None

async def test_update_user_valid_data(db_session, user):
    new_email = "updated_email@example.com"
    updated_user = await UserService.update(db_session, user.id, {"email": new_email})
    assert updated_user is not None
    assert updated_user.email == new_email

async def test_update_user_invalid_data(db_session, user):
    updated_user = await UserService.update(db_session, user.id, {"email": "invalidemail"})
    assert updated_user is None

async def test_delete_user_exists(db_session, user):
    deletion_success = await UserService.delete(db_session, user.id)
    assert deletion_success is True

async def test_delete_user_does_not_exist(db_session):
    deletion_success = await UserService.delete(db_session, "non-existent-id")
    assert deletion_success is False

async def test_list_users_with_pagination(db_session, users_with_same_role_50_users):
    users_page_1 = await UserService.list_users(db_session, skip=0, limit=10)
    users_page_2 = await UserService.list_users(db_session, skip=10, limit=10)
    assert len(users_page_1) == 10
    assert len(users_page_2) == 10
    assert users_page_1[0].id != users_page_2[0].id

async def test_register_user_with_valid_data(db_session, mock_email_service):
    user_data = {
        "email": "register_valid_user@example.com",
        "password": "RegisterValid123!",
    }
    user = await UserService.register_user(db_session, user_data, mock_email_service)
    assert user is not None
    assert user.email == user_data["email"]

async def test_register_user_with_invalid_data(db_session, mock_email_service):
    user_data = {
        "email": "registerinvalidemail",
        "password": "short",
    }
    user = await UserService.register_user(db_session, user_data, mock_email_service)
    assert user is None

async def test_login_user_successful(db_session, verified_user):
    user_data = {
        "email": verified_user.email,
        "password": "MySuperPassword$1234",
    }
    logged_in_user = await UserService.login_user(db_session, user_data["email"], user_data["password"])
    assert logged_in_user is not None

async def test_login_user_incorrect_email(db_session):
    user = await UserService.login_user(db_session, "nonexistentuser@noway.com", "Password123!")
    assert user is None

async def test_login_user_incorrect_password(db_session, user):
    user = await UserService.login_user(db_session, user.email, "IncorrectPassword!")
    assert user is None

async def test_account_lock_after_failed_logins(db_session, verified_user):
    max_login_attempts = get_settings().max_login_attempts
    for _ in range(max_login_attempts):
        await UserService.login_user(db_session, verified_user.email, "wrongpassword")

    is_locked = await UserService.is_account_locked(db_session, verified_user.email)
    assert is_locked

async def test_reset_password(db_session, user):
    new_password = "NewPassword123!"
    reset_success = await UserService.reset_password(db_session, user.id, new_password)
    assert reset_success is True

async def test_verify_email_with_token(db_session, user):
    token = "valid_token_example"
    user.verification_token = token
    await db_session.commit()
    result = await UserService.verify_email_with_token(db_session, user.id, token)
    assert result is True

async def test_unlock_user_account(db_session, locked_user):
    unlocked = await UserService.unlock_user_account(db_session, locked_user.id)
    assert unlocked
    refreshed_user = await UserService.get_by_id(db_session, locked_user.id)
    assert not refreshed_user.is_locked
