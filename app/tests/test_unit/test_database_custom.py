"""
Custom tests to cover database.py completely.
These tests use special techniques to overcome the challenge of testing
module-level code that executes on import.
"""
import pytest
from unittest.mock import patch, MagicMock
import importlib
import sys


class TestModuleImport:
    """
    Tests for module-level code using a special technique.
    This class uses a separate testing approach to test code that runs on import.
    """
    
    def test_create_engine_with_sqlite(self, monkeypatch):
        """Test that SQLite engine is created with correct parameters."""
        # Import the modules we're going to patch first to avoid any issues
        import sqlalchemy
        import app.core.config

        # Create our mocks
        mock_create_engine = MagicMock(return_value="mocked_engine")
        mock_settings = MagicMock()
        mock_settings.DATABASE_URL = "sqlite:///test.db"
        
        # Apply monkeypatching
        monkeypatch.setattr(sqlalchemy, "create_engine", mock_create_engine)
        monkeypatch.setattr(app.core.config, "settings", mock_settings)
        
        # Remove the database module if it's already imported
        if "app.db.database" in sys.modules:
            del sys.modules["app.db.database"]
            
        # Import the module - this should trigger our patched code
        import app.db.database
        
        # Verify that create_engine was called with the right parameters for SQLite
        mock_create_engine.assert_any_call(
            "sqlite:///test.db",
            connect_args={"check_same_thread": False}
        )
    
    def test_create_engine_with_postgresql(self, monkeypatch):
        """Test that PostgreSQL engine is created with correct parameters."""
        # Import the modules we're going to patch first to avoid any issues
        import sqlalchemy
        import app.core.config

        # Create our mocks
        mock_create_engine = MagicMock(return_value="mocked_engine")
        mock_settings = MagicMock()
        mock_settings.DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
        
        # Apply monkeypatching
        monkeypatch.setattr(sqlalchemy, "create_engine", mock_create_engine)
        monkeypatch.setattr(app.core.config, "settings", mock_settings)
        
        # Remove the database module if it's already imported
        if "app.db.database" in sys.modules:
            del sys.modules["app.db.database"]
            
        # Import the module - this should trigger our patched code
        import app.db.database
        
        # Verify that create_engine was called with the right parameters for PostgreSQL
        mock_create_engine.assert_any_call("postgresql://user:pass@localhost:5432/db") 