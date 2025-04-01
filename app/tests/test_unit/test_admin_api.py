"""Unit tests for the admin API endpoints."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.admin import (
    create_api_token_endpoint,
    create_new_superadmin_endpoint,
    deactivate_admin_account_endpoint,
    delete_api_token_endpoint,
    get_api_token_endpoint,
    list_api_tokens_endpoint,
    regenerate_api_token_endpoint,
    update_admin_password_endpoint,
    update_api_token_endpoint,
)
from app.models.user import APIToken, SuperAdmin
from app.schemas.auth import (
    SuperAdminCreate,
    SuperAdminUpdate,
    TokenCreate,
    TokenResponse,
    TokenUpdate,
)


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_admin():
    """Mock admin user for dependency injection."""
    admin = MagicMock(spec=SuperAdmin)
    admin.username = "testadmin"
    admin.is_active = True
    return admin


@pytest.fixture
def mock_token():
    """Mock API token for testing."""
    token = MagicMock(spec=APIToken)
    token.id = 1
    token.token = "test-token-123"
    token.description = "Test token"
    token.is_active = True
    token.created_at = "2023-01-01T00:00:00"
    token.updated_at = "2023-01-01T00:00:00"
    return token


async def test_create_api_token_endpoint(mock_db, mock_admin, mock_token):
    """Test creating a new API token."""
    # Setup
    token_data = TokenCreate(description="Test token")

    # Mock the security function that creates a token
    with patch("app.api.admin.create_api_token", return_value=mock_token):
        # Call the endpoint
        result = await create_api_token_endpoint(token_data, mock_db, mock_admin)

    # Assertions
    assert result.token == mock_token.token
    assert result.description == mock_token.description
    assert result.is_active == mock_token.is_active


async def test_list_api_tokens_endpoint(mock_db, mock_admin, mock_token):
    """Test listing API tokens."""
    # Setup
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_offset = mock_filter.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = [mock_token]
    mock_db.query.return_value.count.return_value = 1

    # Configure the mock token with attributes needed for TokenResponse
    mock_token.id = 1
    mock_token.token = "test-token"
    mock_token.description = "Test token"
    mock_token.is_active = True
    mock_token.created_at = datetime.now()
    mock_token.updated_at = datetime.now()

    # Call the endpoint with patched list_api_tokens_endpoint
    with patch("app.api.admin.TokenResponse") as mock_token_response:
        # Setup the mock to return a proper token response
        mock_token_response.return_value = TokenResponse(
            id=mock_token.id,
            token=mock_token.token,
            description=mock_token.description,
            is_active=mock_token.is_active,
            created_at=mock_token.created_at,
            updated_at=mock_token.updated_at,
        )

        result = await list_api_tokens_endpoint(0, 100, mock_db, mock_admin)

    # Assertions
    assert result.total == 1
    assert len(result.tokens) == 1


async def test_get_api_token_endpoint(mock_db, mock_admin, mock_token):
    """Test getting a specific API token."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_token

    # Call the endpoint
    result = await get_api_token_endpoint(1, mock_db, mock_admin)

    # Assertions
    assert result.id == mock_token.id
    assert result.token == mock_token.token


async def test_get_api_token_endpoint_not_found(mock_db, mock_admin):
    """Test getting a non-existent API token raises 404."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Call the endpoint and check for exception
    with pytest.raises(HTTPException) as exc_info:
        await get_api_token_endpoint(999, mock_db, mock_admin)

    # Assertions
    assert exc_info.value.status_code == 404
    assert "Token not found" in exc_info.value.detail


async def test_update_api_token_endpoint(mock_db, mock_admin, mock_token):
    """Test updating an API token."""
    # Setup
    token_data = TokenUpdate(description="Updated token", is_active=False)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_token

    # Call the endpoint
    await update_api_token_endpoint(token_data, 1, mock_db, mock_admin)

    # Assertions
    assert mock_token.description == "Updated token"
    assert mock_token.is_active is False
    assert mock_db.commit.called
    assert mock_db.refresh.called


async def test_update_api_token_endpoint_not_found(mock_db, mock_admin):
    """Test updating a non-existent API token raises 404."""
    # Setup
    token_data = TokenUpdate(description="Updated token")
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Call the endpoint and check for exception
    with pytest.raises(HTTPException) as exc_info:
        await update_api_token_endpoint(token_data, 999, mock_db, mock_admin)

    # Assertions
    assert exc_info.value.status_code == 404
    assert "Token not found" in exc_info.value.detail


async def test_delete_api_token_endpoint(mock_db, mock_admin, mock_token):
    """Test deleting an API token."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_token

    # Call the endpoint
    result = await delete_api_token_endpoint(1, mock_db, mock_admin)

    # Assertions
    assert mock_db.delete.called
    assert mock_db.commit.called
    assert "successfully deleted" in result.message


async def test_delete_api_token_endpoint_not_found(mock_db, mock_admin):
    """Test deleting a non-existent API token raises 404."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Call the endpoint and check for exception
    with pytest.raises(HTTPException) as exc_info:
        await delete_api_token_endpoint(999, mock_db, mock_admin)

    # Assertions
    assert exc_info.value.status_code == 404
    assert "Token not found" in exc_info.value.detail


async def test_regenerate_api_token_endpoint(mock_db, mock_admin, mock_token):
    """Test regenerating an API token."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_token

    # Call the endpoint
    with patch("secrets.token_urlsafe", return_value="new-token-456"):
        await regenerate_api_token_endpoint(1, mock_db, mock_admin)

    # Assertions
    assert mock_token.token == "new-token-456"
    assert mock_db.commit.called
    assert mock_db.refresh.called


async def test_create_new_superadmin_endpoint(mock_db, mock_admin):
    """Test creating a new superadmin."""
    # Setup
    admin_data = SuperAdminCreate(
        username="newadmin", password="password123", full_name="New Admin"
    )
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Create a mock SuperAdmin with proper attributes
    new_admin = MagicMock(spec=SuperAdmin)
    new_admin.username = "newadmin"
    new_admin.full_name = "New Admin"
    new_admin.is_active = True
    new_admin.created_at = datetime.now()

    # Mock the db.add to capture the created admin and update it
    def mock_add(obj):
        # This simulates the db.add setting the created_at and is_active fields
        if isinstance(obj, SuperAdmin):
            obj.created_at = new_admin.created_at
            obj.is_active = True
            return new_admin

    mock_db.add.side_effect = mock_add

    # Mock password hashing
    with patch("app.api.admin.get_password_hash", return_value="hashed_password"):
        result = await create_new_superadmin_endpoint(admin_data, mock_db, mock_admin)

    # Assertions
    assert mock_db.add.called
    assert mock_db.commit.called
    assert result.username == "newadmin"
    assert result.full_name == "New Admin"
    assert result.is_active is True
    assert result.created_at is not None


async def test_create_new_superadmin_endpoint_username_exists(mock_db, mock_admin):
    """Test creating a superadmin with an existing username raises 400."""
    # Setup
    admin_data = SuperAdminCreate(username="existing", password="password123")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin

    # Call the endpoint and check for exception
    with pytest.raises(HTTPException) as exc_info:
        await create_new_superadmin_endpoint(admin_data, mock_db, mock_admin)

    # Assertions
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


async def test_update_admin_password_endpoint(mock_db, mock_admin):
    """Test updating a superadmin's password."""
    # Setup with correct schema
    password_data = SuperAdminUpdate(
        current_password="oldpassword123", new_password="newpassword123"
    )
    target_admin = MagicMock(spec=SuperAdmin)
    target_admin.username = "testadmin"
    mock_db.query.return_value.filter.return_value.first.return_value = target_admin

    # Mock password verification and hashing
    with (
        patch("app.api.admin.verify_password", return_value=True),
        patch("app.api.admin.get_password_hash", return_value="new_hash"),
    ):
        result = await update_admin_password_endpoint(
            password_data, "testadmin", mock_db, mock_admin
        )

    # Assertions
    assert target_admin.hashed_password == "new_hash"
    assert mock_db.commit.called
    assert "updated successfully" in result.message


async def test_deactivate_admin_account_endpoint(mock_db, mock_admin):
    """Test deactivating a superadmin account."""
    # Setup - create a different admin than the one making the request
    mock_admin.username = "adminuser"  # The admin making the request

    target_admin = MagicMock(spec=SuperAdmin)
    target_admin.username = "targetadmin"  # The admin being deactivated
    mock_db.query.return_value.filter.return_value.first.return_value = target_admin
    mock_db.query.return_value.filter.return_value.count.return_value = (
        2  # More than 1 active admin
    )

    # Call the endpoint
    result = await deactivate_admin_account_endpoint("targetadmin", mock_db, mock_admin)

    # Assertions
    assert target_admin.is_active is False
    assert mock_db.commit.called
    assert "deactivated successfully" in result.message


async def test_deactivate_last_admin_account_endpoint(mock_db, mock_admin):
    """Test deactivating the last admin account raises 400."""
    # Setup - trying to deactivate yourself
    mock_admin.username = "testadmin"  # The admin making the request

    # Setting up the first() to return the same admin (trying to deactivate yourself)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin

    # Call the endpoint and check for exception
    with pytest.raises(HTTPException) as exc_info:
        await deactivate_admin_account_endpoint("testadmin", mock_db, mock_admin)

    # Assertions
    assert exc_info.value.status_code == 400
    assert "Cannot deactivate your own account" in exc_info.value.detail


async def test_deactivate_last_active_admin_account(mock_db, mock_admin):
    """Test deactivating another admin account works properly."""
    # Setup - trying to deactivate another admin account
    mock_admin.username = "adminuser"  # The admin making the request

    target_admin = MagicMock(spec=SuperAdmin)
    target_admin.username = "targetadmin"  # The admin being deactivated

    # Set up the mock database query to return target_admin for the username filter
    mock_db.query.return_value.filter.return_value.first.return_value = target_admin

    # For the active admin count query, we need to return a count greater than 1
    # Create a more complex mock that handles both first() and count() calls
    query_mock = MagicMock()
    filter_mock = MagicMock()

    # Configure first() to return target_admin when filtering by username
    first_mock = MagicMock(return_value=target_admin)

    # Configure count() to return 2 when checking active admins
    count_mock = MagicMock(return_value=2)

    # Set up the chain of mocks
    filter_mock.first = first_mock
    filter_mock.count = count_mock
    query_mock.filter = MagicMock(return_value=filter_mock)
    mock_db.query = MagicMock(return_value=query_mock)

    # Make sure admin_id and current_admin.id are different
    mock_admin.id = 1
    target_admin.id = 2

    # Call the endpoint
    result = await deactivate_admin_account_endpoint("targetadmin", mock_db, mock_admin)

    # Assertions
    assert target_admin.is_active is False
    assert mock_db.commit.called
    assert "deactivated successfully" in result.message


async def test_deactivate_last_active_admin_account_prevention(mock_db, mock_admin):
    """Test that deactivating the last active admin account raises an HTTP 400
    exception."""
    # Setup - trying to deactivate the last admin (not yourself)
    mock_admin.username = "adminuser"  # The admin making the request

    target_admin = MagicMock(spec=SuperAdmin)
    target_admin.username = "targetadmin"  # The admin being deactivated

    # Set up a more complex mock for the database query
    query_mock = MagicMock()
    username_filter_mock = MagicMock()
    active_filter_mock = MagicMock()

    # Configure the username filter to return target_admin
    username_filter_mock.first.return_value = target_admin

    # Configure the active filter to return count 1
    active_filter_mock.count.return_value = 1

    # Set up filter to return different mocks based on the filter criteria
    def filter_side_effect(*args, **kwargs):
        # When filtering by username, return username_filter_mock
        if args and "username" in str(args[0]):
            return username_filter_mock
        # When filtering by is_active, return active_filter_mock
        elif args and "is_active" in str(args[0]):
            return active_filter_mock
        return MagicMock()

    # Set up the query mock with our filter_side_effect
    query_mock.filter = MagicMock(side_effect=filter_side_effect)
    mock_db.query = MagicMock(return_value=query_mock)

    # Make sure admin_id and current_admin.id are different
    mock_admin.id = 1
    target_admin.id = 2

    # Call the endpoint and check for exception
    with pytest.raises(HTTPException) as exc_info:
        await deactivate_admin_account_endpoint("targetadmin", mock_db, mock_admin)

    # Assertions
    assert exc_info.value.status_code == 400
    assert "Cannot deactivate the last active admin account" in exc_info.value.detail
