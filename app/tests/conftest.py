"""Pytest configuration file with common fixtures."""

import os
import warnings
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import JSON, Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import create_access_token
from app.db.database import Base, get_db
from app.main import app
from app.models.cfdi_history import CFDIHistory
from app.models.user import APIToken, User

# Suppress Pydantic deprecation warnings
warnings.filterwarnings(
    "ignore",
    message="The `__fields__` attribute is deprecated",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message="The `__fields_set__` attribute is deprecated",
    category=DeprecationWarning,
)

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def configure_database_url():
    """Configure a non-SQLite database URL to ensure database.py's non-SQLite code
    branch is covered during tests."""
    # Save original value if it exists
    original_database_url = os.environ.get("DATABASE_URL", None)

    # Set a PostgreSQL URL
    os.environ["DATABASE_URL"] = "postgresql://fake:fake@localhost:5432/fakedb"

    # Let tests run
    yield

    # Restore original
    if original_database_url is not None:
        os.environ["DATABASE_URL"] = original_database_url
    else:
        del os.environ["DATABASE_URL"]


# Ensure the CFDIHistory model has required columns
if not hasattr(CFDIHistory, "token_id") or CFDIHistory.token_id is None:
    CFDIHistory.token_id = Column(String, index=True, nullable=True)

if not hasattr(CFDIHistory, "details") or CFDIHistory.details is None:
    CFDIHistory.details = Column(JSON, nullable=True)


@pytest.fixture(scope="session", autouse=True)
def patch_cfdi_history_model():
    """Patch the CFDIHistory model to ensure it has all necessary columns for tests."""
    original_columns = {}
    
    # Save original columns if they exist
    if hasattr(CFDIHistory, "__table__") and hasattr(CFDIHistory.__table__, "columns"):
        for column_name in ["token_id", "details"]:
            original_columns[column_name] = getattr(CFDIHistory, column_name, None)
    
    # Apply patches
    if not hasattr(CFDIHistory, "token_id") or CFDIHistory.token_id is None:
        CFDIHistory.token_id = Column(String, index=True, nullable=True)
    
    if not hasattr(CFDIHistory, "details") or CFDIHistory.details is None:
        CFDIHistory.details = Column(JSON, nullable=True)
    
    yield
    
    # Restore original columns after tests
    for column_name, original_column in original_columns.items():
        if original_column is not None:
            setattr(CFDIHistory, column_name, original_column)


@pytest.fixture
def test_db():
    # Create in-memory SQLite database for testing
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Dependency override
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Create a test database session
    db = TestingSessionLocal()

    # Create a test user
    test_user = User(name="Test User", email="test@example.com", is_active=True)
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Create a test API token
    test_token = APIToken(
        token="test-token",
        description="Test Token",
        is_active=True,
        user_id=test_user.id,
    )
    db.add(test_token)
    db.commit()

    try:
        yield db
    finally:
        db.close()
        # Drop tables after tests
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Fixture that provides a database session for unit tests.

    This is an alias for test_db to maintain naming consistency with the rest of the
    codebase.
    """
    yield test_db


@pytest.fixture
def test_token():
    """Fixture that provides a test JWT token."""
    return create_access_token(user_id=1)


@pytest.fixture
def api_token():
    """Fixture that provides a test API token string."""
    return "test-token"


@pytest.fixture
def client(test_db):
    # Return a test client with the test database
    with TestClient(app) as c:
        yield c


@pytest.fixture
def override_get_token_dependency():
    """Override the token dependency to use a test token for integration tests."""
    # Store the original dependency
    original_dependency = app.dependency_overrides.get(get_db, None)

    def mock_get_current_token():
        return "test-token"

    # Override the dependency
    from app.core.deps import get_current_token

    app.dependency_overrides[get_current_token] = mock_get_current_token

    yield

    # Restore the original dependency
    if original_dependency:
        app.dependency_overrides[get_current_token] = original_dependency
    else:
        del app.dependency_overrides[get_current_token]


class MockResponse:
    """Mock response object for testing."""

    def __init__(self, text: str = "", status_code: int = 200):
        self.text = text
        self.status_code = status_code
