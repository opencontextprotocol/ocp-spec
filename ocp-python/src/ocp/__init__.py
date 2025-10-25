"""
Open Context Protocol (OCP) - Python Library

A zero-infrastructure protocol that provides conversational context
and automatic API discovery to enhance AI agent interactions.

Enables persistent context sharing across HTTP API calls using standard headers,
requiring no servers or infrastructure setup.
"""

from .context import AgentContext
from .http_client import enhance_http_client, wrap_api, OCPHTTPClient
from .headers import OCPHeaders, create_ocp_headers, extract_context_from_response, parse_context, add_context_headers
from .validation import validate_context
from .schema_discovery import OCPSchemaDiscovery, OCPTool, OCPAPISpec
from .agent import OCPAgent

__version__ = "0.1.0"
__all__ = [
    # Core context management
    "AgentContext",
    
    # HTTP client enhancement
    "enhance_http_client", 
    "wrap_api",
    "OCPHTTPClient",
    "OCPHeaders",
    "create_ocp_headers",
    "extract_context_from_response",
    "validate_context",
    
    # Convenience functions for cleaner API
    "parse_context",
    "add_context_headers",
    
    # Schema discovery
    "OCPSchemaDiscovery",
    "OCPTool",
    "OCPAPISpec",
    
    # Complete agent functionality
    "OCPAgent"
]