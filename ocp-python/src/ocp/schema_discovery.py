"""
OCP Schema Discovery

Provides automatic API discovery and tool generation from OpenAPI specifications,
enabling context-aware API interactions with zero infrastructure requirements.
"""

import json
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from urllib.parse import urljoin

@dataclass
class OCPTool:
    """Represents a discovered API tool/endpoint"""
    name: str
    description: str
    method: str
    path: str
    parameters: Dict[str, Any]
    response_schema: Dict[str, Any]
    operation_id: Optional[str] = None
    tags: List[str] = None

@dataclass 
class OCPAPISpec:
    """Represents a parsed OpenAPI specification"""
    base_url: str
    title: str
    version: str
    description: str
    tools: List[OCPTool]
    raw_spec: Dict[str, Any]

class OCPSchemaDiscovery:
    """
    Automatic API discovery and tool generation from OpenAPI specifications.
    
    This enables automatic API discovery while maintaining OCP's zero-infrastructure
    approach by parsing OpenAPI specs directly.
    """
    
    def __init__(self):
        self.cached_specs: Dict[str, OCPAPISpec] = {}
    
    def discover_api(self, spec_url: str, base_url: Optional[str] = None) -> OCPAPISpec:
        """
        Discover API capabilities from OpenAPI specification.
        
        Args:
            spec_url: URL to OpenAPI specification (JSON or YAML)
            base_url: Optional override for API base URL
            
        Returns:
            OCPAPISpec with discovered tools and capabilities
        """
        # Check cache first
        if spec_url in self.cached_specs:
            return self.cached_specs[spec_url]
        
        # Fetch and parse OpenAPI spec
        spec_data = self._fetch_spec(spec_url)
        parsed_spec = self._parse_openapi_spec(spec_data, base_url)
        
        # Cache for future use
        self.cached_specs[spec_url] = parsed_spec
        
        return parsed_spec
    
    def _fetch_spec(self, spec_url: str) -> Dict[str, Any]:
        """Fetch OpenAPI specification from URL"""
        try:
            response = requests.get(spec_url, timeout=30)
            response.raise_for_status()
            
            # Try JSON first, then YAML
            try:
                return response.json()
            except json.JSONDecodeError:
                # Try YAML if json fails (requires yaml package)
                try:
                    import yaml
                    return yaml.safe_load(response.text)
                except ImportError:
                    raise Exception("YAML spec detected but PyYAML not installed. Install with: pip install PyYAML")
                
        except Exception as e:
            raise Exception(f"Failed to fetch OpenAPI spec from {spec_url}: {e}")
    
    def _parse_openapi_spec(self, spec_data: Dict[str, Any], base_url_override: Optional[str] = None) -> OCPAPISpec:
        """Parse OpenAPI specification into OCP tools"""
        
        # Extract basic info
        info = spec_data.get('info', {})
        title = info.get('title', 'Unknown API')
        version = info.get('version', '1.0.0')
        description = info.get('description', '')
        
        # Determine base URL
        base_url = base_url_override
        if not base_url:
            servers = spec_data.get('servers', [])
            if servers:
                base_url = servers[0].get('url', '')
            else:
                base_url = ''
        
        # Parse paths into tools
        tools = []
        paths = spec_data.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'patch', 'delete']:
                    tool = self._create_tool_from_operation(
                        path, method.upper(), operation
                    )
                    if tool:
                        tools.append(tool)
        
        return OCPAPISpec(
            base_url=base_url,
            title=title,
            version=version,
            description=description,
            tools=tools,
            raw_spec=spec_data
        )
    
    def _create_tool_from_operation(self, path: str, method: str, operation: Dict[str, Any]) -> Optional[OCPTool]:
        """Create OCP tool from OpenAPI operation"""
        
        # Generate tool name
        operation_id = operation.get('operationId')
        if operation_id:
            tool_name = operation_id
        else:
            # Generate name from path and method
            clean_path = path.replace('/', '_').replace('{', '').replace('}', '')
            tool_name = f"{method.lower()}{clean_path}"
        
        # Get description
        description = operation.get('summary', '') or operation.get('description', '')
        if not description:
            description = f"{method} {path}"
        
        # Parse parameters
        parameters = self._parse_parameters(operation.get('parameters', []))
        
        # Add request body parameters for POST/PUT/PATCH
        if method in ['POST', 'PUT', 'PATCH'] and 'requestBody' in operation:
            body_params = self._parse_request_body(operation['requestBody'])
            parameters.update(body_params)
        
        # Parse response schema
        response_schema = self._parse_responses(operation.get('responses', {}))
        
        # Get tags
        tags = operation.get('tags', [])
        
        return OCPTool(
            name=tool_name,
            description=description,
            method=method,
            path=path,
            parameters=parameters,
            response_schema=response_schema,
            operation_id=operation_id,
            tags=tags
        )
    
    def _parse_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse OpenAPI parameters into tool parameter schema"""
        parsed_params = {}
        
        for param in parameters:
            name = param.get('name')
            if not name:
                continue
            
            param_schema = {
                'description': param.get('description', ''),
                'required': param.get('required', False),
                'location': param.get('in', 'query'),  # query, path, header, cookie
                'type': 'string'  # Default type
            }
            
            # Extract type from schema
            schema = param.get('schema', {})
            if schema:
                param_schema['type'] = schema.get('type', 'string')
                if 'enum' in schema:
                    param_schema['enum'] = schema['enum']
                if 'format' in schema:
                    param_schema['format'] = schema['format']
            
            parsed_params[name] = param_schema
        
        return parsed_params
    
    def _parse_request_body(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Parse request body into parameters"""
        parameters = {}
        
        content = request_body.get('content', {})
        
        # Look for JSON content first
        json_content = content.get('application/json', {})
        if json_content and 'schema' in json_content:
            schema = json_content['schema']
            
            # Handle object schemas
            if schema.get('type') == 'object':
                properties = schema.get('properties', {})
                required_fields = schema.get('required', [])
                
                for prop_name, prop_schema in properties.items():
                    parameters[prop_name] = {
                        'description': prop_schema.get('description', ''),
                        'required': prop_name in required_fields,
                        'location': 'body',
                        'type': prop_schema.get('type', 'string')
                    }
                    
                    if 'enum' in prop_schema:
                        parameters[prop_name]['enum'] = prop_schema['enum']
        
        return parameters
    
    def _parse_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Parse response schemas"""
        response_schema = {}
        
        # Look for successful response (200, 201, etc.)
        for status_code, response in responses.items():
            if str(status_code).startswith('2'):  # 2xx success codes
                content = response.get('content', {})
                json_content = content.get('application/json', {})
                
                if json_content and 'schema' in json_content:
                    response_schema = json_content['schema']
                    break
        
        return response_schema
    
    def get_tools_by_tag(self, api_spec: OCPAPISpec, tag: str) -> List[OCPTool]:
        """Get tools filtered by tag"""
        return [tool for tool in api_spec.tools if tag in (tool.tags or [])]
    
    def search_tools(self, api_spec: OCPAPISpec, query: str) -> List[OCPTool]:
        """Search tools by name or description"""
        query_lower = query.lower()
        matches = []
        
        for tool in api_spec.tools:
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matches.append(tool)
        
        return matches
    
    def generate_tool_documentation(self, tool: OCPTool) -> str:
        """Generate human-readable documentation for a tool"""
        doc_lines = [
            f"## {tool.name}",
            f"**Method:** {tool.method}",
            f"**Path:** {tool.path}",
            f"**Description:** {tool.description}",
            ""
        ]
        
        if tool.parameters:
            doc_lines.append("### Parameters:")
            for param_name, param_info in tool.parameters.items():
                required = " (required)" if param_info.get('required') else " (optional)"
                location = f" [{param_info.get('location', 'query')}]"
                doc_lines.append(f"- **{param_name}**{required}{location}: {param_info.get('description', '')}")
            doc_lines.append("")
        
        if tool.tags:
            doc_lines.append(f"**Tags:** {', '.join(tool.tags)}")
            doc_lines.append("")
        
        return "\n".join(doc_lines)
    
    def clear_cache(self):
        """Clear cached API specifications"""
        self.cached_specs.clear()