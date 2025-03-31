"""Unit tests for database initialization."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.init_db import init_db
from app.models.user import SuperAdmin


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = MagicMock()
    return db


def test_init_db_admin_exists(mock_db):
    """Test init_db when admin already exists."""
    # Setup - mock that the admin already exists
    mock_admin = MagicMock(spec=SuperAdmin)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin

    # Configure settings mock
    with patch("app.db.init_db.settings", autospec=True) as mock_settings:
        mock_settings.ADMIN_USERNAME = "testadmin"
        mock_settings.ADMIN_PASSWORD = "testpassword"

        # Call the function
        init_db(mock_db)

    # Verify - should not create a new admin
    assert not mock_db.add.called
    assert not mock_db.commit.called


def test_init_db_creates_admin(mock_db):
    """Test init_db creates admin when none exists."""
    # Setup - mock that no admin exists yet
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Configure settings and hash_password mocks
    with (
        patch("app.db.init_db.settings", autospec=True) as mock_settings,
        patch("app.db.init_db.get_password_hash", return_value="hashed_password"),
    ):
        mock_settings.ADMIN_USERNAME = "testadmin"
        mock_settings.ADMIN_PASSWORD = "testpassword"

        # Call the function
        init_db(mock_db)

    # Verify a new admin was created
    assert mock_db.add.called
    assert mock_db.commit.called

    # Check the admin was created with the right values
    args, _ = mock_db.add.call_args
    created_admin = args[0]
    assert isinstance(created_admin, SuperAdmin)
    assert created_admin.username == "testadmin"
    assert created_admin.hashed_password == "hashed_password"


def test_init_db_no_credentials(mock_db):
    """Test init_db when admin credentials are not configured."""
    # Setup - mock that no admin exists yet
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Configure settings with empty credentials
    with patch("app.db.init_db.settings", autospec=True) as mock_settings:
        mock_settings.ADMIN_USERNAME = ""
        mock_settings.ADMIN_PASSWORD = ""

        # Call the function
        init_db(mock_db)

    # Verify - should not create a new admin
    assert not mock_db.add.called
    assert not mock_db.commit.called
