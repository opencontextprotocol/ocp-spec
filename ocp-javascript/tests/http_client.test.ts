/**
 * Tests for OCP HTTP client functionality.
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { OCPHTTPClient, wrapApi } from '../src/http_client.js';
import { AgentContext } from '../src/context.js';
import { createOCPHeaders } from '../src/headers.js';

// Mock fetch globally
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('OCP HTTP Client', () => {
  let context: AgentContext;

  beforeEach(() => {
    context = new AgentContext({ agent_type: 'test_agent', user: 'test_user' });
    context.updateGoal('testing http client');
    jest.clearAllMocks();
  });

  describe('OCPHTTPClient Initialization', () => {
    test('init without http client', () => {
      const ocpClient = new OCPHTTPClient(context);

      expect(ocpClient['context']).toBe(context);
      expect(ocpClient['context'].agent_type).toBe('test_agent');
    });

    test('init auto update context false', () => {
      // Note: JavaScript implementation doesn't have auto_update_context parameter yet
      // This test would need to be updated if that feature is added
      const ocpClient = new OCPHTTPClient(context);
      expect(ocpClient).toBeDefined();
    });
  });

  describe('Header Preparation', () => {
    test('prepare headers no existing', () => {
      const ocpClient = new OCPHTTPClient(context);

      const headers = ocpClient['_prepareHeaders']();

      // Should include OCP headers
      const expectedHeaders = createOCPHeaders(context);
      expect(headers).toEqual(expectedHeaders);
    });

    test('prepare headers with existing', () => {
      const ocpClient = new OCPHTTPClient(context);
      const existingHeaders = { 'Custom-Header': 'value', 'Authorization': 'Bearer token' };

      const headers = ocpClient['_prepareHeaders'](existingHeaders);

      // Should merge existing and OCP headers
      const expectedHeaders = createOCPHeaders(context);
      Object.assign(expectedHeaders, existingHeaders);
      expect(headers).toEqual(expectedHeaders);
    });

    test('prepare headers override ocp', () => {
      const ocpClient = new OCPHTTPClient(context);

      // Get OCP headers to know what to override
      const ocpHeaders = createOCPHeaders(context);
      const ocpHeaderKey = Object.keys(ocpHeaders)[0];

      const existingHeaders = { [ocpHeaderKey]: 'overridden_value' };
      const headers = ocpClient['_prepareHeaders'](existingHeaders);

      // OCP header should actually override existing header (based on implementation)
      // The implementation does: {...ocpHeaders, ...additionalHeaders} which means additional wins
      expect(headers[ocpHeaderKey]).toBe('overridden_value');
    });
  });

  describe('Interaction Logging', () => {
    test('log interaction enabled', () => {
      const ocpClient = new OCPHTTPClient(context);

      // Mock the context.addInteraction method
      const addInteractionSpy = jest.spyOn(context, 'addInteraction');

      // Call private method
      ocpClient['_logInteraction']('GET', 'https://api.example.com/users', 200);

      // Should log interaction
      expect(addInteractionSpy).toHaveBeenCalledWith(
        'api_call_get',
        'https://api.example.com/users',
        '200',
        {
          method: 'GET',
          status_code: 200,
          success: true,
          error: undefined,
        }
      );

      addInteractionSpy.mockRestore();
    });

    test('log interaction disabled', () => {
      // Test with auto_update_context disabled
      const ocpClient = new OCPHTTPClient(context, false);
      const addInteractionSpy = jest.spyOn(context, 'addInteraction');

      ocpClient['_logInteraction']('POST', 'https://api.example.com/data', undefined);

      // Should not log when disabled
      expect(addInteractionSpy).not.toHaveBeenCalled();

      addInteractionSpy.mockRestore();
    });

    test('log interaction different status formats', () => {
      const ocpClient = new OCPHTTPClient(context);
      const addInteractionSpy = jest.spyOn(context, 'addInteraction');

      // Test with status code
      ocpClient['_logInteraction']('GET', 'https://api.example.com/missing', 404);

      // Test with different status
      ocpClient['_logInteraction']('POST', 'https://api.example.com/create', 201);

      // Test with undefined
      ocpClient['_logInteraction']('PUT', 'https://api.example.com/update', undefined);

      // Verify calls
      expect(addInteractionSpy).toHaveBeenNthCalledWith(
        1,
        'api_call_get',
        'https://api.example.com/missing',
        '404',
        {
          method: 'GET',
          status_code: 404,
          success: false,
          error: undefined,
        }
      );

      expect(addInteractionSpy).toHaveBeenNthCalledWith(
        2,
        'api_call_post',
        'https://api.example.com/create',
        '201',
        {
          method: 'POST',
          status_code: 201,
          success: true,
          error: undefined,
        }
      );

      expect(addInteractionSpy).toHaveBeenNthCalledWith(
        3,
        'api_call_put',
        'https://api.example.com/update',
        undefined,
        {
          method: 'PUT',
          status_code: undefined,
          success: false,
          error: undefined,
        }
      );

      addInteractionSpy.mockRestore();
    });
  });

  describe('Request Method', () => {
    test('request method', async () => {
      const ocpClient = new OCPHTTPClient(context);

      // Mock fetch response
      const mockResponse = {
        status: 200,
        statusText: 'OK',
        ok: true,
        headers: new Headers(),
        text: async () => JSON.stringify({ success: true }),
      };
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue(mockResponse as Response);

      // Mock context interaction (without calling the real method)
      const addInteractionMock = jest.fn();
      const originalAddInteraction = context.addInteraction;
      context.addInteraction = addInteractionMock;

      // Make request
      const result = await ocpClient.request('GET', 'https://api.example.com/test', {
        params: { q: 'search' },
        timeout: 30000,
      });

      // Verify fetch was called
      expect(global.fetch).toHaveBeenCalledTimes(1);
      const fetchCall = (global.fetch as jest.MockedFunction<typeof fetch>).mock.calls[0];

      // Check URL has query params
      expect(fetchCall[0].toString()).toContain('q=search');

      // Check options
      expect(fetchCall[1]?.method).toBe('GET');
      expect(fetchCall[1]?.headers).toBeDefined();

      // Verify OCP headers were added
      const headers = fetchCall[1]?.headers as Record<string, string>;
      const expectedOcpHeaders = createOCPHeaders(context);
      for (const [key, value] of Object.entries(expectedOcpHeaders)) {
        expect(headers[key]).toBe(value);
      }

      // Verify interaction was logged
      expect(addInteractionMock).toHaveBeenCalledTimes(1);

      // Verify response was returned
      expect(result.status).toBe(200);

      // Restore original method
      context.addInteraction = originalAddInteraction;
    });
  });

  describe('HTTP Methods', () => {
    test('http methods', async () => {
      const ocpClient = new OCPHTTPClient(context);

      const mockResponse = {
        status: 200,
        statusText: 'OK',
        ok: true,
        headers: new Headers(),
        text: async () => '{}',
      };
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue(mockResponse as Response);

      // Test each HTTP method
      const methods: Array<[string, string]> = [
        ['get', 'GET'],
        ['post', 'POST'],
        ['put', 'PUT'],
        ['delete', 'DELETE'],
        ['patch', 'PATCH'],
      ];

      for (const [methodName, httpMethod] of methods) {
        (global.fetch as jest.MockedFunction<typeof fetch>).mockClear();

        const methodFunc = (ocpClient as any)[methodName];
        await methodFunc.call(ocpClient, 'https://api.example.com/endpoint', {
          json: { test: 'data' },
        });

        // Verify correct HTTP method was used
        expect(global.fetch).toHaveBeenCalledTimes(1);
        const fetchCall = (global.fetch as jest.MockedFunction<typeof fetch>).mock.calls[0];
        expect(fetchCall[1]?.method).toBe(httpMethod);
      }
    });
  });
});

describe('Wrap API', () => {
  let context: AgentContext;

  beforeEach(() => {
    context = new AgentContext({ agent_type: 'test_agent' });
    jest.clearAllMocks();
  });

  test('wrap api basic', () => {
    const apiClient = wrapApi(context, 'https://api.example.com');

    expect(apiClient).toBeDefined();
    expect(apiClient.request).toBeDefined();
  });

  test('wrap api with auth token', () => {
    const apiClient = wrapApi(context, 'https://api.github.com', { 'Authorization': 'token ghp_123456' });

    expect(apiClient).toBeDefined();
  });

  test('wrap api with bearer token', () => {
    const apiClient = wrapApi(context, 'https://api.example.com', { 'Authorization': 'Bearer jwt_token_here' });

    expect(apiClient).toBeDefined();
  });

  test('wrap api with basic auth', () => {
    const apiClient = wrapApi(context, 'https://api.example.com', { 'Authorization': 'Basic dXNlcjpwYXNz' });

    expect(apiClient).toBeDefined();
  });

  test('wrap api with plain token', () => {
    const apiClient = wrapApi(context, 'https://api.example.com', { 'Authorization': 'token abc123def456' });

    expect(apiClient).toBeDefined();
  });

  test('wrap api with custom headers', () => {
    const customHeaders = {
      'User-Agent': 'MyApp/1.0',
      'Accept': 'application/vnd.api+json',
    };

    const apiClient = wrapApi(context, 'https://api.example.com', customHeaders);

    expect(apiClient).toBeDefined();
  });

  test('wrap api base url normalization', () => {
    // Test trailing slash removal - this is implementation dependent
    const apiClient = wrapApi(context, 'https://api.example.com/');
    expect(apiClient).toBeDefined();
  });

  test('wrap api relative url handling', async () => {
    const apiClient = wrapApi(context, 'https://api.example.com');

    const mockResponse = {
      status: 200,
      statusText: 'OK',
      ok: true,
      headers: new Headers(),
      text: async () => '{}',
    };
    (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue(mockResponse as Response);

    // Test relative URL
    await apiClient.request('GET', '/users');

    // Verify full URL was constructed
    expect(global.fetch).toHaveBeenCalledTimes(1);
    const fetchCall = (global.fetch as jest.MockedFunction<typeof fetch>).mock.calls[0];
    expect(fetchCall[0].toString()).toContain('https://api.example.com/users');
  });

  test('wrap api absolute url handling', async () => {
    const apiClient = wrapApi(context, 'https://api.example.com');

    const mockResponse = {
      status: 200,
      statusText: 'OK',
      ok: true,
      headers: new Headers(),
      text: async () => '{}',
    };
    (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue(mockResponse as Response);

    // Test absolute URL
    await apiClient.request('POST', 'https://other-api.com/webhook');

    // Verify URL was passed through unchanged
    const fetchCall = (global.fetch as jest.MockedFunction<typeof fetch>).mock.calls[0];
    expect(fetchCall[0].toString()).toContain('https://other-api.com/webhook');
  });
});

describe('HTTP Client Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('end to end workflow', async () => {
    // Create context
    const context = new AgentContext({
      agent_type: 'integration_test',
      user: 'tester',
    });
    context.updateGoal('test full workflow');

    // Setup mock response
    const mockResponse = {
      status: 200,
      statusText: 'OK',
      ok: true,
      headers: new Headers(),
      text: async () => JSON.stringify({ success: true }),
    };
    (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue(mockResponse as Response);

    // Create OCP client
    const client = new OCPHTTPClient(context);

    // Mock context interaction (without calling the real method)
    const addInteractionMock = jest.fn();
    const originalAddInteraction = context.addInteraction;
    context.addInteraction = addInteractionMock;

    // Make request
    const response = await client.get('https://api.example.com/users', {
      params: { page: 1, limit: 10 },
    });

    // Verify fetch was called correctly
    expect(global.fetch).toHaveBeenCalledTimes(1);
    const fetchCall = (global.fetch as jest.MockedFunction<typeof fetch>).mock.calls[0];

    expect(fetchCall[0].toString()).toContain('https://api.example.com/users');
    expect(fetchCall[0].toString()).toContain('page=1');
    expect(fetchCall[0].toString()).toContain('limit=10');

    // Verify OCP headers were included
    const headers = fetchCall[1]?.headers as Record<string, string>;
    const expectedHeaders = createOCPHeaders(context);
    for (const [key, value] of Object.entries(expectedHeaders)) {
      expect(headers[key]).toBe(value);
    }

    // Verify interaction was logged
    expect(addInteractionMock).toHaveBeenCalledTimes(1);
    const interactionCall = addInteractionMock.mock.calls[0];
    expect(interactionCall[0]).toBe('api_call_get');
    expect(interactionCall[1]).toBe('https://api.example.com/users?page=1&limit=10');
    expect(interactionCall[2]).toBe('200');

    // Verify response
    expect(response.status).toBe(200);

    // Restore original method
    context.addInteraction = originalAddInteraction;
  });

  test('multiple requests context tracking', async () => {
    const context = new AgentContext({ agent_type: 'multi_test' });

    // Create responses for different requests
    const responses = [
      {
        status: 200,
        statusText: 'OK',
        ok: true,
        headers: new Headers(),
        text: async () => '{}',
      },
      {
        status: 201,
        statusText: 'Created',
        ok: true,
        headers: new Headers(),
        text: async () => '{}',
      },
      {
        status: 404,
        statusText: 'Not Found',
        ok: false,
        headers: new Headers(),
        text: async () => '{}',
      },
    ];

    (global.fetch as jest.MockedFunction<typeof fetch>)
      .mockResolvedValueOnce(responses[0] as Response)
      .mockResolvedValueOnce(responses[1] as Response)
      .mockResolvedValueOnce(responses[2] as Response);

    const client = new OCPHTTPClient(context);
    const addInteractionSpy = jest.spyOn(context, 'addInteraction');

    // Make multiple requests
    await client.get('https://api.example.com/users');
    await client.post('https://api.example.com/users', { json: { name: 'test' } });
    await client.delete('https://api.example.com/users/999');

    // Verify all interactions were logged
    expect(addInteractionSpy).toHaveBeenCalledTimes(3);

    // Check interaction details
    const calls = addInteractionSpy.mock.calls;

    expect(calls[0][0]).toBe('api_call_get');
    expect(calls[0][2]).toBe('200');

    expect(calls[1][0]).toBe('api_call_post');
    expect(calls[1][2]).toBe('201');

    expect(calls[2][0]).toBe('api_call_delete');
    expect(calls[2][2]).toBe('404');

    addInteractionSpy.mockRestore();
  });
});
