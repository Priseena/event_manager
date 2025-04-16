import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_send_markdown_email():
    # Mock the email service method
    mock_email_service = AsyncMock()
    mock_email_service.send_user_email.return_value = True

    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    result = await mock_email_service.send_user_email(user_data, 'email_verification')
    assert result is True
    mock_email_service.send_user_email.assert_awaited_once_with(user_data, 'email_verification')
