"""
OCP Registry Client

Provides access to the OCP Community Registry for pre-discovered API specifications.
Enables fast API registration without OpenAPI spec parsing.
"""

import os
import requests
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from .schema_discovery import OCPAPISpec, OCPTool
from .errors import RegistryUnavailable, APINotFound


class OCPRegistry:
    """
    Registry client for pre-discovered API specifications.
    
    Provides fast API lookup from the OCP Community Registry, which stores
    pre-parsed OpenAPI specifications as ready-to-use tool collections.
    """
    
    def __init__(self, registry_url: Optional[str] = None):
        """
        Initialize registry client.
        
        Args:
            registry_url: Registry base URL. Falls back to OCP_REGISTRY_URL env var,
                         then default public registry.
        """
        self.registry_url = (
            registry_url or 
            os.getenv('OCP_REGISTRY_URL', 'https://registry.ocp.dev')
        ).rstrip('/')
        
        # Validate URL format
        if not self.registry_url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid registry URL: {self.registry_url}")
    
    def get_api_spec(self, name: str, base_url: Optional[str] = None) -> OCPAPISpec:
        """
        Get pre-discovered API specification from registry.
        
        Args:
            name: API name in registry (e.g., 'github', 'stripe')
            base_url: Override base URL for API calls
            
        Returns:
            OCPAPISpec with pre-discovered tools
            
        Raises:
            RegistryUnavailable: Registry service unreachable
            APINotFound: API not found in registry
        """
        try:
            # Get API entry from registry
            response = requests.get(
                urljoin(self.registry_url, f'/api/v1/registry/{name}'),
                timeout=10
            )
            
            if response.status_code == 404:
                # Try to get suggestions
                suggestions = self._get_suggestions(name)
                raise APINotFound(name, suggestions)
            
            response.raise_for_status()
            api_entry = response.json()
            
            # Convert registry entry to OCPAPISpec
            return self._entry_to_spec(api_entry, base_url)
            
        except requests.exceptions.RequestException as e:
            raise RegistryUnavailable(self.registry_url, str(e))
    
    def search_apis(self, query: str) -> List[str]:
        """
        Search available APIs for suggestions.
        
        Args:
            query: Search query
            
        Returns:
            List of API names matching query
        """
        try:
            response = requests.get(
                urljoin(self.registry_url, '/api/v1/search'),
                params={'q': query, 'per_page': 10},
                timeout=5
            )
            response.raise_for_status()
            
            search_results = response.json()
            return [result['name'] for result in search_results.get('results', [])]
            
        except requests.exceptions.RequestException:
            # If search fails, return empty list (non-critical)
            return []
    
    def list_apis(self) -> List[str]:
        """
        List all available APIs in registry.
        
        Returns:
            List of API names
        """
        try:
            response = requests.get(
                urljoin(self.registry_url, '/api/v1/registry'),
                timeout=10
            )
            response.raise_for_status()
            
            apis = response.json()
            return [api['name'] for api in apis]
            
        except requests.exceptions.RequestException:
            return []
    
    def _entry_to_spec(self, api_entry: Dict[str, Any], base_url_override: Optional[str] = None) -> OCPAPISpec:
        """Convert registry API entry to OCPAPISpec."""
        
        # Use override base_url if provided, otherwise use registry's base_url
        base_url = base_url_override or api_entry.get('base_url', '')
        
        # Convert tools from registry format to OCPTool objects
        tools = []
        if api_entry.get('tools'):
            for tool_dict in api_entry['tools']:
                tool = OCPTool(
                    name=tool_dict['name'],
                    description=tool_dict['description'],
                    method=tool_dict['method'],
                    path=tool_dict['path'],
                    parameters=tool_dict.get('parameters', {}),
                    response_schema=tool_dict.get('response_schema', {}),
                    operation_id=tool_dict.get('operation_id'),
                    tags=tool_dict.get('tags', [])
                )
                tools.append(tool)
        
        # Create OCPAPISpec (matching dataclass field order)
        return OCPAPISpec(
            base_url=base_url,
            title=api_entry.get('display_name', api_entry['name']),
            version='1.0.0',  # Registry doesn't store version
            description=api_entry.get('description', ''),
            tools=tools,
            raw_spec=api_entry  # Store the original registry entry
        )
    
    def _get_suggestions(self, api_name: str) -> List[str]:
        """Get API name suggestions for error messages."""
        # Try exact search first
        suggestions = self.search_apis(api_name)
        
        # If no results, try partial matches
        if not suggestions and len(api_name) > 2:
            suggestions = self.search_apis(api_name[:3])
        
        return suggestions[:3]  # Limit to 3 suggestions