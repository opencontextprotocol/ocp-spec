---
title: Encoding Rules
weight: 3
---

The `OCP-Session` header contains context data that must be properly encoded for HTTP transmission.

## Encoding Process

1. **JSON Serialization**: Context must be valid UTF-8 JSON
2. **Compression**: Optional gzip compression before Base64 encoding (recommended for large contexts)
3. **Base64 Encoding**: Standard Base64 encoding (RFC 4648)
4. **Header Transmission**: Include as `OCP-Session` header value

## Size Limits

- **Maximum Size**: 8KB for `OCP-Session` header after encoding
- **Recommended Size**: Under 4KB for optimal performance
- **Minimum Size**: No minimum, can be empty JSON object `{}`

## Error Handling

**Invalid Context**: APIs should ignore invalid OCP headers and process requests normally

**Oversized Context**: Headers exceeding limits should be truncated or ignored

**Missing Context**: APIs work normally without OCP headers (backward compatibility)

## Example

```python
import json
import base64
import gzip

# Context object
context = {
    "context_id": "ocp-abc123",
    "agent_type": "coding_assistant",
    "current_goal": "debug_payment_issue"
}

# Serialize to JSON
json_data = json.dumps(context).encode('utf-8')

# Optional compression for large contexts
compressed = gzip.compress(json_data)

# Base64 encode
encoded = base64.b64encode(compressed).decode('ascii')

# Use in HTTP header
headers = {
    'OCP-Session': encoded,
    'OCP-Context-ID': 'ocp-abc123',
    'OCP-Agent-Type': 'coding_assistant'
}
```

## Security Considerations

- **No Sensitive Data**: Never include passwords, tokens, or secrets in context
- **Size Limits**: Enforce header size limits to prevent abuse
- **Logging**: Consider context privacy when logging HTTP requests
- **Validation**: Validate context structure but don't fail requests on invalid context