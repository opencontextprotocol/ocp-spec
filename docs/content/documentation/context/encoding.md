---
title: "Encoding & Compression"
weight: 3
---

The `OCP-Session` header uses a standardized encoding process to efficiently transmit context data while staying within HTTP header size limits.

## Encoding Process

### 1. JSON Serialization
Context objects are serialized to valid UTF-8 JSON:

```json
{
  "context_id": "ocp-debug-payment-abc123",
  "agent_type": "ide_coding_assistant",
  "current_goal": "debug_payment_validation_error",
  "workspace": "ecommerce-backend"
}
```

### 2. Optional Compression
For contexts larger than 1KB, apply gzip compression:

```python
import gzip
import json

context_json = json.dumps(context_obj)
compressed = gzip.compress(context_json.encode('utf-8'))
```

### 3. Base64 Encoding
Apply standard Base64 encoding (RFC 4648):

```python
import base64

encoded = base64.b64encode(compressed).decode('ascii')
# Result: eyJjb250ZXh0X2lkIjoib2NwLWRlYnVnLXBheW1lbnQtYWJjMTIzIn0=
```

### Complete Encoding Example

```python
import json
import gzip  
import base64

def encode_context(context_obj):
    """Encode context for OCP-Session header"""
    # 1. Serialize to JSON
    json_str = json.dumps(context_obj, separators=(',', ':'))
    
    # 2. Compress if beneficial
    json_bytes = json_str.encode('utf-8')
    if len(json_bytes) > 1024:  # Only compress if >1KB
        compressed = gzip.compress(json_bytes)
        # Use compressed if it's actually smaller
        to_encode = compressed if len(compressed) < len(json_bytes) else json_bytes
    else:
        to_encode = json_bytes
    
    # 3. Base64 encode
    encoded = base64.b64encode(to_encode).decode('ascii')
    
    return encoded
```

## Decoding Process

Reverse the encoding process to extract context:

```python
import json
import gzip
import base64

def decode_context(encoded_context):
    """Decode context from OCP-Session header"""
    try:
        # 1. Base64 decode
        decoded_bytes = base64.b64decode(encoded_context.encode('ascii'))
        
        # 2. Try to decompress (might not be compressed)
        try:
            decompressed = gzip.decompress(decoded_bytes)
            json_str = decompressed.decode('utf-8')
        except gzip.BadGzipFile:
            # Not compressed
            json_str = decoded_bytes.decode('utf-8')
        
        # 3. Parse JSON
        context_obj = json.loads(json_str)
        
        return context_obj
        
    except Exception as e:
        # Invalid context - ignore and continue
        return None
```

## Size Limits & Management

### Header Size Limits

**Maximum Header Size**: 8KB (8,192 bytes) after encoding  
**Recommended Size**: Under 4KB for optimal performance  
**Minimum Size**: ~100 bytes for basic context

### Size Management Strategies

**History Truncation**: Keep only recent interactions
```python
# Keep last 20 interactions
if len(context['history']) > 20:
    context['history'] = context['history'][-20:]
```

**Field Compression**: Use shorter field names for frequently used data
```python
# Instead of
context['current_file'] = 'payment_validator.py'

# Use abbreviations in internal representation
context['cf'] = 'payment_validator.py'
```

**Smart Compression**: Only compress when beneficial
```python
def should_compress(data):
    return len(data) > 1024 and estimate_compression_ratio(data) > 0.2
```

## Compression Efficiency

### When Compression Helps
- **Repeated Data**: Similar history entries
- **Verbose Fields**: Long descriptions or error messages  
- **Large Contexts**: >2KB uncompressed

### When Compression Doesn't Help
- **Small Contexts**: <500 bytes
- **Random Data**: Unique identifiers, hashes
- **Already Compressed**: Base64-encoded data

### Compression Ratio Examples

```python
# Good compression (repeated patterns)
context = {
    "history": [
        {"action": "api_call", "api": "github", "operation": "list_issues"},
        {"action": "api_call", "api": "github", "operation": "get_issue"},  
        {"action": "api_call", "api": "github", "operation": "list_commits"}
    ]
}
# Uncompressed: 312 bytes
# Compressed: 156 bytes (50% reduction)

# Poor compression (unique data)
context = {
    "context_id": "ocp-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "random_seed": "7f3e9c8b2a5d1f4e8c9b2a5d1f4e8c9b"
}
# Uncompressed: 205 bytes  
# Compressed: 198 bytes (3% reduction - not worth it)
```

## Error Handling

### Invalid Context Handling
APIs should gracefully handle invalid or missing context:

```python
def extract_context(headers):
    """Extract context with graceful error handling"""
    ocp_session = headers.get('OCP-Session')
    if not ocp_session:
        return None
        
    context = decode_context(ocp_session)
    if not context:
        # Log but don't fail the request
        logger.warning("Invalid OCP-Session header, ignoring")
        return None
        
    return context
```

### Size Limit Enforcement
Client libraries should enforce size limits:

```python
def validate_context_size(encoded_context):
    """Validate context doesn't exceed size limits"""
    if len(encoded_context.encode('utf-8')) > 8192:
        raise ValueError("Context exceeds 8KB limit")
```

### Compression Detection
Automatically detect if content is compressed:

```python
def is_gzipped(data):
    """Check if bytes are gzip compressed"""
    return data.startswith(b'\x1f\x8b\x08')
```