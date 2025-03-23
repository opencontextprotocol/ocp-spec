---
title: Storage
type: docs
weight: 65
---

{{< callout type="info" >}} Protocol Revision: {{< param protocolRevision >}} {{< /callout >}}

The Open Context Protocol (OCP) supports optional context storage for scenarios that require context to persist beyond a single request or session.

OCP does **not** require any centralized infrastructure. Instead, it defines a **retrieval interface** that may be implemented locally (e.g., with SQLite) or remotely (e.g., S3 or HTTP APIs), allowing flexibility across environments.

## ContextStore Interface

Implementations that support context persistence **SHOULD** implement the following interface or equivalent:

```go
type ContextStore interface {
    GetContext(ctx context.Context, id string) (*Context, error)
    SaveContext(ctx context.Context, c *Context) error
    DeleteContext(ctx context.Context, id string) error
}
```

This interface allows storage to be swapped out or extended without breaking compatibility across implementations.

## Supported Backends

The interface can be implemented using a variety of storage systems, including but not limited to:

- SQLite: Ideal for local-first applications that require persistence without external dependencies.
- S3: Recommended for distributed environments that need durable and scalable storage.
- In-Memory: Suitable for ephemeral, high-speed session-based use.
- Remote API: Implementations may expose the interface over HTTP or gRPC if needed.

## Example Implementations

| Backend | Use Case | Notes |
|---------|----------|-------|
| SQLite | Local development & desktop apps | Easy to bundle and deploy |
| S3 | Cloud-native deployments | Globally scalable |
| In-Memory | Temporary/test scenarios | Data lost on restart |
| HTTP API | Multi-service coordination | Useful in microservices |

## Context Identifiers

Stored context MUST be identified using a `context_id`. It is strongly recommended to use [UUIDv4](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.4) to ensure global uniqueness.

## Stateless Compatibility

Even when storage is used, OCP recommends that context be passed inline when possible. This ensures compatibility with stateless workflows and preserves OCP’s zero-infrastructure philosophy.

# Learn More

For further details, refer to:
- [Lifecycle](basic/lifecycle.md)
- [Messages](basic/messages.md)
- [Transports](basic/transports.md)
