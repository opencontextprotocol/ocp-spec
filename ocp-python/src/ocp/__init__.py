"""
Open Context Protocol (OCP) - Zero-infrastructure context for AI agents.

OCP enables AI agents to share context across API calls using standard HTTP headers.
Built specifically for IDE coding assistants, DevOps agents, and agentic workflows.
"""

from .context import AgentContext, create_ide_agent, create_debug_agent, create_devops_agent
from .http_client import enhance_http_client, wrap_api
from .headers import OCPHeaders, create_ocp_headers, extract_context_from_response
from .schemas import validate_context

__version__ = "0.1.0"
__all__ = [
    "AgentContext",
    "create_ide_agent",
    "create_debug_agent", 
    "create_devops_agent",
    "enhance_http_client", 
    "wrap_api",
    "OCPHeaders",
    "create_ocp_headers",
    "extract_context_from_response",
    "validate_context",
]