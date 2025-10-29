"""
OCP Agent - Context-Aware API Discovery and Execution

Combines OCP's context management with automatic API discovery,
providing intelligent API interactions with zero infrastructure.
"""

import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .context import AgentContext
from .schema_discovery import OCPSchemaDiscovery, OCPAPISpec, OCPTool
from .http_client import OCPHTTPClient
from .registry import OCPRegistry
from .storage import OCPStorage


class OCPAgent:
    """
    OCP Agent for Context-Aware API Interactions
    
    Provides:
    1. API Discovery (from OpenAPI specs or community registry) 
    2. Tool Invocation (with parameter validation)
    3. Context Management (persistent across calls)
    4. Local Storage (optional caching and session persistence)
    5. Zero Infrastructure (no servers required)
    """
    
    def __init__(self, 
                 agent_type: str = "ai_agent",
                 user: Optional[str] = None,
                 workspace: Optional[str] = None,
                 agent_goal: Optional[str] = None,
                 registry_url: Optional[str] = None,
                 enable_cache: bool = True):
        """
        Initialize OCP Agent with context and schema discovery.
        
        Args:
            agent_type: Type of AI agent (e.g., "ide_coding_assistant")
            user: User identifier
            workspace: Current workspace/project
            agent_goal: Current objective or goal
            registry_url: Custom registry URL (uses OCP_REGISTRY_URL env var or default if None)
            enable_cache: Enable local caching of API specs (default: True)
        """
        self.context = AgentContext(
            agent_type=agent_type,
            user=user,
            workspace=workspace,
            current_goal=agent_goal
        )
        self.discovery = OCPSchemaDiscovery()
        self.registry = OCPRegistry(registry_url)
        self.storage = OCPStorage() if enable_cache else None
        self.known_apis: Dict[str, OCPAPISpec] = {}
        self.http_client = OCPHTTPClient(self.context)
    
    def register_api(self, name: str, spec_url: Optional[str] = None, base_url: Optional[str] = None) -> OCPAPISpec:
        """
        Register an API for discovery and usage.
        
        Lookup chain: Memory → Cache → Registry → Network
        
        Args:
            name: Human-readable name for the API or registry API name
            spec_url: URL to OpenAPI specification (optional if using registry lookup)
            base_url: Optional override for API base URL
            
        Returns:
            Discovered API specification with available tools
            
        Examples:
            # Registry lookup (fast)
            agent.register_api('github')
            
            # Direct OpenAPI discovery
            agent.register_api('my-api', 'https://api.example.com/openapi.json')
        """
        # 1. Check if already loaded in memory
        if name in self.known_apis:
            return self.known_apis[name]
        
        # 2. Check local cache (if enabled)
        if self.storage:
            cached_spec = self.storage.get_cached_api(name, max_age_days=7)
            if cached_spec:
                self.known_apis[name] = cached_spec
                self.context.add_api_spec(name, "cache")
                return cached_spec
        
        # 3. Fetch from registry or OpenAPI spec
        if spec_url:
            # Direct OpenAPI discovery
            api_spec = self.discovery.discover_api(spec_url, base_url)
            source = spec_url
        else:
            # Registry lookup
            api_spec = self.registry.get_api_spec(name, base_url)
            source = f"registry:{name}"
        
        # Store API spec in memory
        self.known_apis[name] = api_spec
        
        # Cache to disk (if enabled)
        if self.storage:
            self.storage.cache_api(name, api_spec, metadata={"source": source})
        
        # Add to context's API specs
        self.context.add_api_spec(name, source)
        
        # Log API registration
        self.context.add_interaction(
            action="api_registered",
            api_endpoint=source,
            result=f"Discovered {len(api_spec.tools)} tools",
            metadata={
                'api_name': name,
                'api_title': api_spec.title,
                'tool_count': len(api_spec.tools),
                'base_url': api_spec.base_url,
                'source': 'registry' if not spec_url else 'openapi'
            }
        )
        
        return api_spec
    
    def list_tools(self, api_name: Optional[str] = None) -> List[OCPTool]:
        """
        List available tools.
        
        Args:
            api_name: Optional API name to filter tools
            
        Returns:
            List of available tools
        """
        if api_name:
            if api_name not in self.known_apis:
                raise ValueError(f"Unknown API: {api_name}")
            return self.known_apis[api_name].tools
        
        # Return tools from all APIs
        all_tools = []
        for api_spec in self.known_apis.values():
            all_tools.extend(api_spec.tools)
        
        return all_tools
    
    def get_tool(self, tool_name: str, api_name: Optional[str] = None) -> Optional[OCPTool]:
        """
        Get specific tool by name.
        
        Args:
            tool_name: Name of the tool to find
            api_name: Optional API name to search within
            
        Returns:
            Found tool or None
        """
        tools = self.list_tools(api_name)
        
        for tool in tools:
            if tool.name == tool_name:
                return tool
        
        return None
    
    def search_tools(self, query: str, api_name: Optional[str] = None) -> List[OCPTool]:
        """
        Search tools by name or description.
        
        Args:
            query: Search query
            api_name: Optional API name to search within
            
        Returns:
            List of matching tools
        """
        if api_name:
            if api_name not in self.known_apis:
                return []
            return self.discovery.search_tools(self.known_apis[api_name], query)
        
        # Search across all APIs
        matches = []
        for api_spec in self.known_apis.values():
            matches.extend(self.discovery.search_tools(api_spec, query))
        
        return matches
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any] = None, 
                  api_name: Optional[str] = None) -> requests.Response:
        """
        Call a discovered tool with OCP context injection.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters for the tool call
            api_name: Optional API name if tool name is ambiguous
            
        Returns:
            HTTP response from the API call
        """
        parameters = parameters or {}
        
        # Find the tool
        tool = self.get_tool(tool_name, api_name)
        if not tool:
            available_tools = [t.name for t in self.list_tools(api_name)]
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")
        
        # Find the API spec for this tool
        api_spec = None
        for spec in self.known_apis.values():
            if tool in spec.tools:
                api_spec = spec
                break
        
        if not api_spec:
            raise ValueError(f"Could not find API spec for tool '{tool_name}'")
        
        # Validate parameters
        validation_errors = self._validate_parameters(tool, parameters)
        if validation_errors:
            raise ValueError(f"Parameter validation failed: {validation_errors}")
        
        # Build request
        url, request_params = self._build_request(api_spec, tool, parameters)
        
        # Log the tool call
        self.context.add_interaction(
            action=f"tool_call:{tool_name}",
            api_endpoint=url,
            result="executing",
            metadata={
                'tool_name': tool_name,
                'parameters': parameters,
                'method': tool.method
            }
        )
        
        # Make the request with OCP context enhancement
        try:
            response = self.http_client.request(tool.method, url, **request_params)
            
            # Log the result
            self.context.add_interaction(
                action=f"tool_response:{tool_name}",
                api_endpoint=url,
                result=f"{response.status_code} {response.reason}",
                metadata={
                    'status_code': response.status_code,
                    'success': response.ok,
                    'response_size': len(response.content) if response.content else 0
                }
            )
            
            return response
            
        except Exception as e:
            # Log the error
            self.context.add_interaction(
                action=f"tool_error:{tool_name}",
                api_endpoint=url,
                result=f"Error: {str(e)}",
                metadata={
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            )
            raise
    
    def _validate_parameters(self, tool: OCPTool, parameters: Dict[str, Any]) -> List[str]:
        """Validate parameters against tool schema."""
        errors = []
        
        # Check required parameters
        for param_name, param_info in tool.parameters.items():
            if param_info.get('required', False) and param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
        
        # Check parameter types (basic validation)
        for param_name, value in parameters.items():
            if param_name in tool.parameters:
                param_info = tool.parameters[param_name]
                expected_type = param_info.get('type', 'string')
                
                # Basic type checking
                if expected_type == 'integer' and not isinstance(value, int):
                    errors.append(f"Parameter '{param_name}' should be integer, got {type(value).__name__}")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Parameter '{param_name}' should be boolean, got {type(value).__name__}")
                elif expected_type == 'array' and not isinstance(value, list):
                    errors.append(f"Parameter '{param_name}' should be array, got {type(value).__name__}")
        
        return errors
    
    def _build_request(self, api_spec: OCPAPISpec, tool: OCPTool, 
                      parameters: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Build HTTP request from tool and parameters."""
        
        # Start with base URL and path
        url = api_spec.base_url.rstrip('/') + tool.path
        
        # Separate parameters by location
        path_params = {}
        query_params = {}
        body_params = {}
        header_params = {}
        
        for param_name, value in parameters.items():
            if param_name in tool.parameters:
                location = tool.parameters[param_name].get('location', 'query')
                
                if location == 'path':
                    path_params[param_name] = value
                elif location == 'query':
                    query_params[param_name] = value
                elif location == 'body':
                    body_params[param_name] = value
                elif location == 'header':
                    header_params[param_name] = value
        
        # Replace path parameters
        for param_name, value in path_params.items():
            url = url.replace(f'{{{param_name}}}', str(value))
        
        # Build request parameters
        request_params = {}
        
        if query_params:
            request_params['params'] = query_params
        
        if body_params:
            request_params['json'] = body_params
        
        if header_params:
            request_params['headers'] = header_params
        
        # Set timeout
        request_params['timeout'] = 30
        
        return url, request_params
    
    def get_tool_documentation(self, tool_name: str, api_name: Optional[str] = None) -> str:
        """Get documentation for a specific tool."""
        tool = self.get_tool(tool_name, api_name)
        if not tool:
            return f"Tool '{tool_name}' not found"
        
        return self.discovery.generate_tool_documentation(tool)
    
    def update_goal(self, goal: str, summary: Optional[str] = None):
        """Update agent goal and context."""
        self.context.update_goal(goal, summary)