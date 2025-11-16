---
title: "Tool Generation"
weight: 2
---

OCP converts OpenAPI operations into callable Python/JavaScript functions with automatic parameter validation and request building.

## Tool Structure

Each generated tool contains:

```python
@dataclass
class OCPTool:
    name: str                    # Function name (e.g., "create_issue")
    description: str             # Human-readable description
    method: str                  # HTTP method ("GET", "POST", etc.)
    path: str                    # API path pattern ("/repos/{owner}/{repo}/issues")
    parameters: Dict[str, Any]   # Parameter schema with validation rules
    response_schema: Dict[str, Any]  # Expected response structure
    operation_id: Optional[str]  # Original OpenAPI operationId
    tags: List[str]              # OpenAPI tags for organization
```

## Generation Process

### 1. Operation Extraction

Extract operations from OpenAPI paths:

```python
def extract_operations(spec):
    """Extract all operations from OpenAPI spec"""
    operations = []
    paths = spec.get('paths', {})
    
    for path_pattern, path_item in paths.items():
        for method, operation in path_item.items():
            if method.lower() in ['get', 'post', 'put', 'patch', 'delete']:
                operations.append({
                    'path': path_pattern,
                    'method': method.upper(),
                    'operation': operation
                })
    
    return operations
```

### 2. Tool Name Generation

Generate deterministic function names:

```python
def generate_tool_name(method, path, operation):
    """Generate deterministic tool name"""
    
    # 1. Use operationId if available
    if 'operationId' in operation:
        return operation['operationId']
    
    # 2. Generate from method + path
    # Examples:
    # GET /users → get_users
    # POST /repos/{owner}/{repo}/issues → post_repos_owner_repo_issues
    # DELETE /users/{id} → delete_users_id
    
    name_parts = [method.lower()]
    
    # Process path segments
    path_segments = path.strip('/').split('/')
    for segment in path_segments:
        if segment.startswith('{') and segment.endswith('}'):
            # Parameter: {owner} → owner
            param_name = segment[1:-1]
            name_parts.append(param_name)
        else:
            # Literal: users → users
            name_parts.append(segment)
    
    return '_'.join(name_parts)
```

### 3. Parameter Processing

Extract and validate parameters from the operation:

```python
def extract_parameters(operation):
    """Extract parameters from OpenAPI operation"""
    parameters = {}
    
    # Path parameters
    path_params = operation.get('parameters', [])
    for param in path_params:
        if param.get('in') == 'path':
            parameters[param['name']] = {
                'type': param.get('schema', {}).get('type', 'string'),
                'required': param.get('required', False),
                'location': 'path',
                'description': param.get('description', ''),
                'schema': param.get('schema', {})
            }
    
    # Query parameters
    for param in path_params:
        if param.get('in') == 'query':
            parameters[param['name']] = {
                'type': param.get('schema', {}).get('type', 'string'),
                'required': param.get('required', False),
                'location': 'query',
                'description': param.get('description', ''),
                'schema': param.get('schema', {})
            }
    
    # Request body parameters
    request_body = operation.get('requestBody')
    if request_body:
        body_params = extract_request_body_params(request_body)
        parameters.update(body_params)
    
    return parameters
```

### 4. Request Body Processing

Handle JSON request bodies:

```python
def extract_request_body_params(request_body):
    """Extract parameters from request body"""
    parameters = {}
    
    content = request_body.get('content', {})
    json_content = content.get('application/json')
    
    if not json_content:
        return parameters
    
    schema = json_content.get('schema', {})
    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])
    
    for field_name, field_schema in properties.items():
        parameters[field_name] = {
            'type': field_schema.get('type', 'string'),
            'required': field_name in required_fields,
            'location': 'body',
            'description': field_schema.get('description', ''),
            'schema': field_schema
        }
    
    return parameters
```

### 5. Response Schema Extraction

Extract expected response format:

```python
def extract_response_schema(operation):
    """Extract response schema from operation"""
    responses = operation.get('responses', {})
    
    # Look for successful response (200, 201, etc.)
    for status_code, response in responses.items():
        if status_code.startswith('2'):
            content = response.get('content', {})
            json_content = content.get('application/json')
            
            if json_content and 'schema' in json_content:
                return json_content['schema']
    
    return None
```

## Generated Tool Examples

### Simple GET Operation

**OpenAPI Definition:**
```yaml
paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      responses:
        '200':
          description: List of users
```

**Generated Tool:**
```python
def list_users():
    """List all users"""
    url = build_url("/users")
    response = http_client.get(url)
    return parse_response(response)
```

### Complex POST Operation

**OpenAPI Definition:**
```yaml
paths:
  /repos/{owner}/{repo}/issues:
    post:
      operationId: createIssue
      summary: Create an issue
      parameters:
        - name: owner
          in: path
          required: true
          schema:
            type: string
        - name: repo
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                body:
                  type: string
                labels:
                  type: array
                  items:
                    type: string
              required:
                - title
```

**Generated Tool:**
```python
def create_issue(owner: str, repo: str, title: str, body: str = None, labels: List[str] = None):
    """Create an issue
    
    Args:
        owner (str): Repository owner (required)
        repo (str): Repository name (required)  
        title (str): Issue title (required)
        body (str): Issue description (optional)
        labels (List[str]): Issue labels (optional)
    
    Returns:
        dict: Created issue object
    """
    # Validate required parameters
    validate_required_params({'owner': owner, 'repo': repo, 'title': title})
    
    # Build URL with path parameters
    url = build_url(f"/repos/{owner}/{repo}/issues")
    
    # Build request body
    request_body = {'title': title}
    if body is not None:
        request_body['body'] = body
    if labels is not None:
        request_body['labels'] = labels
    
    # Make request with context headers
    response = http_client.post(url, json=request_body)
    return parse_response(response)
```

## Tool Documentation Generation

Generate human-readable documentation:

```python
def generate_tool_documentation(tool):
    """Generate documentation for a tool"""
    doc = f"## {tool.name}\n\n"
    doc += f"**Method:** {tool.method}\n"
    doc += f"**Path:** {tool.path}\n"
    doc += f"**Description:** {tool.description}\n\n"
    
    if tool.parameters:
        doc += "### Parameters:\n"
        for name, param in tool.parameters.items():
            required = " (required)" if param['required'] else " (optional)"
            location = f" [{param['location']}]"
            doc += f"- **{name}**{required}{location}: {param.get('description', '')}\n"
        doc += "\n"
    
    if tool.tags:
        doc += f"**Tags:** {', '.join(tool.tags)}\n\n"
    
    return doc
```

## Tool Execution

Execute tools with validation and context injection:

```python
def execute_tool(tool, **kwargs):
    """Execute a tool with parameter validation"""
    
    # 1. Validate parameters
    validate_parameters(tool.parameters, kwargs)
    
    # 2. Build URL
    url = build_url_with_params(tool.path, kwargs)
    
    # 3. Build request body
    body = build_request_body(tool.parameters, kwargs)
    
    # 4. Add context headers
    headers = build_context_headers()
    
    # 5. Make request
    response = http_client.request(
        method=tool.method,
        url=url,
        json=body,
        headers=headers
    )
    
    # 6. Parse response
    return parse_response(response, tool.response_schema)
```

## Error Handling

Handle tool generation and execution errors:

```python
def generate_tool_safe(path, method, operation):
    """Safely generate tool with error handling"""
    try:
        return generate_tool(path, method, operation)
    except Exception as e:
        logger.warning(f"Failed to generate tool for {method} {path}: {e}")
        return None

def execute_tool_safe(tool, **kwargs):
    """Safely execute tool with error handling"""
    try:
        return execute_tool(tool, **kwargs)
    except ValidationError as e:
        raise ValueError(f"Parameter validation failed: {e}")
    except HTTPError as e:
        raise APIError(f"API call failed: {e}")
```

## Performance Optimizations

### Tool Caching
```python
@lru_cache(maxsize=1000)
def generate_cached_tool(operation_hash):
    """Cache generated tools"""
    return generate_tool(operation_hash)
```

### Lazy Documentation
```python
class OCPTool:
    def __init__(self, ...):
        self._documentation = None
    
    @property
    def documentation(self):
        """Generate documentation on demand"""
        if self._documentation is None:
            self._documentation = generate_tool_documentation(self)
        return self._documentation
```