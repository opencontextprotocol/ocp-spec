---
title: "OpenAPI Parsing"
weight: 1
---

OCP's schema discovery engine processes OpenAPI specifications (v3.0+) to extract API operations and convert them into callable agent tools.

## Parsing Process

### 1. Specification Fetching

```python
# From URL
spec = discovery.fetch_spec("https://api.github.com/openapi.json")

# From local file  
spec = discovery.load_spec("./my-api.yaml")

# From registry (pre-cached)
spec = registry.get_spec("github")
```

### 2. Specification Validation

OCP validates the OpenAPI specification structure:

```python
def validate_spec(spec_data):
    """Validate OpenAPI specification"""
    required_fields = ['openapi', 'info', 'paths']
    
    for field in required_fields:
        if field not in spec_data:
            raise SchemaError(f"Missing required field: {field}")
    
    # Validate OpenAPI version
    version = spec_data.get('openapi', '')
    if not version.startswith('3.'):
        raise SchemaError(f"Unsupported OpenAPI version: {version}")
    
    return True
```

### 3. Base URL Extraction

OCP determines the API base URL from the specification:

```python
def extract_base_url(spec, base_url_override=None):
    """Extract API base URL"""
    
    # 1. Use override if provided
    if base_url_override:
        return base_url_override
    
    # 2. Use first server URL
    servers = spec.get('servers', [])
    if servers and servers[0].get('url'):
        return servers[0]['url']
    
    # 3. Fallback
    raise SchemaError("No base URL found")
```

### 4. Path Processing

Extract operations from the OpenAPI paths section:

```python
def parse_paths(spec):
    """Parse OpenAPI paths into operations"""
    paths = spec.get('paths', {})
    operations = []
    
    for path_pattern, path_item in paths.items():
        # Skip non-operation entries
        if not isinstance(path_item, dict):
            continue
            
        # Process each HTTP method
        for method, operation in path_item.items():
            if method.lower() in HTTP_METHODS:
                operations.append({
                    'path': path_pattern,
                    'method': method.upper(),
                    'operation': operation
                })
    
    return operations
```

## Specification Examples

### Simple API
```yaml
openapi: 3.0.0
info:
  title: Simple API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      responses:
        '200':
          description: List of users
    post:
      operationId: createUser
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
```

**Generated Tools:**
- `list_users()` - GET /users
- `create_user(name, email)` - POST /users

### Complex API with Parameters
```yaml
paths:
  /repos/{owner}/{repo}/issues:
    get:
      operationId: listIssues
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
        - name: state
          in: query
          schema:
            type: string
            enum: [open, closed, all]
            default: open
        - name: labels
          in: query
          schema:
            type: string
      responses:
        '200':
          description: List of issues
```

**Generated Tool:**
```python
def list_issues(owner: str, repo: str, state: str = "open", labels: str = None):
    """List repository issues"""
    # Auto-generated with parameter validation
```

## Error Handling

### Invalid Specifications
```python
def handle_invalid_spec(spec_url, error):
    """Handle parsing errors gracefully"""
    logger.warning(f"Failed to parse {spec_url}: {error}")
    
    # Return empty spec instead of failing
    return OCPAPISpec(
        base_url="",
        title="Invalid API", 
        version="unknown",
        description=f"Failed to parse: {error}",
        tools=[],
        raw_spec={}
    )
```

### Missing Operations
```python
def parse_operation_safe(path, method, operation):
    """Safely parse operation with error handling"""
    try:
        return parse_operation(path, method, operation)
    except Exception as e:
        logger.warning(f"Skipping invalid operation {method} {path}: {e}")
        return None
```

## Caching Strategy

### Specification Caching
```python
class SpecCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, spec_url):
        """Get cached specification"""
        entry = self.cache.get(spec_url)
        if entry and not self._is_expired(entry):
            return entry['spec']
        return None
    
    def put(self, spec_url, spec):
        """Cache specification"""
        self.cache[spec_url] = {
            'spec': spec,
            'timestamp': time.time()
        }
```

### Tool Caching
```python
def get_cached_tools(spec_url):
    """Get cached tools for a specification"""
    cache_key = f"tools:{hash(spec_url)}"
    return cache.get(cache_key)

def cache_tools(spec_url, tools):
    """Cache generated tools"""
    cache_key = f"tools:{hash(spec_url)}"
    cache.set(cache_key, tools, ttl=3600)
```

## Performance Optimizations

### Lazy Loading
```python
def discover_tools_lazy(spec_url):
    """Lazy tool discovery"""
    spec = fetch_spec(spec_url)  # Fast metadata fetch
    
    def generate_tools():
        return parse_tools(spec)   # Heavy processing on demand
    
    return APIProxy(spec, generate_tools)
```

### Parallel Processing
```python
def parse_operations_parallel(paths):
    """Parse operations in parallel"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                future = executor.submit(parse_operation, path, method, operation)
                futures.append(future)
        
        tools = []
        for future in as_completed(futures):
            tool = future.result()
            if tool:
                tools.append(tool)
        
        return tools
```

## Supported OpenAPI Features

### ✅ Supported
- **OpenAPI 3.0+**: Full support for OpenAPI 3.0 and 3.1
- **HTTP Methods**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- **Parameters**: Path, query, header parameters
- **Request Bodies**: JSON, form data, file uploads
- **Response Schemas**: JSON response validation
- **Authentication**: API keys, bearer tokens, OAuth
- **Tags**: Organization and filtering
- **Operation IDs**: Custom function naming

### ⚠️ Partial Support
- **OpenAPI 2.0**: Basic support, but recommend upgrading to 3.0+
- **XML Responses**: Supported but converted to JSON
- **Complex Authentication**: Multi-step auth flows require manual handling

### ❌ Not Supported
- **Webhooks**: OCP is for client-side API calls
- **Callbacks**: Not applicable to agent tool generation
- **Links**: Not used in tool generation