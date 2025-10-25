"""
OCP Error Hierarchy

Consistent error handling for the Open Context Protocol library.
Provides specific exception types for different failure scenarios.
"""

from typing import List, Optional


class OCPError(Exception):
    """Base exception for all OCP-related errors."""
    pass


class RegistryUnavailable(OCPError):
    """Registry service is unreachable or returned an error."""
    
    def __init__(self, registry_url: str, message: str = None):
        self.registry_url = registry_url
        if message is None:
            full_message = f"Registry unavailable at {registry_url}. Use spec_url for direct discovery."
        else:
            full_message = f"Registry unavailable at {registry_url}: {message}"
        super().__init__(full_message)


class APINotFound(OCPError):
    """API not found in the registry."""
    
    def __init__(self, api_name: str, suggestions: Optional[List[str]] = None):
        self.api_name = api_name
        self.suggestions = suggestions or []
        
        message = f"API '{api_name}' not found in registry"
        if suggestions:
            message += f". Did you mean: {', '.join(suggestions[:3])}?"
        super().__init__(message)


class SchemaDiscoveryError(OCPError):
    """OpenAPI schema discovery and parsing errors."""
    pass


class ValidationError(OCPError):
    """Context or parameter validation errors."""
    pass