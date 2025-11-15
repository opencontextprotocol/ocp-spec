---
title: "HTTP Protocol"
weight: 1
---

# HTTP Protocol

The core OCP protocol uses standard HTTP headers to transmit context information without requiring server modifications or additional infrastructure.

## Header Specification

### Required Headers

#### `OCP-Context-ID`
- **Purpose**: Unique identifier for the agent session
- **Format**: 1-64 characters, alphanumeric + hyphens
- **Pattern**: `^[a-zA-Z0-9\-]{1,64}$`
- **Example**: `ocp-debug-payment-abc123`

```http
OCP-Context-ID: ocp-debug-payment-abc123
```

#### `OCP-Agent-Type`
- **Purpose**: Type of agent making the request  
- **Format**: 1-128 characters, descriptive identifier
- **Pattern**: `^[a-zA-Z0-9_\-\.]{1,128}$`
- **Examples**: `ide_coding_assistant`, `cli_tool`, `jupyter_notebook`

```http
OCP-Agent-Type: ide_coding_assistant
```

### Optional Headers

#### `OCP-Agent-Goal`
- **Purpose**: Current agent objective or task
- **Format**: 1-256 characters, human-readable description
- **Example**: `debug_payment_validation_error`

```http
OCP-Agent-Goal: debug_payment_validation_error
```

#### `OCP-Session`
- **Purpose**: Base64-encoded JSON context object
- **Format**: Base64-encoded string, max 8KB
- **Encoding**: UTF-8 JSON → optional gzip → Base64

```http
OCP-Session: eyJjb250ZXh0X2lkIjoib2NwLWRlYnVnLXBheW1lbnQtYWJjMTIzIn0=
```

#### `OCP-User`
- **Purpose**: User identifier for multi-user environments  
- **Format**: 1-64 characters, user identifier
- **Examples**: `alice`, `user123`, `dev-team-lead`

```http
OCP-User: alice
```

#### `OCP-Workspace`
- **Purpose**: Current workspace or project context
- **Format**: 1-128 characters, workspace identifier
- **Examples**: `ecommerce-backend`, `mobile-app`

```http
OCP-Workspace: ecommerce-backend
```

## Encoding Specification

### JSON Serialization
Context objects must be valid UTF-8 JSON:

```json
{
  "context_id": "ocp-debug-payment-abc123",
  "agent_type": "ide_coding_assistant",
  "current_goal": "debug_payment_validation_error"
}
```

### Compression Algorithm
1. **Threshold**: Apply gzip compression only if beneficial (>20% size reduction)
2. **Compression**: Use gzip with default compression level
3. **Detection**: Compressed data identified by gzip header (`\x1f\x8b`)

```python
def compress_context(json_str):
    json_bytes = json_str.encode('utf-8')
    if len(json_bytes) <= 1024:
        return json_bytes  # Skip compression for small contexts
    
    compressed = gzip.compress(json_bytes)
    # Only use compression if it provides significant benefit
    return compressed if len(compressed) < len(json_bytes) * 0.8 else json_bytes
```

### Base64 Encoding
Apply RFC 4648 standard Base64 encoding:

```python
encoded = base64.b64encode(data).decode('ascii')
```

### Size Limits
- **Maximum Header Size**: 8KB (8,192 bytes) after Base64 encoding
- **Recommended Size**: <4KB for optimal performance  
- **Minimum Size**: ~100 bytes for basic context

## HTTP Compatibility

### Infrastructure Requirements
OCP headers are standard HTTP headers that pass through all standard web infrastructure:

- **Web Servers**: Apache, Nginx, IIS
- **Load Balancers**: HAProxy, AWS ALB, Google LB
- **CDNs**: CloudFlare, AWS CloudFront, Azure CDN
- **API Gateways**: AWS API Gateway, Kong, Zuul
- **Proxies**: Squid, Varnish, corporate proxies

### Header Processing Rules

#### Client Behavior
```http
GET /api/resource HTTP/1.1
Host: api.example.com
Authorization: Bearer token123
OCP-Context-ID: ocp-session-abc123
OCP-Agent-Type: ide_assistant
OCP-Session: eyJjb250ZXh0X2lkIjoib2NwLXNlc3Npb24tYWJjMTIzIn0=
```

#### Server Behavior
**Level 1 (Context Aware)**:
- Server MAY read OCP headers
- Server MUST process request normally if OCP headers are invalid/missing
- Server MUST NOT fail requests due to OCP header issues

**Level 2 (Context Enhanced)**:
- Server MAY provide enhanced responses based on context
- Server MUST gracefully fallback to Level 1 behavior

## Error Handling Specification

### Invalid Headers
```python
def process_ocp_headers(headers):
    """Process OCP headers with graceful error handling"""
    try:
        context_id = headers.get('OCP-Context-ID')
        if context_id and not validate_context_id(context_id):
            logger.warning(f"Invalid OCP-Context-ID: {context_id}")
            context_id = None
            
        return extract_context_safe(headers)
    except Exception as e:
        logger.warning(f"Failed to process OCP headers: {e}")
        return None  # Continue processing without context
```

### Size Violations
```python
def validate_header_size(encoded_session):
    """Validate OCP-Session header size"""
    if len(encoded_session.encode('utf-8')) > 8192:
        raise ValueError("OCP-Session header exceeds 8KB limit")
```

### Malformed Context
```python
def decode_session_safe(encoded_session):
    """Safely decode OCP-Session with error handling"""
    try:
        decoded = base64.b64decode(encoded_session)
        
        # Try decompression
        try:
            if decoded.startswith(b'\x1f\x8b'):  # gzip header
                decoded = gzip.decompress(decoded)
        except gzip.BadGzipFile:
            pass  # Not compressed
            
        return json.loads(decoded.decode('utf-8'))
    except Exception:
        return None  # Invalid session data
```

## Performance Considerations

### Header Size Optimization
- **History Truncation**: Limit history to recent entries
- **Field Abbreviation**: Use short field names for internal data
- **Selective Compression**: Only compress when beneficial

### Caching Strategy
```python
class ContextCache:
    """Cache parsed context to avoid repeated parsing"""
    
    def get_context(self, context_id, encoded_session):
        cache_key = f"{context_id}:{hash(encoded_session)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        context = decode_session_safe(encoded_session)
        self.cache[cache_key] = context
        return context
```

### Network Efficiency
- **Header Reuse**: Context persists across multiple requests
- **Incremental Updates**: Only send changed context fields
- **Compression**: Reduce bandwidth for large contexts

## Security Model

### Privacy Protection
- **No Sensitive Data**: Never include passwords, tokens, or secrets
- **User Data**: Minimize personally identifiable information
- **Workspace Isolation**: Context scoped to current workspace/session

### Validation Rules
```python
def validate_context_security(context):
    """Validate context doesn't contain sensitive data"""
    sensitive_patterns = [
        r'password', r'secret', r'token', r'key',
        r'auth', r'credential', r'private'
    ]
    
    context_str = json.dumps(context).lower()
    for pattern in sensitive_patterns:
        if re.search(pattern, context_str):
            logger.warning(f"Potential sensitive data in context: {pattern}")
```

### Logging Considerations
```python
def sanitize_headers_for_logging(headers):
    """Remove sensitive headers from logs"""
    safe_headers = headers.copy()
    # Log OCP headers but truncate session data
    if 'OCP-Session' in safe_headers:
        safe_headers['OCP-Session'] = safe_headers['OCP-Session'][:50] + '...'
    return safe_headers
```