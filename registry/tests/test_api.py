"""Test the registry API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ocp-registry"


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "api" in data


def test_register_api(client: TestClient, sample_api_registration):
    """Test API registration."""
    response = client.post("/api/v1/registry", json=sample_api_registration)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == sample_api_registration["name"]
    assert data["display_name"] == sample_api_registration["display_name"]
    assert data["status"] in ["active", "validation_pending", "validation_failed"]
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_api(client: TestClient, sample_api_registration):
    """Test registering duplicate API fails."""
    # Register first time
    response = client.post("/api/v1/registry", json=sample_api_registration)
    assert response.status_code == 201
    
    # Try to register same API again
    response = client.post("/api/v1/registry", json=sample_api_registration)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_api(client: TestClient, sample_api_registration):
    """Test getting API by name."""
    # Register API first
    register_response = client.post("/api/v1/registry", json=sample_api_registration)
    assert register_response.status_code == 201
    
    # Get API
    response = client.get(f"/api/v1/registry/{sample_api_registration['name']}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == sample_api_registration["name"]
    assert data["usage_count"] >= 1  # Should increment on access


def test_get_nonexistent_api(client: TestClient):
    """Test getting non-existent API returns 404."""
    response = client.get("/api/v1/registry/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_apis(client: TestClient, sample_api_registration):
    """Test listing APIs."""
    # Register API first
    client.post("/api/v1/registry", json=sample_api_registration)
    
    # List APIs
    response = client.get("/api/v1/registry")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(api["name"] == sample_api_registration["name"] for api in data)


def test_search_apis(client: TestClient, sample_api_registration):
    """Test searching APIs."""
    # Register API first
    client.post("/api/v1/registry", json=sample_api_registration)
    
    # Search for API
    response = client.get("/api/v1/search?q=github")
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["results"]) >= 1


def test_get_categories(client: TestClient, sample_api_registration):
    """Test getting categories."""
    # Register API first
    client.post("/api/v1/registry", json=sample_api_registration)
    
    # Get categories
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    # Should have at least the development category
    category_names = [cat["category"] for cat in data]
    assert "development" in category_names


def test_validate_api_spec(client: TestClient):
    """Test API specification validation."""
    validation_request = {
        "openapi_url": "https://httpbin.org/spec.json",
        "base_url": "https://httpbin.org"
    }
    
    response = client.post("/api/v1/validate", json=validation_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "valid" in data
    assert "openapi_valid" in data
    assert "endpoint_accessible" in data
    assert "errors" in data


def test_get_registry_stats(client: TestClient, sample_api_registration):
    """Test getting registry statistics."""
    # Register API first
    client.post("/api/v1/registry", json=sample_api_registration)
    
    # Get stats
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_apis" in data
    assert "active_apis" in data
    assert "categories" in data
    assert "most_popular" in data
    assert data["total_apis"] >= 1