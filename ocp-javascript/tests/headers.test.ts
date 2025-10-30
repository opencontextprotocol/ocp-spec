/**
 * Tests for OCP header encoding and decoding functionality.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { gzipSync, gunzipSync } from 'zlib';
import {
  OCPHeaders,
  createOCPHeaders,
  extractContextFromResponse,
  parseContext,
  addContextHeaders,
  OCP_CONTEXT_ID,
  OCP_SESSION,
  OCP_AGENT_TYPE,
  OCP_AGENT_GOAL,
  OCP_USER,
  OCP_WORKSPACE,
  OCP_VERSION,
} from '../src/headers.js';
import { AgentContext } from '../src/context.js';

// Fixtures
let sampleContext: AgentContext;
let minimalContext: AgentContext;
let complexContext: AgentContext;

// Mock HTTP response helper
function mockHttpResponse(options: { status?: number; headers?: Record<string, string>; text?: string } = {}) {
  return {
    status: options.status || 200,
    headers: options.headers || {},
    text: options.text || '',
    json: () => (options.text ? JSON.parse(options.text) : {}),
  };
}

beforeEach(() => {
  sampleContext = new AgentContext({
    agent_type: 'test_agent',
    user: 'test_user',
    workspace: 'test_workspace',
    current_file: 'test_file.js',
  });
  sampleContext.updateGoal('test_goal', 'Testing OCP functionality');
  sampleContext.addInteraction('test_action', 'test_endpoint', 'test_result');

  minimalContext = new AgentContext({ agent_type: 'minimal_agent' });

  complexContext = new AgentContext({
    agent_type: 'complex_agent',
    user: 'complex_user',
    workspace: 'complex_workspace',
    current_file: 'complex_file.js',
  });
  complexContext.updateGoal('complex_goal', 'Complex goal summary');
  for (let i = 0; i < 5; i++) {
    complexContext.addInteraction(`action_${i}`, `endpoint_${i}`, `result_${i}`, { step: i });
  }
  for (let i = 0; i < 3; i++) {
    complexContext.addRecentChange(`change_${i}`);
  }
  complexContext.addApiSpec('github', 'https://api.github.com');
  complexContext.addApiSpec('stripe', 'https://api.stripe.com');
  complexContext.setErrorContext('Test error message', 'error_file.js');
});

describe('OCP Headers Encoding', () => {
  test('encode minimal context', () => {
    const headers = OCPHeaders.encodeContext(minimalContext);

    expect(headers[OCP_CONTEXT_ID]).toBeDefined();
    expect(headers[OCP_SESSION]).toBeDefined();
    expect(headers[OCP_AGENT_TYPE]).toBeDefined();
    expect(headers[OCP_VERSION]).toBeDefined();

    expect(headers[OCP_CONTEXT_ID]).toBe(minimalContext.context_id);
    expect(headers[OCP_AGENT_TYPE]).toBe(minimalContext.agent_type);
    expect(headers[OCP_VERSION]).toBe('1.0');
  });

  test('encode full context', () => {
    const headers = OCPHeaders.encodeContext(sampleContext);

    // Check all expected headers are present
    const expectedHeaders = [OCP_CONTEXT_ID, OCP_SESSION, OCP_AGENT_TYPE, OCP_VERSION];
    for (const header of expectedHeaders) {
      expect(headers[header]).toBeDefined();
    }

    // Check optional headers
    if (sampleContext.current_goal) {
      expect(headers[OCP_AGENT_GOAL]).toBeDefined();
      expect(headers[OCP_AGENT_GOAL]).toBe(sampleContext.current_goal);
    }

    if (sampleContext.workspace) {
      expect(headers[OCP_WORKSPACE]).toBeDefined();
      expect(headers[OCP_WORKSPACE]).toBe(sampleContext.workspace);
    }
  });

  test('encode with compression', () => {
    const headers = OCPHeaders.encodeContext(complexContext, true);

    // Session data should be compressed if large enough
    const sessionData = headers[OCP_SESSION];
    if (sessionData.startsWith('gzip:')) {
      // Verify we can decode the compressed data
      const encodedData = sessionData.slice(5);
      const compressed = Buffer.from(encodedData, 'base64');
      const decompressed = gunzipSync(compressed).toString('utf-8');
      const parsed = JSON.parse(decompressed);

      expect(parsed.context_id).toBe(complexContext.context_id);
    }
  });

  test('encode without compression', () => {
    const headers = OCPHeaders.encodeContext(sampleContext, false);

    // Session data should be base64 encoded but not compressed
    const sessionData = headers[OCP_SESSION];
    expect(sessionData.startsWith('gzip:')).toBe(false);

    // Should be decodable as base64
    const decoded = Buffer.from(sessionData, 'base64').toString('utf-8');
    const parsed = JSON.parse(decoded);
    expect(parsed.context_id).toBe(sampleContext.context_id);
  });
});

describe('OCP Headers Decoding', () => {
  test('decode valid headers', () => {
    // Encode then decode
    const headers = OCPHeaders.encodeContext(sampleContext);
    const decodedContext = OCPHeaders.decodeContext(headers);

    expect(decodedContext).not.toBeNull();
    expect(decodedContext!.context_id).toBe(sampleContext.context_id);
    expect(decodedContext!.agent_type).toBe(sampleContext.agent_type);
    expect(decodedContext!.user).toBe(sampleContext.user);
    expect(decodedContext!.history.length).toBe(sampleContext.history.length);
  });

  test('decode case insensitive', () => {
    const headers = OCPHeaders.encodeContext(sampleContext);

    // Convert to different cases
    const mixedCaseHeaders: Record<string, string> = {
      'ocp-context-id': headers[OCP_CONTEXT_ID],
      'OCP-SESSION': headers[OCP_SESSION],
      'Ocp-Agent-Type': headers[OCP_AGENT_TYPE],
    };

    const decodedContext = OCPHeaders.decodeContext(mixedCaseHeaders);
    expect(decodedContext).not.toBeNull();
    expect(decodedContext!.context_id).toBe(sampleContext.context_id);
  });

  test('decode compressed headers', () => {
    const headers = OCPHeaders.encodeContext(complexContext, true);
    const decodedContext = OCPHeaders.decodeContext(headers);

    expect(decodedContext).not.toBeNull();
    expect(decodedContext!.context_id).toBe(complexContext.context_id);
    expect(decodedContext!.history.length).toBe(complexContext.history.length);
  });

  test('decode missing headers', () => {
    // Missing context ID
    let headers: Record<string, string> = { [OCP_SESSION]: 'dGVzdA==' };
    expect(OCPHeaders.decodeContext(headers)).toBeNull();

    // Missing session
    headers = { [OCP_CONTEXT_ID]: 'ocp-12345678' };
    expect(OCPHeaders.decodeContext(headers)).toBeNull();
  });

  test('decode invalid base64', () => {
    const headers = {
      [OCP_CONTEXT_ID]: 'ocp-12345678',
      [OCP_SESSION]: 'invalid-base64-data',
    };
    expect(OCPHeaders.decodeContext(headers)).toBeNull();
  });

  test('decode invalid json', () => {
    const invalidJson = Buffer.from('invalid json').toString('base64');
    const headers = {
      [OCP_CONTEXT_ID]: 'ocp-12345678',
      [OCP_SESSION]: invalidJson,
    };
    expect(OCPHeaders.decodeContext(headers)).toBeNull();
  });
});

describe('OCP Headers Validation', () => {
  test('validate valid headers', () => {
    const headers = OCPHeaders.encodeContext(sampleContext);
    expect(OCPHeaders.validateHeaders(headers)).toBe(true);
  });

  test('validate missing headers', () => {
    // Missing context ID
    let headers: Record<string, string> = { [OCP_SESSION]: 'dGVzdA==' };
    expect(OCPHeaders.validateHeaders(headers)).toBe(false);

    // Missing session
    headers = { [OCP_CONTEXT_ID]: 'ocp-12345678' };
    expect(OCPHeaders.validateHeaders(headers)).toBe(false);
  });

  test('validate invalid data', () => {
    const headers = {
      [OCP_CONTEXT_ID]: 'ocp-12345678',
      [OCP_SESSION]: 'invalid-data',
    };
    expect(OCPHeaders.validateHeaders(headers)).toBe(false);
  });
});

describe('OCP Headers Utilities', () => {
  test('get context summary', () => {
    const headers = OCPHeaders.encodeContext(sampleContext);
    const summary = OCPHeaders.getContextSummary(headers);

    expect(typeof summary).toBe('string');
    expect(summary).toContain(sampleContext.context_id);
    expect(summary).toContain(sampleContext.agent_type);
  });

  test('merge headers', () => {
    const baseHeaders: Record<string, string> = {
      'Authorization': 'Bearer token123',
      'Content-Type': 'application/json',
    };

    const ocpHeaders = {
      [OCP_CONTEXT_ID]: 'ocp-12345678',
      [OCP_AGENT_TYPE]: 'test_agent',
    };

    const merged = OCPHeaders.mergeHeaders(baseHeaders, ocpHeaders);

    // Should contain both sets
    expect(merged['Authorization']).toBeDefined();
    expect(merged['Content-Type']).toBeDefined();
    expect(merged[OCP_CONTEXT_ID]).toBeDefined();
    expect(merged[OCP_AGENT_TYPE]).toBeDefined();

    // Original headers should not be modified
    expect(baseHeaders[OCP_CONTEXT_ID]).toBeUndefined();
  });

  test('strip ocp headers', () => {
    const headers = OCPHeaders.encodeContext(sampleContext);
    headers['Authorization'] = 'Bearer token123';
    headers['Content-Type'] = 'application/json';

    const stripped = OCPHeaders.stripOCPHeaders(headers);

    // OCP headers should be removed
    expect(stripped[OCP_CONTEXT_ID]).toBeUndefined();
    expect(stripped[OCP_SESSION]).toBeUndefined();
    expect(stripped[OCP_AGENT_TYPE]).toBeUndefined();

    // Non-OCP headers should remain
    expect(stripped['Authorization']).toBeDefined();
    expect(stripped['Content-Type']).toBeDefined();
  });
});

describe('Convenience Functions', () => {
  test('create ocp headers', () => {
    const headers = createOCPHeaders(sampleContext);

    expect(headers[OCP_CONTEXT_ID]).toBeDefined();
    expect(headers[OCP_CONTEXT_ID]).toBe(sampleContext.context_id);
  });

  test('create ocp headers with base', () => {
    const baseHeaders = { Authorization: 'Bearer token123' };
    const headers = createOCPHeaders(sampleContext, baseHeaders);

    // Should contain both
    expect(headers['Authorization']).toBeDefined();
    expect(headers[OCP_CONTEXT_ID]).toBeDefined();
  });

  test('extract context from response', () => {
    // Create response with OCP headers
    const ocpHeaders = OCPHeaders.encodeContext(sampleContext);
    const response = mockHttpResponse({ headers: ocpHeaders });

    const extractedContext = extractContextFromResponse(response);

    expect(extractedContext).not.toBeNull();
    expect(extractedContext!.context_id).toBe(sampleContext.context_id);
  });

  test('extract context no headers', () => {
    const response = mockHttpResponse({ headers: { 'Content-Type': 'application/json' } });

    const extractedContext = extractContextFromResponse(response);
    expect(extractedContext).toBeNull();
  });

  test('extract context no headers attr', () => {
    const response = {};

    const extractedContext = extractContextFromResponse(response);
    expect(extractedContext).toBeNull();
  });
});

describe('Header Round Trip', () => {
  test('minimal roundtrip', () => {
    const headers = OCPHeaders.encodeContext(minimalContext);
    const decoded = OCPHeaders.decodeContext(headers);

    expect(decoded!.context_id).toBe(minimalContext.context_id);
    expect(decoded!.agent_type).toBe(minimalContext.agent_type);
  });

  test('complex roundtrip', () => {
    const headers = OCPHeaders.encodeContext(complexContext);
    const decoded = OCPHeaders.decodeContext(headers);

    // Verify all data preserved
    expect(decoded!.context_id).toBe(complexContext.context_id);
    expect(decoded!.agent_type).toBe(complexContext.agent_type);
    expect(decoded!.user).toBe(complexContext.user);
    expect(decoded!.workspace).toBe(complexContext.workspace);
    expect(decoded!.current_file).toBe(complexContext.current_file);
    expect(decoded!.current_goal).toBe(complexContext.current_goal);
    expect(decoded!.error_context).toBe(complexContext.error_context);
    expect(decoded!.history.length).toBe(complexContext.history.length);
    expect(decoded!.recent_changes.length).toBe(complexContext.recent_changes.length);
    expect(decoded!.api_specs).toEqual(complexContext.api_specs);
  });

  test.each([true, false])('roundtrip with compression options: %s', (compress) => {
    const headers = OCPHeaders.encodeContext(sampleContext, compress);
    const decoded = OCPHeaders.decodeContext(headers);

    expect(decoded!.context_id).toBe(sampleContext.context_id);
    expect(decoded!.current_goal).toBe(sampleContext.current_goal);
    expect(decoded!.history.length).toBe(sampleContext.history.length);
  });
});

describe('New Convenience Functions', () => {
  test('parse context with dict', () => {
    const headers = sampleContext.toHeaders();
    const parsed = parseContext(headers);

    expect(parsed).not.toBeNull();
    expect(parsed!.agent_type).toBe(sampleContext.agent_type);
    expect(parsed!.user).toBe(sampleContext.user);
  });

  test('parse context with headers object', () => {
    const headersDict = sampleContext.toHeaders();

    // Mock headers object with items() method
    const headersObj: any = {
      items: () => Object.entries(headersDict),
    };

    const parsed = parseContext(headersObj);
    expect(parsed).not.toBeNull();
    expect(parsed!.agent_type).toBe(sampleContext.agent_type);
  });

  test('parse context no ocp headers', () => {
    const headers = { 'content-type': 'application/json' };
    const parsed = parseContext(headers);
    expect(parsed).toBeNull();
  });

  test('add context headers flask style', () => {
    // Mock Flask response with proper headers object
    const headersMock: any = {};
    const response: any = {
      headers: headersMock,
    };

    addContextHeaders(response, sampleContext);

    // Should have added headers
    expect(Object.keys(response.headers).length).toBeGreaterThan(0);
    expect(Object.keys(response.headers).some((key) => key.startsWith('OCP-'))).toBe(true);
  });

  test('add context headers django style', () => {
    // Mock Django response (no headers, uses setHeader)
    const setHeaderCalls: Array<[string, string]> = [];
    const response: any = {
      setHeader: (key: string, value: string) => setHeaderCalls.push([key, value]),
    };

    addContextHeaders(response, sampleContext);

    // Should have called setHeader for each OCP header
    expect(setHeaderCalls.length).toBeGreaterThan(0);
    expect(setHeaderCalls.some(([key]) => key.startsWith('OCP-'))).toBe(true);
  });

  test('add context headers fastapi style', () => {
    // Mock FastAPI response with headers object
    const response: any = {
      headers: {},
    };

    addContextHeaders(response, sampleContext);

    // Should have added headers to the dict
    expect(Object.keys(response.headers).length).toBeGreaterThan(0);
    expect(Object.keys(response.headers).some((key) => key.startsWith('OCP-'))).toBe(true);
  });

  test('add context headers generic dict', () => {
    // Mock response with headers dict
    const response: any = {
      headers: {},
    };

    addContextHeaders(response, sampleContext);

    expect(Object.keys(response.headers).length).toBeGreaterThan(0);
    expect(Object.keys(response.headers).some((key) => key.startsWith('OCP-'))).toBe(true);
  });

  test('add context headers unsupported type', () => {
    // Mock completely unsupported response that fails all attempts
    const response: any = {};

    expect(() => addContextHeaders(response, sampleContext)).toThrow(TypeError);
    expect(() => addContextHeaders(response, sampleContext)).toThrow(/Unsupported response type/);
  });

  test('add context headers with compression', () => {
    const response: any = {
      headers: {},
    };

    addContextHeaders(response, sampleContext, false);

    expect(Object.keys(response.headers).length).toBeGreaterThan(0);
    expect(Object.keys(response.headers).some((key) => key.startsWith('OCP-'))).toBe(true);
  });
});
