"""Tests for OCP Registry functionality."""

import pytest
import requests
import requests_mock
from unittest.mock import patch, Mock
import os
import json

from ocp_agent.registry import OCPRegistry
from ocp_agent.errors import RegistryUnavailable, APINotFound
from ocp_agent.schema_discovery import OCPAPISpec, OCPTool


class TestOCPRegistry:
    """Test OCPRegistry functionality."""
    
    @pytest.fixture
    def registry(self):
        """Create test registry instance."""
        return OCPRegistry("https://test-registry.ocp.dev")
    
    @pytest.fixture
    def sample_api_entry(self):
        """Sample registry API entry response."""
        return {
            "name": "httpbin",
            "display_name": "HTTPBin Testing Service",
            "description": "HTTP testing service",
            "openapi_url": "https://httpbin.org/spec.json",
            "base_url": "https://httpbin.org/",
            "category": "development",
            "auth_config": {
                "type": "none",
                "header_name": None,
                "instructions": "No authentication required"
            },
            "tags": ["testing", "debugging"],
            "tool_count": 2,
            "tools": [
                {
                    "name": "get_get",
                    "description": "Returns GET request data",
                    "method": "GET",
                    "path": "/get",
                    "parameters": {},
                    "response_schema": {}
                },
                {
                    "name": "post_post",
                    "description": "Returns POST request data",
                    "method": "POST",
                    "path": "/post",
                    "parameters": {},
                    "response_schema": {}
                }
            ]
        }
    
    def test_registry_initialization_default_url(self):
        """Test registry initialization with default URL."""
        registry = OCPRegistry()
        assert registry.registry_url == "https://registry.ocp.dev"
    
    def test_registry_initialization_custom_url(self):
        """Test registry initialization with custom URL."""
        registry = OCPRegistry("https://custom-registry.com")
        assert registry.registry_url == "https://custom-registry.com"
    
    def test_registry_initialization_env_var(self):
        """Test registry initialization with environment variable."""
        with patch.dict(os.environ, {'OCP_REGISTRY_URL': 'https://env-registry.com'}):
            registry = OCPRegistry()
            assert registry.registry_url == "https://env-registry.com"
    
    def test_registry_initialization_invalid_url(self):
        """Test registry initialization with invalid URL."""
        with pytest.raises(ValueError, match="Invalid registry URL"):
            OCPRegistry("invalid-url")
    
    def test_get_api_spec_success(self, registry, sample_api_entry):
        """Test successful API spec retrieval."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/registry/httpbin",
                json=sample_api_entry
            )
            
            api_spec = registry.get_api_spec("httpbin")
            
            assert isinstance(api_spec, OCPAPISpec)
            assert api_spec.title == "HTTPBin Testing Service"
            assert api_spec.base_url == "https://httpbin.org/"
            assert len(api_spec.tools) == 2
            assert api_spec.tools[0].name == "get_get"
            assert api_spec.tools[1].name == "post_post"
    
    def test_get_api_spec_with_base_url_override(self, registry, sample_api_entry):
        """Test API spec retrieval with base URL override."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/registry/httpbin",
                json=sample_api_entry
            )
            
            api_spec = registry.get_api_spec("httpbin", "https://custom.httpbin.org")
            
            assert api_spec.base_url == "https://custom.httpbin.org"
    
    def test_get_api_spec_not_found(self, registry):
        """Test API spec retrieval for non-existent API."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/registry/nonexistent",
                status_code=404
            )
            # Mock search for suggestions
            m.get(
                "https://test-registry.ocp.dev/api/v1/search",
                json={"results": [{"name": "httpbin"}]}
            )
            
            with pytest.raises(APINotFound) as exc_info:
                registry.get_api_spec("nonexistent")
            
            assert exc_info.value.api_name == "nonexistent"
            assert "httpbin" in exc_info.value.suggestions
    
    def test_get_api_spec_registry_unavailable(self, registry):
        """Test API spec retrieval when registry is unavailable."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/registry/httpbin",
                exc=requests.exceptions.ConnectionError
            )
            
            with pytest.raises(RegistryUnavailable) as exc_info:
                registry.get_api_spec("httpbin")
            
            assert "test-registry.ocp.dev" in str(exc_info.value)
    
    def test_search_apis_success(self, registry):
        """Test successful API search."""
        search_response = {
            "results": [
                {"name": "github"},
                {"name": "gitlab"}
            ]
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/search",
                json=search_response
            )
            
            results = registry.search_apis("git")
            
            assert results == ["github", "gitlab"]
    
    def test_search_apis_failure(self, registry):
        """Test API search when registry is unavailable."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/search",
                exc=requests.exceptions.ConnectionError
            )
            
            results = registry.search_apis("git")
            
            # Should return empty list on failure
            assert results == []
    
    def test_list_apis_success(self, registry):
        """Test successful API listing."""
        api_list = [
            {"name": "github"},
            {"name": "stripe"},
            {"name": "httpbin"}
        ]
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/registry",
                json=api_list
            )
            
            results = registry.list_apis()
            
            assert results == ["github", "stripe", "httpbin"]
    
    def test_list_apis_failure(self, registry):
        """Test API listing when registry is unavailable."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/registry",
                exc=requests.exceptions.ConnectionError
            )
            
            results = registry.list_apis()
            
            # Should return empty list on failure
            assert results == []
    
    def test_entry_to_spec_conversion(self, registry, sample_api_entry):
        """Test conversion of registry entry to OCPAPISpec."""
        api_spec = registry._entry_to_spec(sample_api_entry)
        
        assert isinstance(api_spec, OCPAPISpec)
        assert api_spec.title == "HTTPBin Testing Service"
        assert api_spec.version == "1.0.0"
        assert api_spec.base_url == "https://httpbin.org/"
        
        # Check tools conversion
        assert len(api_spec.tools) == 2
        tool1 = api_spec.tools[0]
        assert isinstance(tool1, OCPTool)
        assert tool1.name == "get_get"
        assert tool1.method == "GET"
        assert tool1.path == "/get"
    
    def test_get_suggestions_exact_match(self, registry):
        """Test getting suggestions with exact match."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://test-registry.ocp.dev/api/v1/search",
                json={"results": [{"name": "github"}]}
            )
            
            suggestions = registry._get_suggestions("github")
            
            assert suggestions == ["github"]
    
    def test_get_suggestions_partial_match(self, registry):
        """Test getting suggestions with partial match."""
        with requests_mock.Mocker() as m:
            # First call returns no results
            m.get(
                "https://test-registry.ocp.dev/api/v1/search?q=unknown",
                json={"results": []}
            )
            # Second call with partial query returns results
            m.get(
                "https://test-registry.ocp.dev/api/v1/search?q=unk",
                json={"results": [{"name": "github"}]}
            )
            
            suggestions = registry._get_suggestions("unknown")
            
            assert suggestions == ["github"]