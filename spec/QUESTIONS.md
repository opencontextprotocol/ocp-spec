# Open Questions & Edge Cases

*(to be addressed before implementation)*

## 1. Context Object & Size Limits
- What’s the maximum practical size for a context object?
  - Can LCP fit within HTTP headers (~8 KB limit on most servers)?
  - If too large, should we fallback to request bodies or external storage?
  - Should we standardize compression for large payloads?
- Should LCP enforce a structure for history length?
  - Do we limit history (e.g., last 20 messages) or let clients decide?
  - Should there be a recommended “max context size”?
- Do we need a "context pruning" guideline?
  - Should we suggest automatic trimming of older messages?
  - Should LCP define a default expiration for stored context?

## 2. Security & Validation
- How do we ensure context integrity?
  - Should LCP require cryptographic signatures (e.g., HMAC, JWT-like)?
  - How do we prevent tampering if context is passed between systems?
  - Should stored context objects require authentication?
- How do we handle sensitive data inside context?
  - Do we recommend encrypting stored context?
  - Should there be a privacy flag (e.g., “don’t log this”)?
- What happens if a client sends invalid context?
  - Should APIs reject malformed context?
  - Should we define error response formats for bad context?

## 3. Stateless vs. Stateful Mode
- How does LCP handle stateful storage?
  - Should there be a standard API for fetching stored context?
  - Do we define a storage format or let implementations decide?
  - Should stateful context automatically expire after some time?
- How do clients reference stored context?
  - Should stored contexts always have a unique `context_id`?
  - Do we allow partial updates to stored context (e.g., append new history)?
- What happens when stored context expires or is deleted?
  - Should API responses indicate missing/expired context?
  - Should clients be expected to resend full history when context is lost?

## 4. Transport Considerations
- How do we handle different transport layers?
  - Should LCP define a standard header name for HTTP (`LCP-Context`)?
  - Should WebSockets/gRPC pass context as metadata or inline payloads?
- How do we handle context across multiple requests?
  - Should we provide guidelines for multi-turn interactions?
  - Should clients be able to batch requests with the same context?
- Error handling when context is missing or malformed
  - Should we define standardized error codes for invalid/missing context?
  - What should happen if a model doesn’t support LCP context?

## 5. Adoption & Interoperability
- How do we ensure compatibility with existing AI APIs?
  - Should we test OpenAI, Claude, and Mistral compatibility early?
  - Should LCP support adapter modes for APIs that don’t accept structured context?
- Should LCP provide standard helper libraries?
  - Do we want official SDKs in TypeScript, Go, Python?
  - Should we provide example implementations in OpenAI/Claude?
- Should LCP define a standard logging/debugging format?
  - Do we need a standard way to inspect/debug context exchanges?
  - Should there be a debug mode that logs raw context data?