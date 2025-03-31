"""
Special test module for database.py coverage.
This aims to directly test the conditional branches during module import.
"""

import importlib
import sys
from unittest import mock


def test_sqlite_engine_creation():
    """
    Test the SQLite engine creation branch (line 23).

    This test directly covers line 23 in database.py by modifying the module state
    and forcing reimporting the module to trigger the if branch for SQLite.
    """
    # Save original modules
    orig_modules = dict(sys.modules)

    try:
        # Remove the database module if loaded
        if "app.db.database" in sys.modules:
            del sys.modules["app.db.database"]

        # Mock our dependencies for a fresh import
        mock_settings = mock.MagicMock()
        mock_settings.DATABASE_URL = "sqlite:///test.db"

        mock_engine = mock.MagicMock()
        mock_create_engine = mock.MagicMock(return_value=mock_engine)

        # Create mocks for the imported modules
        mock_config = mock.MagicMock()
        mock_config.settings = mock_settings

        mock_sqlalchemy = mock.MagicMock()
        mock_sqlalchemy.create_engine = mock_create_engine

        # Replace modules with mocks
        sys.modules["app.core.config"] = mock_config
        sys.modules["sqlalchemy"] = mock_sqlalchemy

        # Import the database module - this will execute the module code
        import app.db.database

        importlib.reload(app.db.database)

        # Verify the sqlite engine creation was called with correct parameters
        # Instead of asserting the call count, check if the right parameters were used
        found_expected_call = False
        expected_args = ("sqlite:///test.db",)
        expected_kwargs = {"connect_args": {"check_same_thread": False}}

        for args, kwargs in mock_create_engine.call_args_list:
            if (
                args == expected_args
                and "connect_args" in kwargs
                and kwargs["connect_args"] == expected_kwargs["connect_args"]
            ):
                found_expected_call = True
                break

        assert (
            found_expected_call
        ), "SQLite engine creation was not called with expected parameters"

    finally:
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(orig_modules)
