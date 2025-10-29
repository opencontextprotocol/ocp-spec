"""
Tests for OCP Agent functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ocp_agent.agent import OCPAgent
from ocp_agent.context import AgentContext
from ocp_agent.schema_discovery import OCPTool, OCPAPISpec


class TestOCPAgent:
    """Test OCPAgent functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        return OCPAgent(
            agent_type="test_agent",
            user="test_user",
            workspace="test_workspace",
            agent_goal="test goal",
            enable_cache=False  # Disable cache for testing
        )
    
    @pytest.fixture
    def sample_api_spec(self):
        """Sample API specification for testing."""
        tools = [
            OCPTool(
                name="get_items",
                description="List all items",
                method="GET",
                path="/items",
                parameters={
                    "limit": {
                        "type": "integer",
                        "required": False,
                        "location": "query"
                    }
                },
                response_schema={}
            ),
            OCPTool(
                name="post_items",
                description="Create a new item",
                method="POST",
                path="/items",
                parameters={
                    "name": {
                        "type": "string",
                        "required": True,
                        "location": "body"
                    },
                    "description": {
                        "type": "string",
                        "required": False,
                        "location": "body"
                    }
                },
                response_schema={}
            ),
            OCPTool(
                name="get_items_id",
                description="Get a specific item",
                method="GET",
                path="/items/{id}",
                parameters={
                    "id": {
                        "type": "string",
                        "required": True,
                        "location": "path"
                    }
                },
                response_schema={}
            )
        ]
        
        return OCPAPISpec(
            title="Test API",
            version="1.0.0",
            base_url="https://api.test.com",
            description="A test API for testing purposes",
            tools=tools,
            raw_spec={}
        )
    
    def test_agent_creation(self, agent):
        """Test agent creation and initialization."""
        assert agent.context.agent_type == "test_agent"
        assert agent.context.user == "test_user"
        assert agent.context.workspace == "test_workspace"
        assert agent.context.current_goal == "test goal"
        assert isinstance(agent.known_apis, dict)
        assert len(agent.known_apis) == 0
        assert agent.discovery is not None
        assert agent.http_client is not None
    
    @patch('ocp_agent.schema_discovery.OCPSchemaDiscovery.discover_api')
    def test_register_api(self, mock_discover, agent, sample_api_spec):
        """Test API registration."""
        mock_discover.return_value = sample_api_spec
        
        result = agent.register_api(
            name="test_api",
            spec_url="https://api.test.com/openapi.json"
        )
        
        assert result == sample_api_spec
        assert "test_api" in agent.known_apis
        assert agent.known_apis["test_api"] == sample_api_spec
        assert "test_api" in agent.context.api_specs
        assert len(agent.context.history) == 1
        assert agent.context.history[0]["action"] == "api_registered"
        
        mock_discover.assert_called_once_with(
            "https://api.test.com/openapi.json", 
            None
        )
    
    @patch('ocp_agent.schema_discovery.OCPSchemaDiscovery.discover_api')
    def test_register_api_with_base_url(self, mock_discover, agent, sample_api_spec):
        """Test API registration with custom base URL."""
        mock_discover.return_value = sample_api_spec
        
        agent.register_api(
            name="test_api",
            spec_url="https://api.test.com/openapi.json",
            base_url="https://custom.test.com"
        )
        
        mock_discover.assert_called_once_with(
            "https://api.test.com/openapi.json",
            "https://custom.test.com"
        )
    
    def test_list_tools_no_apis(self, agent):
        """Test listing tools when no APIs are registered."""
        tools = agent.list_tools()
        assert tools == []
    
    def test_list_tools_with_api(self, agent, sample_api_spec):
        """Test listing tools after registering an API."""
        agent.known_apis["test_api"] = sample_api_spec
        
        # List all tools
        all_tools = agent.list_tools()
        assert len(all_tools) == 3
        assert all([tool.name in ["get_items", "post_items", "get_items_id"] 
                   for tool in all_tools])
        
        # List tools for specific API
        api_tools = agent.list_tools("test_api")
        assert len(api_tools) == 3
        assert api_tools == sample_api_spec.tools
    
    def test_list_tools_unknown_api(self, agent):
        """Test listing tools for unknown API."""
        with pytest.raises(ValueError, match="Unknown API: unknown_api"):
            agent.list_tools("unknown_api")
    
    def test_get_tool(self, agent, sample_api_spec):
        """Test getting a specific tool."""
        agent.known_apis["test_api"] = sample_api_spec
        
        # Get existing tool
        tool = agent.get_tool("get_items")
        assert tool is not None
        assert tool.name == "get_items"
        assert tool.method == "GET"
        
        # Get tool from specific API
        tool = agent.get_tool("post_items", "test_api")
        assert tool is not None
        assert tool.name == "post_items"
        
        # Get non-existent tool
        tool = agent.get_tool("nonexistent")
        assert tool is None
    
    @patch('ocp_agent.schema_discovery.OCPSchemaDiscovery.search_tools')
    def test_search_tools(self, mock_search, agent, sample_api_spec):
        """Test searching tools."""
        agent.known_apis["test_api"] = sample_api_spec
        mock_search.return_value = [sample_api_spec.tools[0]]  # Return first tool
        
        # Search all APIs
        results = agent.search_tools("list")
        assert len(results) == 1
        mock_search.assert_called_once_with(sample_api_spec, "list")
        
        # Search specific API
        mock_search.reset_mock()
        results = agent.search_tools("list", "test_api")
        assert len(results) == 1
        mock_search.assert_called_once_with(sample_api_spec, "list")
        
        # Search unknown API
        results = agent.search_tools("list", "unknown_api")
        assert results == []
    
    def test_validate_parameters(self, agent, sample_api_spec):
        """Test parameter validation."""
        post_tool = sample_api_spec.tools[1]  # post_items tool
        
        # Valid parameters
        errors = agent._validate_parameters(post_tool, {"name": "test"})
        assert errors == []
        
        # Missing required parameter
        errors = agent._validate_parameters(post_tool, {})
        assert len(errors) == 1
        assert "Missing required parameter: name" in errors[0]
        
        # Wrong parameter type
        errors = agent._validate_parameters(post_tool, {"name": 123})
        # Basic validation doesn't catch string type issues in our current implementation
        assert errors == []  # This might change if we enhance type validation
    
    def test_build_request(self, agent, sample_api_spec):
        """Test building HTTP requests from tools and parameters."""
        # Test query parameters
        get_tool = sample_api_spec.tools[0]  # get_items tool
        url, params = agent._build_request(
            sample_api_spec, 
            get_tool, 
            {"limit": 10}
        )
        
        assert url == "https://api.test.com/items"
        assert params["params"]["limit"] == 10
        assert params["timeout"] == 30
        
        # Test path parameters
        get_tool = sample_api_spec.tools[2]  # get_items_id tool
        url, params = agent._build_request(
            sample_api_spec, 
            get_tool, 
            {"id": "123"}
        )
        
        assert url == "https://api.test.com/items/123"
        assert "params" not in params or not params["params"]
        
        # Test body parameters
        post_tool = sample_api_spec.tools[1]  # post_items tool
        url, params = agent._build_request(
            sample_api_spec,
            post_tool,
            {"name": "test item", "description": "test desc"}
        )
        
        assert url == "https://api.test.com/items"
        assert params["json"]["name"] == "test item"
        assert params["json"]["description"] == "test desc"
    
    @patch('ocp_agent.http_client.OCPHTTPClient.request')
    def test_call_tool_success(self, mock_request, agent, sample_api_spec):
        """Test successful tool calling."""
        agent.known_apis["test_api"] = sample_api_spec
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.ok = True
        mock_response.content = b'{"success": true}'
        mock_request.return_value = mock_response
        
        response = agent.call_tool("get_items", {"limit": 5})
        
        assert response == mock_response
        assert len(agent.context.history) >= 2  # tool_call and tool_response
        
        # Check that the request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "GET"  # method
        assert call_args[0][1] == "https://api.test.com/items"  # url
        assert call_args[1]["params"]["limit"] == 5
    
    def test_call_tool_not_found(self, agent, sample_api_spec):
        """Test calling a non-existent tool."""
        agent.known_apis["test_api"] = sample_api_spec
        
        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            agent.call_tool("nonexistent")
    
    def test_call_tool_validation_error(self, agent, sample_api_spec):
        """Test calling a tool with invalid parameters."""
        agent.known_apis["test_api"] = sample_api_spec
        
        with pytest.raises(ValueError, match="Parameter validation failed"):
            agent.call_tool("post_items", {})  # Missing required 'name' parameter
    
    @patch('ocp_agent.schema_discovery.OCPSchemaDiscovery.generate_tool_documentation')
    def test_get_tool_documentation(self, mock_generate_doc, agent, sample_api_spec):
        """Test getting tool documentation."""
        agent.known_apis["test_api"] = sample_api_spec
        mock_generate_doc.return_value = "Tool documentation"
        
        doc = agent.get_tool_documentation("get_items")
        assert doc == "Tool documentation"
        mock_generate_doc.assert_called_once_with(sample_api_spec.tools[0])
        
        # Test non-existent tool
        doc = agent.get_tool_documentation("nonexistent")
        assert "not found" in doc
    
    def test_update_goal(self, agent):
        """Test updating agent goal."""
        initial_interactions = len(agent.context.history)
        
        agent.update_goal("new goal", "goal summary")
        
        assert agent.context.current_goal == "new goal"
        assert agent.context.context_summary == "goal summary"
    
    @patch('ocp_agent.agent.OCPRegistry')
    def test_register_api_from_registry(self, mock_registry_class, agent, sample_api_spec):
        """Test API registration from registry."""
        # Setup mock registry
        mock_registry = Mock()
        mock_registry.get_api_spec.return_value = sample_api_spec
        mock_registry_class.return_value = mock_registry
        
        # Create new agent to trigger registry initialization
        agent = OCPAgent(
            agent_type="test_agent",
            registry_url="https://test-registry.com",
            enable_cache=False
        )
        
        # Register API from registry
        result = agent.register_api("test_api")
        
        # Verify registry was called correctly
        mock_registry.get_api_spec.assert_called_once_with("test_api", None)
        
        # Verify API was registered
        assert result == sample_api_spec
        assert "test_api" in agent.known_apis
        assert agent.known_apis["test_api"] == sample_api_spec
        
        # Verify context tracking
        assert "test_api" in agent.context.api_specs
        assert agent.context.api_specs["test_api"] == "registry:test_api"
        
        # Verify interaction logging
        assert len(agent.context.history) == 1
        interaction = agent.context.history[0]
        assert interaction["action"] == "api_registered"
        assert interaction["api_endpoint"] == "registry:test_api"
        assert interaction["metadata"]["source"] == "registry"
    
    @patch('ocp_agent.agent.OCPSchemaDiscovery')
    def test_register_api_from_openapi_url(self, mock_discovery_class, agent, sample_api_spec):
        """Test API registration from OpenAPI URL (existing behavior)."""
        # Setup mock discovery
        mock_discovery = Mock()
        mock_discovery.discover_api.return_value = sample_api_spec
        mock_discovery_class.return_value = mock_discovery
        
        # Create new agent
        agent = OCPAgent(agent_type="test_agent", enable_cache=False)
        
        # Register API with URL
        result = agent.register_api("test_api", "https://api.test.com/openapi.json")
        
        # Verify discovery was called
        mock_discovery.discover_api.assert_called_once_with("https://api.test.com/openapi.json", None)
        
        # Verify API was registered
        assert result == sample_api_spec
        assert "test_api" in agent.known_apis
        
        # Verify context tracking  
        assert agent.context.api_specs["test_api"] == "https://api.test.com/openapi.json"
        
        # Verify metadata indicates OpenAPI source
        interaction = agent.context.history[0]
        assert interaction["metadata"]["source"] == "openapi"
    
    @patch('ocp_agent.agent.OCPRegistry')
    def test_register_api_with_base_url_override(self, mock_registry_class, agent, sample_api_spec):
        """Test API registration with base URL override."""
        mock_registry = Mock()
        mock_registry.get_api_spec.return_value = sample_api_spec
        mock_registry_class.return_value = mock_registry
        
        agent = OCPAgent(agent_type="test_agent", enable_cache=False)
        
        # Register with base URL override
        agent.register_api("test_api", base_url="https://custom.test.com")
        
        # Verify base_url was passed to registry
        mock_registry.get_api_spec.assert_called_once_with("test_api", "https://custom.test.com")
    
    def test_agent_initialization_with_registry_url(self):
        """Test agent initialization with custom registry URL."""
        agent = OCPAgent(
            agent_type="test_agent",
            registry_url="https://custom-registry.com"
        )
        
        assert agent.registry.registry_url == "https://custom-registry.com"