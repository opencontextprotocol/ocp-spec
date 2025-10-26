/**
 * OCP Headers - HTTP header management for Open Context Protocol.
 * 
 * Handles encoding/decoding agent context into HTTP headers and validation.
 */

import { gzipSync, gunzipSync } from 'zlib';
import { AgentContext } from './context.js';

// OCP Header names
export const OCP_CONTEXT_ID = 'OCP-Context-ID';
export const OCP_SESSION = 'OCP-Session';
export const OCP_AGENT_GOAL = 'OCP-Agent-Goal';
export const OCP_AGENT_TYPE = 'OCP-Agent-Type';
export const OCP_USER = 'OCP-User';
export const OCP_WORKSPACE = 'OCP-Workspace';
export const OCP_VERSION = 'OCP-Version';

// Current OCP specification version
export const OCP_SPEC_VERSION = '1.0';

/**
 * Manages OCP HTTP headers for agent context transmission.
 * 
 * Handles encoding agent context into HTTP headers and decoding
 * received headers back into context objects.
 */
export class OCPHeaders {
  /**
   * Encode AgentContext into OCP HTTP headers
   */
  static encodeContext(context: AgentContext, compress: boolean = true): Record<string, string> {
    const headers: Record<string, string> = {
      [OCP_CONTEXT_ID]: context.context_id,
      [OCP_AGENT_TYPE]: context.agent_type,
      [OCP_VERSION]: OCP_SPEC_VERSION,
    };

    // Add optional headers if present
    if (context.current_goal) {
      headers[OCP_AGENT_GOAL] = context.current_goal;
    }

    if (context.user) {
      headers[OCP_USER] = context.user;
    }

    if (context.workspace) {
      headers[OCP_WORKSPACE] = context.workspace;
    }

    // Encode session data
    const sessionData = context.toDict();
    const sessionJson = JSON.stringify(sessionData);

    if (compress && sessionJson.length > 1000) {
      // Compress large session data
      const compressed = gzipSync(Buffer.from(sessionJson, 'utf-8'));
      const encoded = compressed.toString('base64');
      headers[OCP_SESSION] = `gzip:${encoded}`;
    } else {
      // Base64 encode without compression
      const encoded = Buffer.from(sessionJson, 'utf-8').toString('base64');
      headers[OCP_SESSION] = encoded;
    }

    return headers;
  }

  /**
   * Decode OCP headers back into an AgentContext object
   */
  static decodeContext(headers: Record<string, string>): AgentContext | null {
    // Normalize header names (case-insensitive lookup)
    const normalizedHeaders: Record<string, string> = {};
    for (const [key, value] of Object.entries(headers)) {
      normalizedHeaders[key.toLowerCase()] = value;
    }

    const contextId = normalizedHeaders[OCP_CONTEXT_ID.toLowerCase()];
    const sessionData = normalizedHeaders[OCP_SESSION.toLowerCase()];

    if (!contextId || !sessionData) {
      return null;
    }

    try {
      let sessionJson: string;

      // Decode session data
      if (sessionData.startsWith('gzip:')) {
        // Decompress gzipped data
        const encodedData = sessionData.slice(5); // Remove "gzip:" prefix
        const compressed = Buffer.from(encodedData, 'base64');
        sessionJson = gunzipSync(compressed).toString('utf-8');
      } else {
        // Base64 decode
        sessionJson = Buffer.from(sessionData, 'base64').toString('utf-8');
      }

      // Parse context data
      const contextData = JSON.parse(sessionJson);
      return AgentContext.fromDict(contextData);
    } catch (e) {
      return null;
    }
  }

  /**
   * Validate that headers contain valid OCP context
   */
  static validateHeaders(headers: Record<string, string>): boolean {
    const normalizedHeaders: Record<string, string> = {};
    for (const [key, value] of Object.entries(headers)) {
      normalizedHeaders[key.toLowerCase()] = value;
    }

    // Check required headers
    const required = [OCP_CONTEXT_ID.toLowerCase(), OCP_SESSION.toLowerCase()];
    if (!required.every(header => header in normalizedHeaders)) {
      return false;
    }

    // Validate context can be decoded
    const context = OCPHeaders.decodeContext(headers);
    return context !== null;
  }

  /**
   * Get a human-readable summary of the OCP context from headers
   */
  static getContextSummary(headers: Record<string, string>): string {
    const normalizedHeaders: Record<string, string> = {};
    for (const [key, value] of Object.entries(headers)) {
      normalizedHeaders[key.toLowerCase()] = value;
    }

    const contextId = normalizedHeaders[OCP_CONTEXT_ID.toLowerCase()] || 'unknown';
    const agentType = normalizedHeaders[OCP_AGENT_TYPE.toLowerCase()] || 'unknown';
    const goal = normalizedHeaders[OCP_AGENT_GOAL.toLowerCase()] || 'none';
    const user = normalizedHeaders[OCP_USER.toLowerCase()] || 'unknown';
    const workspace = normalizedHeaders[OCP_WORKSPACE.toLowerCase()] || 'unknown';

    return `OCP Context: ${contextId} | Agent: ${agentType} | Goal: ${goal} | Workspace: ${workspace}`;
  }

  /**
   * Merge OCP headers with existing HTTP headers
   */
  static mergeHeaders(
    baseHeaders: Record<string, string>,
    ocpHeaders: Record<string, string>
  ): Record<string, string> {
    return { ...baseHeaders, ...ocpHeaders };
  }

  /**
   * Remove OCP headers from a headers dictionary
   */
  static stripOCPHeaders(headers: Record<string, string>): Record<string, string> {
    const ocpHeaderNames = new Set([
      OCP_CONTEXT_ID.toLowerCase(),
      OCP_SESSION.toLowerCase(),
      OCP_AGENT_GOAL.toLowerCase(),
      OCP_AGENT_TYPE.toLowerCase(),
      OCP_USER.toLowerCase(),
      OCP_WORKSPACE.toLowerCase(),
      OCP_VERSION.toLowerCase(),
    ]);

    const result: Record<string, string> = {};
    for (const [key, value] of Object.entries(headers)) {
      if (!ocpHeaderNames.has(key.toLowerCase())) {
        result[key] = value;
      }
    }
    return result;
  }
}

/**
 * Convenience function to create OCP headers from context
 */
export function createOCPHeaders(
  context: AgentContext,
  baseHeaders?: Record<string, string>,
  compress: boolean = true
): Record<string, string> {
  const ocpHeaders = OCPHeaders.encodeContext(context, compress);

  if (baseHeaders) {
    return OCPHeaders.mergeHeaders(baseHeaders, ocpHeaders);
  }

  return ocpHeaders;
}

/**
 * Extract OCP context from an HTTP response object
 */
export function extractContextFromResponse(response: any): AgentContext | null {
  if (!response || !response.headers) {
    return null;
  }

  // Convert headers to dict (handle different response types)
  let headersDict: Record<string, string>;

  if (typeof response.headers.entries === 'function') {
    headersDict = {};
    for (const [key, value] of response.headers.entries()) {
      headersDict[key] = value;
    }
  } else if (typeof response.headers.items === 'function') {
    headersDict = Object.fromEntries(response.headers.items());
  } else {
    headersDict = response.headers;
  }

  return OCPHeaders.decodeContext(headersDict);
}

/**
 * Convenience function to parse OCP context from HTTP headers
 */
export function parseContext(headers: any): AgentContext | null {
  // Convert headers to dict (handle different header types)
  let headersDict: Record<string, string>;

  if (headers instanceof Headers) {
    headersDict = {};
    headers.forEach((value, key) => {
      headersDict[key] = value;
    });
  } else if (typeof headers.entries === 'function') {
    headersDict = Object.fromEntries(headers.entries());
  } else if (typeof headers.items === 'function') {
    headersDict = Object.fromEntries(headers.items());
  } else {
    headersDict = headers;
  }

  return OCPHeaders.decodeContext(headersDict);
}

/**
 * Convenience function to add OCP headers to HTTP response objects
 */
export function addContextHeaders(
  response: any,
  context: AgentContext,
  compress: boolean = true
): void {
  const ocpHeaders = createOCPHeaders(context, undefined, compress);

  // Handle different response types
  if (response.headers && typeof response.headers.set === 'function') {
    // Headers object (fetch API)
    for (const [key, value] of Object.entries(ocpHeaders)) {
      response.headers.set(key, value);
    }
  } else if (response.headers && typeof response.headers === 'object') {
    // Plain object
    Object.assign(response.headers, ocpHeaders);
  } else if (typeof response.setHeader === 'function') {
    // Node.js response
    for (const [key, value] of Object.entries(ocpHeaders)) {
      response.setHeader(key, value);
    }
  } else {
    throw new TypeError(
      `Unsupported response type: ${typeof response}. ` +
      `Response must have a 'headers' attribute that supports item assignment.`
    );
  }
}
