"""
Open Context Protocol (OCP) - Python Library

A zero-infrastructure protocol that provides conversational context
and automatic API discovery to enhance AI agent interactions.

Combines the best of MCP's API discovery with persistent context management,
requiring no servers or infrastructure setup.
"""

from .context import AgentContext, create_ide_agent, create_debug_agent, create_devops_agent
from .http_client import enhance_http_client, wrap_api, OCPHTTPClient
from .headers import OCPHeaders, create_ocp_headers, extract_context_from_response
from .schemas import validate_context
from .schema_discovery import OCPSchemaDiscovery, OCPTool, OCPAPISpec
from .agent import OCPAgent, create_github_agent, create_stripe_agent

__version__ = "0.1.0"
__all__ = [
    # Core context management
    "AgentContext",
    "create_ide_agent",
    "create_debug_agent", 
    "create_devops_agent",
    
    # HTTP client enhancement
    "enhance_http_client", 
    "wrap_api",
    "OCPHTTPClient",
    "OCPHeaders",
    "create_ocp_headers",
    "extract_context_from_response",
    "validate_context",
    
    # Schema discovery
    "OCPSchemaDiscovery",
    "OCPTool",
    "OCPAPISpec",
    
    # Complete agent with MCP parity
    "OCPAgent",
    "create_github_agent",
    "create_stripe_agent"
]