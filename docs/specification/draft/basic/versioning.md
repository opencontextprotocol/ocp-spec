---
title: Versioning
type: docs
weight: 80
---

The Open Context Protocol (OCP) uses string-based version identifiers following the format  
`YYYY-MM-DD`, indicating the last date backwards-incompatible changes were made.

The current protocol version is draft. [See all revisions]({{< ref "/specification/draft/revisions" >}}).

{{< callout type="info" >}}  
The protocol version will _not_ be incremented when updates maintain backwards compatibility.  
This allows incremental improvements while preserving interoperability.  
{{< /callout >}}

## Version Negotiation

OCP does not assume a client-server model, but when implementations interact across multiple systems,  
they MAY support multiple protocol versions simultaneously. Implementations MUST agree on a  
single version for any given exchange.

If version negotiation fails, implementations MUST return an appropriate error response,  
allowing systems to gracefully handle version mismatches.

## Breaking Changes

A new protocol version MUST be issued when changes are introduced that:
- Modify the structure of context objects in a non-backward-compatible way.
- Introduce required fields or remove existing required fields.
- Change the expected behavior of existing transports.

## Learn More

For further details, refer to:
- [Lifecycle](basic/lifecycle.md)
- [Transports](basic/transports.md)
- [Security](basic/security.md)
