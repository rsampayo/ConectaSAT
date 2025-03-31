"""Unit tests for security functions."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.core.security import (
    authenticate_admin,
    create_api_token,
    create_token,
    get_password_hash,
    verify_api_token,
    verify_password,
)
from app.models.user import APIToken, SuperAdmin


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_admin():
    """Mock admin user."""
    admin = MagicMock(spec=SuperAdmin)
    admin.username = "testadmin"
    admin.hashed_password = get_password_hash("testpassword")
    admin.is_active = True
    return admin


@pytest.fixture
def mock_token():
    """Mock API token."""
    token = MagicMock(spec=APIToken)
    token.token = "test-token-123"
    token.is_active = True
    return token


def test_create_token():
    """Test token creation with and without expiration."""
    # Test with default expiration
    data = {"sub": "test-user"}
    token = create_token(data)
    assert isinstance(token, str)
    assert len(token) > 0

    # Test with custom expiration
    expires = timedelta(minutes=30)
    token_with_exp = create_token(data, expires)
    assert isinstance(token_with_exp, str)
    assert len(token_with_exp) > 0


def test_verify_password():
    """Test password verification."""
    # Generate a hash
    hashed = get_password_hash("testpassword")

    # Verify correct password
    assert verify_password("testpassword", hashed) is True

    # Verify incorrect password
    assert verify_password("wrongpassword", hashed) is False


def test_get_password_hash():
    """Test password hashing."""
    # Hash a password
    hashed = get_password_hash("testpassword")

    # Ensure it returns a string
    assert isinstance(hashed, str)

    # Ensure it's not the original password
    assert hashed != "testpassword"

    # Ensure two hashes of the same password are different
    hashed2 = get_password_hash("testpassword")
    assert hashed != hashed2

    # But both should verify against the original password
    assert verify_password("testpassword", hashed)
    assert verify_password("testpassword", hashed2)


def test_authenticate_admin_valid(mock_db, mock_admin):
    """Test admin authentication with valid credentials."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin

    # Test with correct password
    with patch("app.core.security.verify_password", return_value=True):
        result = authenticate_admin(mock_db, "testadmin", "testpassword")

    # Should return the admin
    assert result == mock_admin


def test_authenticate_admin_invalid_password(mock_db, mock_admin):
    """Test admin authentication with invalid password."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin

    # Test with wrong password
    with patch("app.core.security.verify_password", return_value=False):
        result = authenticate_admin(mock_db, "testadmin", "wrongpassword")

    # Should return None
    assert result is None


def test_authenticate_admin_inactive(mock_db, mock_admin):
    """Test authentication with an inactive admin account."""
    # Setup
    mock_admin.is_active = False
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin

    # Test with correct password but inactive account
    with patch("app.core.security.verify_password", return_value=True):
        result = authenticate_admin(mock_db, "testadmin", "testpassword")

    # Should return None
    assert result is None


def test_authenticate_admin_not_found(mock_db):
    """Test authentication with a non-existent admin username."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Test with non-existent username
    result = authenticate_admin(mock_db, "nonexistent", "anypassword")

    # Should return None
    assert result is None


def test_verify_api_token_valid(mock_db, mock_token):
    """Test verification of a valid API token."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_token

    # Test verification
    result = verify_api_token(mock_db, "test-token-123")

    # Should return True
    assert result is True


def test_verify_api_token_invalid(mock_db):
    """Test verification of an invalid API token."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Test verification
    result = verify_api_token(mock_db, "invalid-token")

    # Should return False
    assert result is False


def test_verify_api_token_inactive(mock_db):
    """Test verification of an inactive API token."""
    # Setup - The query should filter for active tokens, so we return None
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Test verification
    result = verify_api_token(mock_db, "test-token-123")

    # Should return False
    assert result is False


def test_create_api_token(mock_db):
    """Test creation of a new API token."""
    # Setup
    description = "Test token description"

    # Mock the secrets module
    with patch("secrets.token_urlsafe", return_value="new-token-456"):
        create_api_token(mock_db, description)

    # Should call db methods
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called

    # Should have created a token with the right values
    args, _ = mock_db.add.call_args
    created_token = args[0]
    assert created_token.token == "new-token-456"
    assert created_token.description == description
