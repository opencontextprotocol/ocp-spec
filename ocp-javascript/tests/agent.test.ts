/**
 * Tests for OCP Agent functionality.
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { OCPAgent } from '../src/agent.js';
import type { OCPAPISpec, OCPTool } from '../src/schema_discovery.js';

// Mock fetch globally
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('OCP Agent', () => {
  let agent: OCPAgent;

  const sampleApiSpec: OCPAPISpec = {
    title: 'Test API',
    version: '1.0.0',
    base_url: 'https://api.test.com',
    description: 'A test API for testing purposes',
    tools: [
      {
        name: 'get_items',
        description: 'List all items',
        method: 'GET',
        path: '/items',
        parameters: {
          limit: {
            type: 'integer',
            required: false,
            location: 'query',
          },
        },
        response_schema: {},
        operation_id: undefined,
        tags: [],
      },
      {
        name: 'post_items',
        description: 'Create a new item',
        method: 'POST',
        path: '/items',
        parameters: {
          name: {
            type: 'string',
            required: true,
            location: 'body',
          },
          description: {
            type: 'string',
            required: false,
            location: 'body',
          },
        },
        response_schema: {},
        operation_id: undefined,
        tags: [],
      },
      {
        name: 'get_items_id',
        description: 'Get a specific item',
        method: 'GET',
        path: '/items/{id}',
        parameters: {
          id: {
            type: 'string',
            required: true,
            location: 'path',
          },
        },
        response_schema: {},
        operation_id: undefined,
        tags: [],
      },
    ],
    raw_spec: {},
  };

  beforeEach(() => {
    jest.clearAllMocks();
    agent = new OCPAgent('test_agent', 'test_user', 'test_workspace', 'test goal', undefined, false);
  });

  describe('Agent Creation', () => {
    test('agent creation', () => {
      expect(agent.context.agent_type).toBe('test_agent');
      expect(agent.context.user).toBe('test_user');
      expect(agent.context.workspace).toBe('test_workspace');
      expect(agent.context.current_goal).toBe('test goal');
      expect(agent.knownApis.size).toBe(0);
      expect(agent['discovery']).toBeDefined();
      expect(agent['httpClient']).toBeDefined();
    });
  });

  describe('Register API', () => {
    test('register api', async () => {
      // Mock discovery
      const mockDiscoverApi = jest.fn<(url: string, baseUrl?: string) => Promise<OCPAPISpec>>().mockResolvedValue(sampleApiSpec);
      agent['discovery'].discoverApi = mockDiscoverApi;

      const result = await agent.registerApi('test_api', 'https://api.test.com/openapi.json');

      expect(result).toEqual(sampleApiSpec);
      expect(agent.knownApis.get('test_api')).toEqual(sampleApiSpec);
      expect(agent.context.api_specs['test_api']).toBeDefined();
      expect(agent.context.history.length).toBeGreaterThanOrEqual(1);
      expect(agent.context.history[0].action).toBe('api_registered');

      expect(mockDiscoverApi).toHaveBeenCalledWith('https://api.test.com/openapi.json', undefined);
    });

    test('register api with base url', async () => {
      const mockDiscoverApi = jest.fn<(url: string, baseUrl?: string) => Promise<OCPAPISpec>>().mockResolvedValue(sampleApiSpec);
      agent['discovery'].discoverApi = mockDiscoverApi;

      await agent.registerApi(
        'test_api',
        'https://api.test.com/openapi.json',
        'https://custom.test.com'
      );

      expect(mockDiscoverApi).toHaveBeenCalledWith(
        'https://api.test.com/openapi.json',
        'https://custom.test.com'
      );
    });
  });

  describe('List Tools', () => {
    test('list tools no apis', () => {
      const tools = agent.listTools();
      expect(tools).toEqual([]);
    });

    test('list tools with api', () => {
      agent.knownApis.set('test_api', sampleApiSpec);

      // List all tools
      const allTools = agent.listTools();
      expect(allTools.length).toBe(3);
      expect(allTools.every((tool) => ['get_items', 'post_items', 'get_items_id'].includes(tool.name))).toBe(
        true
      );

      // List tools for specific API
      const apiTools = agent.listTools('test_api');
      expect(apiTools.length).toBe(3);
      expect(apiTools).toEqual(sampleApiSpec.tools);
    });

    test('list tools unknown api', () => {
      expect(() => agent.listTools('unknown_api')).toThrow('Unknown API: unknown_api');
    });
  });

  describe('Get Tool', () => {
    test('get tool', () => {
      agent.knownApis.set('test_api', sampleApiSpec);

      // Get existing tool
      const tool = agent.getTool('get_items');
      expect(tool).toBeDefined();
      expect(tool!.name).toBe('get_items');
      expect(tool!.method).toBe('GET');

      // Get tool from specific API
      const tool2 = agent.getTool('post_items', 'test_api');
      expect(tool2).toBeDefined();
      expect(tool2!.name).toBe('post_items');

      // Get non-existent tool
      const tool3 = agent.getTool('nonexistent');
      expect(tool3).toBeUndefined();
    });
  });

  describe('Search Tools', () => {
    test('search tools', () => {
      agent.knownApis.set('test_api', sampleApiSpec);

      // Mock search implementation
      const mockSearch = jest.fn<(spec: OCPAPISpec, query: string) => OCPTool[]>().mockReturnValue([sampleApiSpec.tools[0]]);
      agent['discovery'].searchTools = mockSearch;

      // Search all APIs
      const results = agent.searchTools('list');
      expect(results.length).toBe(1);
      expect(mockSearch).toHaveBeenCalledWith(sampleApiSpec, 'list');

      // Search specific API
      mockSearch.mockClear();
      const results2 = agent.searchTools('list', 'test_api');
      expect(results2.length).toBe(1);
      expect(mockSearch).toHaveBeenCalledWith(sampleApiSpec, 'list');

      // Search unknown API
      const results3 = agent.searchTools('list', 'unknown_api');
      expect(results3).toEqual([]);
    });
  });

  describe('Parameter Validation', () => {
    test('validate parameters', () => {
      const postTool = sampleApiSpec.tools[1]; // post_items tool

      // Valid parameters
      const errors1 = (agent as any)._validateParameters(postTool, { name: 'test' });
      expect(errors1).toEqual([]);

      // Missing required parameter
      const errors2 = (agent as any)._validateParameters(postTool, {});
      expect(errors2.length).toBe(1);
      expect(errors2[0]).toContain('Missing required parameter: name');

      // Wrong parameter type (basic validation doesn't catch this)
      const errors3 = (agent as any)._validateParameters(postTool, { name: 123 });
      expect(errors3).toEqual([]);
    });
  });

  describe('Build Request', () => {
    test('build request', () => {
      // Test query parameters
      const getTool = sampleApiSpec.tools[0]; // get_items tool
      const [url1, params1] = (agent as any)._buildRequest(sampleApiSpec, getTool, { limit: 10 });

      expect(url1).toBe('https://api.test.com/items');
      expect(params1.params.limit).toBe(10);
      expect(params1.timeout).toBe(30000);

      // Test path parameters
      const getTool2 = sampleApiSpec.tools[2]; // get_items_id tool
      const [url2, params2] = (agent as any)._buildRequest(sampleApiSpec, getTool2, { id: '123' });

      expect(url2).toBe('https://api.test.com/items/123');
      expect(!params2.params || Object.keys(params2.params).length === 0).toBe(true);

      // Test body parameters
      const postTool = sampleApiSpec.tools[1]; // post_items tool
      const [url3, params3] = (agent as any)._buildRequest(sampleApiSpec, postTool, {
        name: 'test item',
        description: 'test desc',
      });

      expect(url3).toBe('https://api.test.com/items');
      expect(params3.json.name).toBe('test item');
      expect(params3.json.description).toBe('test desc');
    });
  });

  describe('Call Tool', () => {
    test('call tool success', async () => {
      agent.knownApis.set('test_api', sampleApiSpec);

      // Mock successful response
      const mockResponse = {
        status: 200,
        statusText: 'OK',
        ok: true,
        data: { success: true },
        text: '{"success": true}',
        headers: new Headers(),
        json: async () => ({ success: true }),
      };

      const mockRequest = jest.fn<(method: string, url: string, options?: any) => Promise<typeof mockResponse>>().mockResolvedValue(mockResponse);
      agent['httpClient'].request = mockRequest;

      const response = await agent.callTool('get_items', { limit: 5 });

      expect(response).toEqual(mockResponse);
      expect(agent.context.history.length).toBeGreaterThanOrEqual(2);

      // Check that the request was made correctly
      expect(mockRequest).toHaveBeenCalledTimes(1);
      const callArgs = mockRequest.mock.calls[0];
      expect(callArgs[0]).toBe('GET'); // method
      expect(callArgs[1]).toBe('https://api.test.com/items'); // url
      expect(callArgs[2].params.limit).toBe(5);
    });

    test('call tool not found', async () => {
      agent.knownApis.set('test_api', sampleApiSpec);

      await expect(agent.callTool('nonexistent')).rejects.toThrow("Tool 'nonexistent' not found");
    });

    test('call tool validation error', async () => {
      agent.knownApis.set('test_api', sampleApiSpec);

      await expect(agent.callTool('post_items', {})).rejects.toThrow('Parameter validation failed');
    });
  });

  describe('Tool Documentation', () => {
    test('get tool documentation', () => {
      agent.knownApis.set('test_api', sampleApiSpec);

      const mockGenerateDoc = jest.fn<(tool: OCPTool) => string>().mockReturnValue('Tool documentation');
      agent['discovery'].generateToolDocumentation = mockGenerateDoc;

      const doc = agent.getToolDocumentation('get_items');
      expect(doc).toBe('Tool documentation');
      expect(mockGenerateDoc).toHaveBeenCalledWith(sampleApiSpec.tools[0]);

      // Test non-existent tool
      const doc2 = agent.getToolDocumentation('nonexistent');
      expect(doc2.toLowerCase()).toContain('not found');
    });
  });

  describe('Update Goal', () => {
    test('update goal', () => {
      const initialInteractions = agent.context.history.length;

      agent.updateGoal('new goal', 'goal summary');

      expect(agent.context.current_goal).toBe('new goal');
      expect(agent.context.context_summary).toBe('goal summary');
    });
  });

  describe('Registry Integration', () => {
    test('register api from registry', async () => {
      // Mock registry
      const mockGetApiSpec = jest.fn<(apiName: string, baseUrl?: string) => Promise<OCPAPISpec>>().mockResolvedValue(sampleApiSpec);
      const mockRegistry = {
        getApiSpec: mockGetApiSpec,
        registryUrl: 'https://test-registry.com',
      };

      // Create agent with custom registry
      const agentWithRegistry = new OCPAgent('test_agent', undefined, undefined, undefined, 'https://test-registry.com', false);

      agentWithRegistry['registry'] = mockRegistry as any;

      // Register API from registry
      const result = await agentWithRegistry.registerApi('test_api');

      // Verify registry was called correctly
      expect(mockGetApiSpec).toHaveBeenCalledWith('test_api', undefined);

      // Verify API was registered
      expect(result).toEqual(sampleApiSpec);
      expect(agentWithRegistry.knownApis.get('test_api')).toEqual(sampleApiSpec);

      // Verify context tracking
      expect(agentWithRegistry.context.api_specs['test_api']).toBe('registry:test_api');

      // Verify interaction logging
      expect(agentWithRegistry.context.history.length).toBeGreaterThanOrEqual(1);
      const interaction = agentWithRegistry.context.history[0];
      expect(interaction.action).toBe('api_registered');
      expect(interaction.api_endpoint).toBe('registry:test_api');
      expect(interaction.metadata.source).toBe('registry');
    });

    test('register api from openapi url', async () => {
      const mockDiscoverApi = jest.fn<(url: string, baseUrl?: string) => Promise<OCPAPISpec>>().mockResolvedValue(sampleApiSpec);
      agent['discovery'].discoverApi = mockDiscoverApi as any;

      // Register API with URL
      const result = await agent.registerApi('test_api', 'https://api.test.com/openapi.json');

      // Verify discovery was called
      expect(mockDiscoverApi).toHaveBeenCalled();

      // Verify API was registered
      expect(result).toEqual(sampleApiSpec);
      expect(agent.knownApis.get('test_api')).toBeDefined();

      // Verify context tracking
      expect(agent.context.api_specs['test_api']).toBe('https://api.test.com/openapi.json');

      // Verify metadata indicates OpenAPI source
      const interaction = agent.context.history[0];
      expect(interaction.metadata.source).toBe('openapi');
    });

    test('register api with base url override', async () => {
      const mockGetApiSpec = jest.fn<(apiName: string, baseUrl?: string) => Promise<OCPAPISpec>>().mockResolvedValue(sampleApiSpec);
      const mockRegistry = {
        getApiSpec: mockGetApiSpec,
        registryUrl: 'https://registry.ocp.dev',
      };

      const agentWithRegistry = new OCPAgent('test_agent', undefined, undefined, undefined, undefined, false);
      agentWithRegistry['registry'] = mockRegistry as any;

      // Register with base URL override
      await agentWithRegistry.registerApi('test_api', undefined, 'https://custom.test.com');

      // Verify base_url was passed to registry
      expect(mockGetApiSpec).toHaveBeenCalled();
    });

    test('agent initialization with registry url', () => {
      const agentWithRegistry = new OCPAgent('test_agent', undefined, undefined, undefined, 'https://custom-registry.com', false);

      expect((agentWithRegistry['registry'] as any).registryUrl).toBe('https://custom-registry.com');
    });
  });
});
