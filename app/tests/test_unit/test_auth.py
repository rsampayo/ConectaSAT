"""Unit tests for authentication utilities."""

from datetime import timedelta
from unittest.mock import patch

from app.core.auth import (
    create_access_token,
    get_token_data,
    get_user_id_from_token_data,
)


def test_create_access_token():
    """Test creation of an access token."""
    # Test with default expiration
    with patch("app.core.auth.create_token") as mock_create_token:
        mock_create_token.return_value = "dummy-token"
        token = create_access_token(user_id=1)

        # Verify create_token was called
        mock_create_token.assert_called_once()
        # Extract the arguments
        args, _ = mock_create_token.call_args
        token_data, expires_delta = args

        # Check token data
        assert token_data["sub"] == "1"
        assert token_data["type"] == "access"
        # Check that the returned value matches
        assert token == "dummy-token"


def test_create_access_token_with_custom_expiration():
    """Test creation of an access token with custom expiration."""
    # Test with custom expiration
    custom_exp = timedelta(minutes=30)

    with patch("app.core.auth.create_token") as mock_create_token:
        mock_create_token.return_value = "dummy-token"
        create_access_token(user_id=1, expires_delta=custom_exp)

        # Verify create_token was called
        mock_create_token.assert_called_once()
        # Extract the arguments
        args, _ = mock_create_token.call_args
        token_data, expires_delta = args

        # Check that expires_delta is correctly passed
        assert expires_delta == custom_exp


def test_get_token_data():
    """Test decoding a JWT token."""
    # Mocked decoded data
    mock_decoded = {"sub": "1", "type": "access", "exp": 1609459200}

    # Test token decoding
    with patch("app.core.auth.jwt.decode", return_value=mock_decoded) as mock_decode:
        result = get_token_data("dummy.token.string")

        # Verify jwt.decode was called with the right arguments
        mock_decode.assert_called_once()
        assert result == mock_decoded


def test_get_user_id_from_token_data():
    """Test extracting user ID from token data."""
    # Test with valid token data
    token_data = {"sub": "123", "type": "access"}
    user_id = get_user_id_from_token_data(token_data)

    assert user_id == 123

    # Test with float value in string
    token_data = {"sub": "456", "type": "access"}
    user_id = get_user_id_from_token_data(token_data)

    assert user_id == 456
