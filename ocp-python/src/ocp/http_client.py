"""
HTTP Client Enhancement - Make any HTTP client OCP-enabled.

Provides wrapper functions and classes to automatically add OCP context
headers to HTTP requests using popular Python HTTP libraries.
"""

import functools
from typing import Dict, Any, Optional, Union, Callable
from urllib.parse import urlparse

from .context import AgentContext
from .headers import create_ocp_headers, extract_context_from_response


class OCPHTTPClient:
    """
    Universal OCP-enabled HTTP client that wraps existing HTTP libraries.
    
    Automatically adds OCP context headers to all requests and tracks
    interactions in the agent context.
    """
    
    def __init__(
        self, 
        context: AgentContext,
        http_client: Any = None,
        auto_update_context: bool = True
    ):
        """
        Initialize OCP HTTP client.
        
        Args:
            context: Agent context to include in requests
            http_client: Underlying HTTP client (requests.Session, httpx.Client, etc.)
            auto_update_context: Whether to automatically update context with interactions
        """
        self.context = context
        self.http_client = http_client
        self.auto_update_context = auto_update_context
        
        # If no client provided, use requests as default
        if http_client is None:
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
        
        # Make request using underlying client
        if hasattr(self.http_client, 'request'):
            response = self.http_client.request(method, url, **kwargs)
        else:
            # Fallback for function-based clients
            response = self.http_client(method, url, **kwargs)
        
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


def enhance_http_client(http_client: Any, context: AgentContext) -> OCPHTTPClient:
    """
    Enhance an existing HTTP client with OCP context capabilities.
    
    Args:
        http_client: Existing HTTP client (requests.Session, httpx.Client, etc.)
        context: Agent context to include in requests
        
    Returns:
        OCP-enhanced HTTP client
        
    Example:
        >>> import requests
        >>> from ocp import AgentContext, enhance_http_client
        >>> 
        >>> context = AgentContext(agent_type="ide_copilot")
        >>> github = enhance_http_client(requests, context)
        >>> response = github.get("https://api.github.com/user")
    """
    return OCPHTTPClient(context, http_client)


def wrap_api(
    base_url: str, 
    context: AgentContext,
    auth: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    http_client: Any = None
) -> OCPHTTPClient:
    """
    Create an OCP-enabled client for a specific API.
    
    Args:
        base_url: Base URL for the API (e.g., "https://api.github.com")
        context: Agent context to include in requests
        auth: Authorization header value (e.g., "token ghp_xxx", "Bearer jwt_token")
        headers: Additional headers to include in all requests
        http_client: Underlying HTTP client to use
        
    Returns:
        OCP-enabled API client
        
    Example:
        >>> from ocp import AgentContext, wrap_api
        >>> 
        >>> context = AgentContext(agent_type="debug_assistant")
        >>> github = wrap_api(
        ...     "https://api.github.com",
        ...     context,
        ...     auth="token ghp_your_token"
        ... )
        >>> issues = github.get("/search/issues", params={"q": "bug"})
    """
    # Set up base headers
    base_headers = headers.copy() if headers else {}
    
    if auth:
        if auth.startswith(('token ', 'Bearer ', 'Basic ')):
            base_headers['Authorization'] = auth
        else:
            # Assume it's a token
            base_headers['Authorization'] = f'token {auth}'
    
    # Create HTTP client with base URL
    if http_client is None:
        import requests
        session = requests.Session()
        session.headers.update(base_headers)
        http_client = session
    
    # Create OCP client
    ocp_client = OCPHTTPClient(context, http_client)
    
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


def create_requests_patch(context: AgentContext) -> Callable:
    """
    Create a patch for the requests library to automatically add OCP headers.
    
    This function returns a decorator that can be used to patch requests.request
    or applied globally.
    
    Args:
        context: Agent context to include in all requests
        
    Returns:
        Decorator function that adds OCP headers to requests
        
    Example:
        >>> import requests
        >>> from ocp import AgentContext, create_requests_patch
        >>> 
        >>> context = AgentContext(agent_type="ide_copilot")
        >>> patch = create_requests_patch(context)
        >>> 
        >>> # Apply to specific requests
        >>> @patch
        >>> def make_api_call():
        ...     return requests.get("https://api.github.com/user")
        >>> 
        >>> # Or monkey-patch globally (use with caution)
        >>> requests.request = patch(requests.request)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Add OCP headers to the request
            headers = kwargs.get('headers', {})
            ocp_headers = create_ocp_headers(context)
            kwargs['headers'] = {**headers, **ocp_headers}
            
            # Make the request
            response = func(*args, **kwargs)
            
            # Log interaction if it's an HTTP request
            if len(args) >= 2:  # method, url
                method, url = args[0], args[1]
                context.add_interaction(
                    action=f"api_call_{method.lower()}",
                    api_endpoint=f"{method.upper()} {urlparse(url).path}",
                    result=f"HTTP {response.status_code}" if hasattr(response, 'status_code') else None
                )
            
            return response
        return wrapper
    return decorator


def create_httpx_patch(context: AgentContext) -> Callable:
    """
    Create a patch for the httpx library to automatically add OCP headers.
    
    Similar to create_requests_patch but for the httpx library.
    
    Args:
        context: Agent context to include in all requests
        
    Returns:
        Decorator function that adds OCP headers to httpx requests
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Add OCP headers
            headers = kwargs.get('headers', {})
            ocp_headers = create_ocp_headers(context)
            kwargs['headers'] = {**headers, **ocp_headers}
            
            response = func(*args, **kwargs)
            
            # Log interaction
            if len(args) >= 2:
                method, url = args[0], args[1]
                context.add_interaction(
                    action=f"api_call_{method.lower()}",
                    api_endpoint=f"{method.upper()} {urlparse(url).path}",
                    result=f"HTTP {response.status_code}" if hasattr(response, 'status_code') else None
                )
            
            return response
        return wrapper
    return decorator