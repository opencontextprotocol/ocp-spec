"""
Tests for OCP schema discovery functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from ocp_agent.schema_discovery import OCPSchemaDiscovery, OCPTool, OCPAPISpec


class TestOCPSchemaDiscovery:
    """Test schema discovery functionality."""
    
    @pytest.fixture
    def discovery(self):
        """Create a schema discovery instance."""
        return OCPSchemaDiscovery()
    
    @pytest.fixture
    def sample_openapi_spec(self):
        """Sample OpenAPI specification for testing."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "https://api.example.com"}
            ],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "description": "Get a list of all users",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer"},
                                "required": False
                            }
                        ]
                    },
                    "post": {
                        "summary": "Create user",
                        "description": "Create a new user",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string"}
                                        },
                                        "required": ["name", "email"]
                                    }
                                }
                            }
                        }
                    }
                },
                "/users/{id}": {
                    "get": {
                        "summary": "Get user",
                        "description": "Get a specific user by ID",
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "schema": {"type": "string"},
                                "required": True
                            }
                        ]
                    }
                }
            }
        }
    
    def test_parse_openapi_spec(self, discovery, sample_openapi_spec):
        """Test parsing OpenAPI specification."""
        api_spec = discovery._parse_openapi_spec(
            sample_openapi_spec, 
            "https://api.example.com"
        )
        
        assert isinstance(api_spec, OCPAPISpec)
        assert api_spec.title == "Test API"
        assert api_spec.version == "1.0.0"
        assert api_spec.base_url == "https://api.example.com"
        assert len(api_spec.tools) == 3  # GET /users, POST /users, GET /users/{id}
    
    def test_generate_tools_from_spec(self, discovery, sample_openapi_spec):
        """Test tool generation from OpenAPI specification."""
        api_spec = discovery._parse_openapi_spec(
            sample_openapi_spec, 
            "https://api.example.com"
        )
        
        tools = api_spec.tools
        assert len(tools) == 3  # GET /users, POST /users, GET /users/{id}
        
        # Check that we have the expected tools with deterministic names
        tool_names = [t.name for t in tools]
        expected_names = ["get_users", "post_users", "get_users_id"]  # Based on naming logic
        
        for expected_name in expected_names:
            assert expected_name in tool_names, f"Expected tool name '{expected_name}' not found in {tool_names}"
        
        # Check GET /users tool
        get_users = next((t for t in tools if t.name == "get_users"), None)
        assert get_users is not None
        assert get_users.method == "GET"
        assert get_users.path == "/users"
        assert get_users.description == "List users"
        assert "limit" in get_users.parameters
        assert get_users.parameters["limit"]["type"] == "integer"
        assert get_users.parameters["limit"]["location"] == "query"
        assert not get_users.parameters["limit"]["required"]
        
        # Check POST /users tool
        post_users = next((t for t in tools if t.name == "post_users"), None)
        assert post_users is not None
        assert post_users.method == "POST"
        assert post_users.path == "/users"
        assert "name" in post_users.parameters
        assert "email" in post_users.parameters
        assert post_users.parameters["name"]["required"]
        assert post_users.parameters["email"]["required"]
        
        # Check GET /users/{id} tool
        get_users_id = next((t for t in tools if t.name == "get_users_id"), None)
        assert get_users_id is not None
        assert get_users_id.method == "GET"
        assert get_users_id.path == "/users/{id}"
        assert "id" in get_users_id.parameters
        assert get_users_id.parameters["id"]["location"] == "path"
        assert get_users_id.parameters["id"]["required"]
    
    @patch('requests.get')
    def test_discover_api_success(self, mock_get, discovery, sample_openapi_spec):
        """Test successful API discovery."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = sample_openapi_spec
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api_spec = discovery.discover_api(
            "https://api.example.com/openapi.json"
        )
        
        assert isinstance(api_spec, OCPAPISpec)
        assert api_spec.title == "Test API"
        assert len(api_spec.tools) == 3
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_discover_api_with_base_url_override(self, mock_get, discovery, sample_openapi_spec):
        """Test API discovery with base URL override."""
        mock_response = Mock()
        mock_response.json.return_value = sample_openapi_spec
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api_spec = discovery.discover_api(
            "https://api.example.com/openapi.json",
            base_url="https://custom.example.com"
        )
        
        assert api_spec.base_url == "https://custom.example.com"
    
    @patch('requests.get')
    def test_discover_api_failure(self, mock_get, discovery):
        """Test API discovery failure handling."""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Network error"):
            discovery.discover_api("https://api.example.com/openapi.json")
    
    def test_search_tools(self, discovery):
        """Test tool searching functionality."""
        # Create some sample tools
        tools = [
            OCPTool(
                name="list_users",
                description="Get all users from the system",
                method="GET",
                path="/users",
                parameters={},
                response_schema={}
            ),
            OCPTool(
                name="create_user",
                description="Create a new user account",
                method="POST",
                path="/users",
                parameters={},
                response_schema={}
            ),
            OCPTool(
                name="list_orders",
                description="Get customer orders",
                method="GET",
                path="/orders",
                parameters={},
                response_schema={}
            )
        ]
        
        api_spec = OCPAPISpec(
            title="Test API",
            version="1.0.0",
            base_url="https://api.example.com",
            description="A test API for testing purposes",
            tools=tools,
            raw_spec={}
        )
        
        # Test search by name
        user_tools = discovery.search_tools(api_spec, "user")
        assert len(user_tools) == 2
        assert all("user" in tool.name.lower() or "user" in tool.description.lower() 
                  for tool in user_tools)
        
        # Test search by description
        create_tools = discovery.search_tools(api_spec, "create")
        assert len(create_tools) == 1
        assert create_tools[0].name == "create_user"
        
        # Test no matches
        no_matches = discovery.search_tools(api_spec, "nonexistent")
        assert len(no_matches) == 0
    
    def test_generate_tool_documentation(self, discovery):
        """Test tool documentation generation."""
        tool = OCPTool(
            name="create_user",
            description="Create a new user account",
            method="POST",
            path="/users",
            parameters={
                "name": {
                    "type": "string",
                    "description": "User's full name",
                    "required": True,
                    "location": "body"
                },
                "email": {
                    "type": "string", 
                    "description": "User's email address",
                    "required": True,
                    "location": "body"
                },
                "age": {
                    "type": "integer",
                    "description": "User's age",
                    "required": False,
                    "location": "body"
                }
            },
            response_schema={}
        )
        
        doc = discovery.generate_tool_documentation(tool)
        
        assert "create_user" in doc
        assert "Create a new user account" in doc
        assert "POST" in doc
        assert "/users" in doc
        assert "name" in doc
        assert "email" in doc
        assert "age" in doc
        assert "required" in doc.lower()
        assert "optional" in doc.lower()


class TestOCPTool:
    """Test OCPTool dataclass."""
    
    def test_tool_creation(self):
        """Test creating an OCPTool instance."""
        tool = OCPTool(
            name="test_tool",
            description="A test tool",
            method="GET",
            path="/test",
            parameters={"param": {"type": "string"}},
            response_schema={}
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.method == "GET"
        assert tool.path == "/test"
        assert tool.parameters["param"]["type"] == "string"


class TestOCPAPISpec:
    """Test OCPAPISpec dataclass."""
    
    def test_api_spec_creation(self):
        """Test creating an OCPAPISpec instance."""
        tools = [
            OCPTool("tool1", "Description 1", "GET", "/path1", {}, {}),
            OCPTool("tool2", "Description 2", "POST", "/path2", {}, {})
        ]
        
        api_spec = OCPAPISpec(
            title="Test API",
            version="1.0.0",
            base_url="https://api.example.com",
            description="A test API for testing purposes",
            tools=tools,
            raw_spec={}
        )
        
        assert api_spec.title == "Test API"
        assert api_spec.version == "1.0.0" 
        assert api_spec.base_url == "https://api.example.com"
        assert api_spec.description == "A test API for testing purposes"
        assert len(api_spec.tools) == 2
        assert api_spec.tools[0].name == "tool1"
        assert api_spec.tools[1].name == "tool2"