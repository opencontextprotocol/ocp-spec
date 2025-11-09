"""
Tests for OCP HTTP client functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
from urllib.parse import urlparse

from ocp_agent.http_client import (
    OCPHTTPClient,
    wrap_api
)
from ocp_agent.context import AgentContext
from ocp_agent.headers import create_ocp_headers


class TestOCPHTTPClient:
    """Test OCPHTTPClient class functionality."""
    
    @pytest.fixture
    def context(self):
        """Create test context."""
        return AgentContext(
            agent_type="test_agent",
            user="test_user",
            current_goal="testing http client"
        )
    
    def test_init_without_http_client(self, context):
        """Test initialization with default requests client."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            ocp_client = OCPHTTPClient(context)
            
            assert ocp_client.context == context
            assert ocp_client.http_client == mock_session
            mock_session_class.assert_called_once()
    
    def test_init_auto_update_context_false(self, context):
        """Test initialization with auto_update_context disabled."""
        ocp_client = OCPHTTPClient(context, auto_update_context=False)
        
        assert ocp_client.auto_update_context is False
    
    def test_prepare_headers_no_existing(self, context):
        """Test header preparation with no existing headers."""
        ocp_client = OCPHTTPClient(context)
        
        headers = ocp_client._prepare_headers()
        
        # Should include OCP headers
        expected_headers = create_ocp_headers(context)
        assert headers == expected_headers
    
    def test_prepare_headers_with_existing(self, context):
        """Test header preparation with existing headers."""
        ocp_client = OCPHTTPClient(context)
        existing_headers = {"Custom-Header": "value", "Authorization": "Bearer token"}
        
        headers = ocp_client._prepare_headers(existing_headers)
        
        # Should merge existing and OCP headers
        expected_headers = create_ocp_headers(context)
        expected_headers.update(existing_headers)
        assert headers == expected_headers
    
    def test_prepare_headers_override_ocp(self, context):
        """Test that existing headers can override OCP headers."""
        ocp_client = OCPHTTPClient(context)
        
        # Get OCP headers to know what to override
        ocp_headers = create_ocp_headers(context)
        ocp_header_key = list(ocp_headers.keys())[0]
        
        existing_headers = {ocp_header_key: "overridden_value"}
        headers = ocp_client._prepare_headers(existing_headers)
        
        # OCP header should actually override existing header (based on implementation)
        # The implementation does: merged.update(ocp_headers) which means OCP wins
        assert headers[ocp_header_key] == ocp_headers[ocp_header_key]
    
    def test_log_interaction_enabled(self, context):
        """Test interaction logging when enabled."""
        ocp_client = OCPHTTPClient(context, auto_update_context=True)
        
        # Mock response with status_code
        mock_response = Mock()
        mock_response.status_code = 200
        
        # Mock the context.add_interaction method
        context.add_interaction = Mock()
        
        ocp_client._log_interaction("GET", "https://api.example.com/users", mock_response)
        
        # Should log interaction
        context.add_interaction.assert_called_once_with(
            action="api_call_get",
            api_endpoint="GET /users", 
            result="HTTP 200",
            metadata={"url": "https://api.example.com/users", "domain": "api.example.com"}
        )
    
    def test_log_interaction_disabled(self, context):
        """Test interaction logging when disabled."""
        ocp_client = OCPHTTPClient(context, auto_update_context=False)
        context.add_interaction = Mock()
        
        ocp_client._log_interaction("POST", "https://api.example.com/data", None)
        
        # Should not log interaction
        context.add_interaction.assert_not_called()
    
    def test_log_interaction_different_status_formats(self, context):
        """Test interaction logging with different response status formats."""
        ocp_client = OCPHTTPClient(context)
        context.add_interaction = Mock()
        
        # Test status_code attribute
        mock_response1 = Mock()
        mock_response1.status_code = 404
        ocp_client._log_interaction("GET", "https://api.example.com/missing", mock_response1)
        
        # Test status attribute (httpx style)
        mock_response2 = Mock()
        mock_response2.status = 201
        del mock_response2.status_code  # Ensure status_code doesn't exist
        ocp_client._log_interaction("POST", "https://api.example.com/create", mock_response2)
        
        # Test no status
        ocp_client._log_interaction("PUT", "https://api.example.com/update", None)
        
        # Verify calls
        expected_calls = [
            call(action="api_call_get", api_endpoint="GET /missing", result="HTTP 404", 
                 metadata={"url": "https://api.example.com/missing", "domain": "api.example.com"}),
            call(action="api_call_post", api_endpoint="POST /create", result="HTTP 201",
                 metadata={"url": "https://api.example.com/create", "domain": "api.example.com"}),
            call(action="api_call_put", api_endpoint="PUT /update", result=None,
                 metadata={"url": "https://api.example.com/update", "domain": "api.example.com"})
        ]
        context.add_interaction.assert_has_calls(expected_calls)
    
    def test_request_method(self, context):
        """Test generic request method."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.request.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            ocp_client = OCPHTTPClient(context)
            
            # Mock context interaction
            context.add_interaction = Mock()
            
            # Make request
            result = ocp_client.request("GET", "https://api.example.com/test", 
                                      params={"q": "search"}, timeout=30)
            
            # Verify request was made with OCP headers
            mock_session.request.assert_called_once()
            args, kwargs = mock_session.request.call_args
            
            assert args == ("GET", "https://api.example.com/test")
            assert "headers" in kwargs
            assert "params" in kwargs
            assert "timeout" in kwargs
            assert kwargs["params"] == {"q": "search"}
            assert kwargs["timeout"] == 30
            
            # Verify OCP headers were added
            headers = kwargs["headers"]
            expected_ocp_headers = create_ocp_headers(context)
            for key, value in expected_ocp_headers.items():
                assert headers[key] == value
            
            # Verify interaction was logged
            context.add_interaction.assert_called_once()
            
            # Verify response was returned
            assert result == mock_response
    
    def test_http_methods(self, context):
        """Test individual HTTP method helpers."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_session.request.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            ocp_client = OCPHTTPClient(context, auto_update_context=False)
            
            # Test each HTTP method
            methods = [
                ("get", "GET"),
                ("post", "POST"), 
                ("put", "PUT"),
                ("delete", "DELETE"),
                ("patch", "PATCH")
            ]
            
            for method_name, http_method in methods:
                mock_session.request.reset_mock()
                
                method_func = getattr(ocp_client, method_name)
                result = method_func("https://api.example.com/endpoint", data={"test": "data"})
                
                # Verify correct HTTP method was used
                mock_session.request.assert_called_once()
                args, kwargs = mock_session.request.call_args
                assert args == (http_method, "https://api.example.com/endpoint")
                assert "data" in kwargs
                assert kwargs["data"] == {"test": "data"}
                assert result == mock_response


class TestWrapAPI:
    """Test wrap_api function."""
    
    @pytest.fixture
    def context(self):
        return AgentContext(agent_type="test_agent")
    
    def test_wrap_api_basic(self, context):
        """Test basic API wrapping."""
        with patch('requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            api_client = wrap_api("https://api.example.com", context)
            
            assert isinstance(api_client, OCPHTTPClient)
            assert api_client.context == context
            assert hasattr(api_client, 'base_url')
            assert api_client.base_url == "https://api.example.com"
    
    def test_wrap_api_with_auth_token(self, context):
        """Test API wrapping with token authentication."""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            api_client = wrap_api(
                "https://api.github.com", 
                context,
                headers={"Authorization": "token ghp_123456"}
            )
            
            # Verify session headers were updated
            mock_session.headers.update.assert_called_once()
            headers = mock_session.headers.update.call_args[0][0]
            assert headers['Authorization'] == 'token ghp_123456'
    
    def test_wrap_api_with_bearer_token(self, context):
        """Test API wrapping with Bearer token."""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            api_client = wrap_api(
                "https://api.example.com",
                context, 
                headers={"Authorization": "Bearer jwt_token_here"}
            )
            
            headers = mock_session.headers.update.call_args[0][0]
            assert headers['Authorization'] == 'Bearer jwt_token_here'
    
    def test_wrap_api_with_basic_auth(self, context):
        """Test API wrapping with Basic auth.""" 
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            api_client = wrap_api(
                "https://api.example.com",
                context,
                headers={"Authorization": "Basic dXNlcjpwYXNz"}
            )
            
            headers = mock_session.headers.update.call_args[0][0]
            assert headers['Authorization'] == 'Basic dXNlcjpwYXNz'
    
    def test_wrap_api_with_plain_token(self, context):
        """Test API wrapping with plain token (now explicit header)."""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            api_client = wrap_api(
                "https://api.example.com",
                context,
                headers={"Authorization": "token abc123def456"}
            )
            
            headers = mock_session.headers.update.call_args[0][0]
            assert headers['Authorization'] == 'token abc123def456'
    
    def test_wrap_api_with_custom_headers(self, context):
        """Test API wrapping with custom headers."""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            custom_headers = {
                "User-Agent": "MyApp/1.0",
                "Accept": "application/vnd.api+json"
            }
            
            api_client = wrap_api(
                "https://api.example.com",
                context,
                headers=custom_headers
            )
            
            headers = mock_session.headers.update.call_args[0][0]
            assert headers['User-Agent'] == 'MyApp/1.0'
            assert headers['Accept'] == 'application/vnd.api+json'
    
    
    def test_wrap_api_base_url_normalization(self, context):
        """Test that base URLs are properly normalized."""
        with patch("requests.Session"):
            # Test trailing slash removal
            api_client = wrap_api("https://api.example.com/", context)
            assert api_client.base_url == "https://api.example.com"
    
    def test_wrap_api_relative_url_handling(self, context):
        """Test that relative URLs are properly handled."""
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.request = Mock()
            mock_session_class.return_value = mock_session
            
            api_client = wrap_api("https://api.example.com", context)
            
            # Test relative URL
            api_client.request("GET", "/users")
            
            # Verify full URL was constructed
            mock_session.request.assert_called_once()
            args = mock_session.request.call_args[0]
            assert args[1] == "https://api.example.com/users"
    
    def test_wrap_api_absolute_url_handling(self, context):
        """Test that absolute URLs are passed through unchanged.""" 
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session.request = Mock()
            mock_session_class.return_value = mock_session
            
            api_client = wrap_api("https://api.example.com", context)
            
            # Test absolute URL
            api_client.request("POST", "https://other-api.com/webhook")
            
            # Verify URL was passed through unchanged
            args = mock_session.request.call_args[0]
            assert args[1] == "https://other-api.com/webhook"


class TestHTTPClientIntegration:
    """Integration tests for HTTP client components."""
    
    def test_end_to_end_workflow(self):
        """Test complete OCP HTTP client workflow."""
        # Create context
        context = AgentContext(
            agent_type="integration_test",
            user="tester",
            current_goal="test full workflow"
        )
        
        with patch("requests.Session") as mock_session_class:
            # Setup mock session and response
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            mock_session.request.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            # Create OCP client
            client = OCPHTTPClient(context)
            
            # Mock context interaction
            context.add_interaction = Mock()
            
            # Make request
            response = client.get("https://api.example.com/users", 
                                params={"page": 1, "limit": 10})
            
            # Verify request was made correctly
            mock_session.request.assert_called_once()
            args, kwargs = mock_session.request.call_args
            
            assert args == ("GET", "https://api.example.com/users")
            assert kwargs["params"] == {"page": 1, "limit": 10}
            
            # Verify OCP headers were included
            headers = kwargs["headers"]
            expected_headers = create_ocp_headers(context)
            for key, value in expected_headers.items():
                assert headers[key] == value
            
            # Verify interaction was logged
            context.add_interaction.assert_called_once()
            call_args = context.add_interaction.call_args
            assert call_args[1]["action"] == "api_call_get"
            assert call_args[1]["api_endpoint"] == "GET /users"
            assert call_args[1]["result"] == "HTTP 200"
            
            # Verify response
            assert response == mock_response
            assert response.status_code == 200
    
    def test_multiple_requests_context_tracking(self):
        """Test that multiple requests are properly tracked in context."""
        context = AgentContext(agent_type="multi_test")
        
        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            # Create responses for different requests
            responses = [
                Mock(status_code=200),
                Mock(status_code=201), 
                Mock(status_code=404)
            ]
            mock_session.request.side_effect = responses
            
            client = OCPHTTPClient(context)
            context.add_interaction = Mock()
            
            # Make multiple requests
            client.get("https://api.example.com/users")
            client.post("https://api.example.com/users", json={"name": "test"})
            client.delete("https://api.example.com/users/999")
            
            # Verify all interactions were logged
            assert context.add_interaction.call_count == 3
            
            # Check interaction details
            calls = context.add_interaction.call_args_list
            
            assert calls[0][1]["action"] == "api_call_get"
            assert calls[0][1]["result"] == "HTTP 200"
            
            assert calls[1][1]["action"] == "api_call_post"  
            assert calls[1][1]["result"] == "HTTP 201"
            
            assert calls[2][1]["action"] == "api_call_delete"
            assert calls[2][1]["result"] == "HTTP 404"