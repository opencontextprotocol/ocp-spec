"""Tests for OCP CLI main functionality."""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from ocp_cli.main import OCPCli, RegistryClient


class TestRegistryClient:
    """Test RegistryClient functionality."""
    
    def test_client_initialization(self):
        """Test registry client initializes with correct base URL."""
        client = RegistryClient("https://registry.example.com")
        assert client.base_url == "https://registry.example.com"
    
    def test_client_strips_trailing_slash(self):
        """Test registry client strips trailing slash from URL."""
        client = RegistryClient("https://registry.example.com/")
        assert client.base_url == "https://registry.example.com"
    
    @patch('ocp_cli.main.requests.get')
    def test_list_apis(self, mock_get):
        """Test listing APIs from registry."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "test-api", "display_name": "Test API"}
        ]
        mock_get.return_value = mock_response
        
        client = RegistryClient("https://registry.example.com")
        result = client.list_apis()
        
        assert len(result) == 1
        assert result[0]["name"] == "test-api"
        mock_get.assert_called_once()
    
    @patch('ocp_cli.main.requests.get')
    def test_list_apis_with_filters(self, mock_get):
        """Test listing APIs with category and status filters."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        client = RegistryClient("https://registry.example.com")
        client.list_apis(category="development", status="active")
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['category'] == "development"
        assert call_args[1]['params']['status'] == "active"
    
    @patch('ocp_cli.main.requests.get')
    def test_get_api(self, mock_get):
        """Test getting specific API details."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "test-api",
            "display_name": "Test API",
            "tools": []
        }
        mock_get.return_value = mock_response
        
        client = RegistryClient("https://registry.example.com")
        result = client.get_api("test-api")
        
        assert result["name"] == "test-api"
        mock_get.assert_called_once_with(
            "https://registry.example.com/api/v1/registry/test-api"
        )


class TestOCPCli:
    """Test OCPCli main class functionality."""
    
    def test_cli_initialization(self):
        """Test CLI initializes correctly."""
        cli = OCPCli()
        assert cli is not None
    
    @patch('ocp_cli.main.RegistryClient')
    def test_get_registry_client_default_url(self, mock_client):
        """Test getting registry client with default URL."""
        cli = OCPCli()
        cli._get_registry_client()
        
        mock_client.assert_called_once_with("http://localhost:8000")
    
    @patch('ocp_cli.main.RegistryClient')
    def test_get_registry_client_custom_url(self, mock_client):
        """Test getting registry client with custom URL."""
        cli = OCPCli()
        cli._get_registry_client("https://custom.registry.com")
        
        mock_client.assert_called_once_with("https://custom.registry.com")
    
    @patch('ocp_cli.main.RegistryClient')
    @patch('builtins.print')
    def test_registry_list_full_output(self, mock_print, mock_client_class):
        """Test registry list with full output."""
        mock_client = Mock()
        mock_client.list_apis.return_value = [
            {
                "name": "test-api",
                "display_name": "Test API",
                "description": "A test API",
                "tools": []
            }
        ]
        mock_client_class.return_value = mock_client
        
        cli = OCPCli()
        cli.registry_list(summary=False)
        
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        data = json.loads(output)
        assert len(data) == 1
        assert "tools" in data[0]  # Full output includes tools
    
    @patch('ocp_cli.main.RegistryClient')
    @patch('builtins.print')
    def test_registry_list_summary_output(self, mock_print, mock_client_class):
        """Test registry list with summary output."""
        mock_client = Mock()
        mock_client.list_apis.return_value = [
            {
                "name": "test-api",
                "display_name": "Test API",
                "description": "A test API",
                "tools": [],
                "auth_config": {}
            }
        ]
        mock_client_class.return_value = mock_client
        
        cli = OCPCli()
        cli.registry_list(summary=True)
        
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        data = json.loads(output)
        assert len(data) == 1
        assert "name" in data[0]
        assert "display_name" in data[0]
        assert "description" in data[0]
        assert "tools" not in data[0]  # Summary excludes tools
        assert "auth_config" not in data[0]  # Summary excludes auth_config
    
    @patch('ocp_cli.main.RegistryClient')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_registry_list_connection_error(self, mock_exit, mock_print, mock_client_class):
        """Test registry list handles connection errors."""
        mock_client = Mock()
        mock_client.list_apis.side_effect = ConnectionError("Connection refused")
        mock_client_class.return_value = mock_client
        
        cli = OCPCli()
        cli.registry_list()
        
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        data = json.loads(output)
        assert "error" in data
        mock_exit.assert_called_once_with(1)
