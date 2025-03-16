---
title: Specification (Latest)
cascade:
  type: docs
breadcrumbs: false
weight: 10
aliases:
  - /latest
---

{{< callout type="info" >}} Protocol Revision: {{< param protocolRevision >}} {{< /callout >}}

The Open Context Protocol (OCP) is a zero-infrastructure protocol for managing AI model context across applications. It defines a lightweight, standardized mechanism for passing, persisting, and retrieving context across different systems, enabling seamless interoperability without requiring dedicated infrastructure.

This specification uses the key terms MUST, MUST NOT, SHOULD, and MAY as defined in [RFC2119](https://datatracker.ietf.org/doc/html/rfc2119).

### Key Details

- Enables structured context sharing across AI applications.
- Supports multiple transport layers, including HTTP headers, WebSockets, and gRPC.
- Stateless-first, with optional external storage for long-lived interactions.
- Designed to be lightweight, extensible, and transport-agnostic.

### Security Considerations

To ensure context integrity and privacy, OCP:
- Requires authentication for stored context retrieval (unless explicitly configured otherwise).
- Supports message signing for verifying context authenticity.
- Allows implementations to enforce expiration policies on stored context.

### Learn More

For full details on how OCP works, refer to:

- [Architecture](architecture.md)
- [Versioning](basic/versioning.md)
- [Lifecycle](basic/lifecycle.md)
- [Transports](basic/transports.md)
- [Security](basic/security.md)
- [Contributing](contributing.md)