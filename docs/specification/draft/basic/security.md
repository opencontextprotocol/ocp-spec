---
title: Security
type: docs
weight: 60
---

{{< callout type="info" >}} Protocol Revision: draft {{< /callout >}}

The Open Context Protocol (OCP) provides flexible mechanisms for managing AI model context across applications.  
Security considerations depend on whether context is passed inline (stateless) or stored and retrieved (stateful).

## Authentication

OCP itself does not mandate an authentication mechanism, but when context is stored externally,  
clients MUST authenticate before retrieving or modifying context.

Implementations SHOULD support one or more of the following:
- OAuth 2.0 Bearer Tokens (for API-based retrieval)
- Mutual TLS (mTLS) (for secure service-to-service communication)
- Signed Requests (for tamper-proof context references)

For inline (stateless) context, authentication is implicit—only authorized systems should be  
able to generate and validate context objects.

## Message Integrity

To prevent tampering, stored context SHOULD include cryptographic signatures.

- HMAC-based Signing: A `signature` field MAY be included in stored contexts.
- Public-Key Cryptography: Implementations MAY use asymmetric signing (e.g., JWT-based signatures).

Example of a signed context:
```json
{
  "context_id": "123e4567-e89b-12d3-a456-426614174000",
  "metadata": { "user_id": "user-123" },
  "session": { "history": [ ... ] },
  "expires": "2025-03-16T12:00:00Z",
  "signature": "MEUCIQ..."
}
```

## Access Control

When retrieving stored context:
- Clients MUST have appropriate permissions to access a given `context_id`.
- Implementations SHOULD restrict access based on user identity, roles, and scopes.
- Sensitive metadata MAY be encrypted before storage.

## Context Expiration

OCP supports explicit expiration:
- A stored context MUST NOT be used beyond its `expires` timestamp.
- If an implementation supports revocation, it SHOULD provide an API to delete stored contexts.

## Learn More

For further details, refer to:
- [Lifecycle](basic/lifecycle.md)
- [Messages](basic/messages.md)
- [Transports](basic/transports.md)
