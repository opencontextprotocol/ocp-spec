"""
HTTP Client Enhancement - Make HTTP requests OCP-enabled.

Provides a simple HTTP client that automatically adds OCP context
headers to all requests.
"""

import functools
from typing import Dict, Any, Optional, Union, Callable
from urllib.parse import urlparse

from .context import AgentContext
from .headers import create_ocp_headers, extract_context_from_response


class OCPHTTPClient:
    """
    OCP-enabled HTTP client.
    
    Automatically adds OCP context headers to all requests and tracks
    interactions in the agent context.
    """
    
    def __init__(
        self, 
        context: AgentContext,
        auto_update_context: bool = True
    ):
        """
        Initialize OCP HTTP client.
        
        Args:
            context: Agent context to include in requests
            auto_update_context: Whether to automatically update context with interactions
        """
        self.context = context
        self.auto_update_context = auto_update_context
        
        # Use requests as our HTTP client
        import requests
        self.http_client = requests.Session()
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers with OCP context."""
        ocp_headers = create_ocp_headers(self.context)
        
        if headers:
            # Merge with existing headers
            merged = headers.copy()
            merged.update(ocp_headers)
            return merged
        
        return ocp_headers
    
    def _log_interaction(self, method: str, url: str, response: Any = None) -> None:
        """Log the API interaction in context."""
        if not self.auto_update_context:
            return
        
        # Parse API endpoint
        parsed = urlparse(url)
        endpoint = f"{method.upper()} {parsed.path}"
        
        # Get response status if available
        result = None
        if response and hasattr(response, 'status_code'):
            result = f"HTTP {response.status_code}"
        elif response and hasattr(response, 'status'):
            result = f"HTTP {response.status}"
        
        # Add to context history
        self.context.add_interaction(
            action=f"api_call_{method.lower()}",
            api_endpoint=endpoint,
            result=result,
            metadata={"url": url, "domain": parsed.netloc}
        )
    
    def request(self, method: str, url: str, **kwargs) -> Any:
        """Make an HTTP request with OCP context."""
        # Prepare headers
        headers = kwargs.get('headers', {})
        kwargs['headers'] = self._prepare_headers(headers)
        
        # Make request
        response = self.http_client.request(method, url, **kwargs)
        
        # Log interaction
        self._log_interaction(method, url, response)
        
        return response
    
    def get(self, url: str, **kwargs) -> Any:
        """Make a GET request with OCP context."""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Any:
        """Make a POST request with OCP context."""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Any:
        """Make a PUT request with OCP context."""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Any:
        """Make a DELETE request with OCP context."""
        return self.request('DELETE', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Any:
        """Make a PATCH request with OCP context.""" 
        return self.request('PATCH', url, **kwargs)


def wrap_api(
    base_url: str, 
    context: AgentContext,
    headers: Optional[Dict[str, str]] = None
) -> OCPHTTPClient:
    """
    Create an OCP-enabled client for a specific API.
    
    Args:
        base_url: Base URL for the API (e.g., "https://api.github.com")
        context: Agent context to include in requests
        headers: Additional headers to include in all requests
        
    Returns:
        OCP-enabled API client
        
    Example:
        >>> from ocp_agent import AgentContext, wrap_api
        >>> 
        >>> context = AgentContext(agent_type="debug_assistant")
        >>> github = wrap_api(
        ...     "https://api.github.com",
        ...     context,
        ...     headers={"Authorization": "token ghp_your_token"}
        ... )
        >>> issues = github.get("/search/issues", params={"q": "bug"})
    """
    # Set up base headers
    base_headers = headers.copy() if headers else {}
    
    # Create HTTP client with base URL
    import requests
    session = requests.Session()
    session.headers.update(base_headers)
    
    # Create OCP client
    ocp_client = OCPHTTPClient(context)
    ocp_client.http_client = session
    
    # Store base URL for convenience
    ocp_client.base_url = base_url.rstrip('/')
    
    # Override methods to handle relative URLs
    original_request = ocp_client.request
    
    def request_with_base_url(method: str, url: str, **kwargs):
        if not url.startswith('http'):
            url = f"{ocp_client.base_url}{url}"
        return original_request(method, url, **kwargs)
    
    ocp_client.request = request_with_base_url
    
    return ocp_client