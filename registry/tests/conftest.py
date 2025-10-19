"""Test configuration and fixtures."""

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from registry.database import Base, get_db
from registry.main import app


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_api_registration():
    """Sample API registration for testing."""
    return {
        "name": "github",
        "display_name": "GitHub API", 
        "description": "GitHub REST API for repository management and collaboration",
        "openapi_url": "https://api.github.com/rest/openapi.json",
        "base_url": "https://api.github.com",
        "category": "development",
        "auth_config": {
            "type": "bearer_token",
            "header_name": "Authorization",
            "instructions": "Use 'Bearer <token>' format with personal access token"
        },
        "tags": ["git", "repositories", "collaboration"],
        "documentation_url": "https://docs.github.com/en/rest",
        "rate_limit": "5000 requests/hour"
    }