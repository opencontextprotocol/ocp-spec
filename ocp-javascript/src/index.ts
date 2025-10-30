/**
 * Open Context Protocol (OCP) - JavaScript/TypeScript Library
 * 
 * A zero-infrastructure protocol that provides conversational context
 * and automatic API discovery to enhance AI agent interactions.
 * 
 * Enables persistent context sharing across HTTP API calls using standard headers,
 * requiring no servers or infrastructure setup.
 */

/**
 * Open Context Protocol (OCP) - JavaScript/TypeScript Implementation
 * 
 * Core library for implementing OCP context management in AI agents.
 */

// Core exports
export { AgentContext, OCPContextDict } from './context.js';

// Headers
export {
    OCPHeaders,
    OCP_CONTEXT_ID,
    OCP_SESSION,
    OCP_AGENT_GOAL,
    OCP_AGENT_TYPE,
    OCP_USER,
    OCP_WORKSPACE,
    OCP_VERSION,
    OCP_SPEC_VERSION,
    createOCPHeaders,
    extractContextFromResponse,
    parseContext,
    addContextHeaders
} from './headers.js';

// Validation
export {
    ValidationResult,
    validateContext,
    validateContextDict,
    getSchema,
    validateAndFixContext
} from './validation.js';

// Errors
export {
    OCPError,
    RegistryUnavailable,
    APINotFound,
    SchemaDiscoveryError,
    ValidationError
} from './errors.js';

// Schema Discovery
export {
    OCPSchemaDiscovery,
    type OCPTool,
    type OCPAPISpec
} from './schema_discovery.js';

// Registry
export { OCPRegistry } from './registry.js';

// HTTP Client
export {
    OCPHTTPClient,
    type OCPResponse,
    wrapApi
} from './http_client.js';

// Agent
export { OCPAgent } from './agent.js';

// Storage
export { OCPStorage } from './storage.js';

// Version
export const VERSION = '0.1.0';
