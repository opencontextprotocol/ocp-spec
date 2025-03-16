---
title: Base Protocol
cascade:
  type: docs
weight: 2
---

{{< callout type="info" >}} Protocol Revision: draft {{< /callout >}}

The Open Context Protocol (OCP) defines a structured approach for managing AI model context  
across applications. The protocol consists of multiple layers, allowing implementations  
to choose the features that best fit their needs.

## Core Components

OCP is designed with modularity in mind, consisting of the following primary components:

- Context Objects: Standardized structure for representing AI model context.
- Lifecycle Management: Handling of context creation, updates, and expiration.
- Transports: Mechanisms for transmitting context over HTTP, WebSockets, and gRPC.
- Security & Integrity: Authentication, message signing, and access control.

Each of these components is detailed in separate sections of the specification.

## Message Format

OCP does not mandate a specific messaging protocol but defines a standardized  
context object format that can be passed between applications.

| Field        | Type     | Required | Description                        |
|-------------|---------|----------|------------------------------------|
| `context_id` | String  | `✅ Yes`  | Unique identifier for the context |
| `metadata`  | Object  | `❌ No`   | Optional metadata for applications |
| `session`   | Object  | `✅ Yes`  | Contextual data (e.g., chat history) |
| `expires`   | String  | `❌ No`   | Expiration timestamp (ISO 8601) |

## Learn More

For further details, refer to:
- [Lifecycle](basic/lifecycle.md)
- [Messages](basic/messages.md)
- [Transports](basic/transports.md)
- [Security](basic/security.md)
