---
title: Messages
type: docs
weight: 40
---

{{< callout type="info" >}} Protocol Revision: draft {{< /callout >}}

OCP defines a structured format for passing context between applications.  
Contexts can be embedded within messages or referenced via identifiers.

## Context Object

An OCP context object MUST be a structured JSON object containing:

- `context_id` (string, required) – A unique identifier for the context.
- `metadata` (object, optional) – Arbitrary key-value metadata.
- `session` (object, required) – Contains contextual information (e.g., conversation history).
- `expires` (timestamp, optional) – Defines when the context MUST NOT be used.

### Example Context Object
```json
{
  "context_id": "123e4567-e89b-12d3-a456-426614174000",
  "metadata": {
    "application": "example-app",
    "user_id": "user-123"
  },
  "session": {
    "history": [
      { "role": "user", "message": "Translate this text." },
      { "role": "assistant", "message": "Here is the translation..." }
    ]
  },
  "expires": "2025-03-16T12:00:00Z"
}
```

## Context Transmission

OCP does not mandate a specific transport but defines the following transmission methods:

### Inline Context (Stateless Mode)

Contexts MAY be included directly in requests, such as:

- HTTP Headers
  ```http
  OCP-Context: eyJjb250ZXh0X2lkIjoiMTIz... (base64-encoded JSON)
  ```
- JSON Payload
  ```json
  {
    "context": {}
  }
  ```
- WebSockets / gRPC Metadata
  ```protobuf
  message Request {
    string context_id = 1;
    Context session = 2;
  }
  ```

### Stored Context (Stateful Mode)

If a context is persisted, clients MUST reference it via `context_id`:
```http
GET /context/123e4567
Authorization: Bearer YOUR-API-KEY
```
The response MUST return the full context object.

## Error Handling

If a context is unavailable or invalid, implementations MUST return an appropriate error:

```http
404 Not Found

{
  "error": "Context not found",
  "context_id": "123e4567"
}
```

## Learn More

For further details, refer to:
- [Lifecycle](basic/lifecycle.md)
- [Transports](basic/transports.md)
- [Security](basic/security.md)
