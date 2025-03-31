"""
Pytest configuration file with common fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

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
    try:
        yield db
    finally:
        db.close()
        # Drop tables after tests
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    # Return a test client with the test database
    with TestClient(app) as c:
        yield c
