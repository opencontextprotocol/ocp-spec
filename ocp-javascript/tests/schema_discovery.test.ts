/**
 * Tests for OCP schema discovery functionality.
 */

import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { OCPSchemaDiscovery } from '../src/schema_discovery.js';
import type { OCPAPISpec, OCPTool } from '../src/schema_discovery.js';

// Mock fetch globally
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('OCP Schema Discovery', () => {
  let discovery: OCPSchemaDiscovery;

  const sampleOpenApiSpec = {
    openapi: '3.0.0',
    info: {
      title: 'Test API',
      version: '1.0.0',
    },
    servers: [{ url: 'https://api.example.com' }],
    paths: {
      '/users': {
        get: {
          summary: 'List users',
          description: 'Get a list of all users',
          parameters: [
            {
              name: 'limit',
              in: 'query',
              schema: { type: 'integer' },
              required: false,
            },
          ],
        },
        post: {
          summary: 'Create user',
          description: 'Create a new user',
          requestBody: {
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    name: { type: 'string' },
                    email: { type: 'string' },
                  },
                  required: ['name', 'email'],
                },
              },
            },
          },
        },
      },
      '/users/{id}': {
        get: {
          summary: 'Get user',
          description: 'Get a specific user by ID',
          parameters: [
            {
              name: 'id',
              in: 'path',
              schema: { type: 'string' },
              required: true,
            },
          ],
        },
      },
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    discovery = new OCPSchemaDiscovery();
  });

  describe('Parse OpenAPI Spec', () => {
    test('parse openapi spec', () => {
      const apiSpec = (discovery as any)._parseOpenApiSpec(
        sampleOpenApiSpec,
        'https://api.example.com'
      );

      expect(apiSpec.title).toBe('Test API');
      expect(apiSpec.version).toBe('1.0.0');
      expect(apiSpec.base_url).toBe('https://api.example.com');
      expect(apiSpec.tools.length).toBe(3); // GET /users, POST /users, GET /users/{id}
    });

    test('generate tools from spec', () => {
      const apiSpec = (discovery as any)._parseOpenApiSpec(
        sampleOpenApiSpec,
        'https://api.example.com'
      );

      const tools = apiSpec.tools;
      expect(tools.length).toBe(3); // GET /users, POST /users, GET /users/{id}

      // Check that we have the expected tools with deterministic names
      const toolNames = tools.map((t: OCPTool) => t.name);
      const expectedNames = ['get__users', 'post__users', 'get__users_{id}'];

      for (const expectedName of expectedNames) {
        expect(toolNames).toContain(expectedName);
      }

      // Check GET /users tool
      const getUsers = tools.find((t: OCPTool) => t.name === 'get__users');
      expect(getUsers).toBeDefined();
      expect(getUsers!.method).toBe('GET');
      expect(getUsers!.path).toBe('/users');
      expect(getUsers!.description).toBe('Get a list of all users');
      expect(getUsers!.parameters['limit']).toBeDefined();
      expect(getUsers!.parameters['limit'].type).toBe('integer');
      expect(getUsers!.parameters['limit'].location).toBe('query');
      expect(getUsers!.parameters['limit'].required).toBe(false);

      // Check POST /users tool
      const postUsers = tools.find((t: OCPTool) => t.name === 'post__users');
      expect(postUsers).toBeDefined();
      expect(postUsers!.method).toBe('POST');
      expect(postUsers!.path).toBe('/users');
      expect(postUsers!.parameters['name']).toBeDefined();
      expect(postUsers!.parameters['email']).toBeDefined();
      expect(postUsers!.parameters['name'].required).toBe(true);
      expect(postUsers!.parameters['email'].required).toBe(true);

      // Check GET /users/{id} tool
      const getUsersId = tools.find((t: OCPTool) => t.name === 'get__users_{id}');
      expect(getUsersId).toBeDefined();
      expect(getUsersId!.method).toBe('GET');
      expect(getUsersId!.path).toBe('/users/{id}');
      expect(getUsersId!.parameters['id']).toBeDefined();
      expect(getUsersId!.parameters['id'].location).toBe('path');
      expect(getUsersId!.parameters['id'].required).toBe(true);
    });
  });

  describe('Discover API', () => {
    test('discover api success', async () => {
      // Mock fetch response
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: async () => sampleOpenApiSpec,
      } as Response);

      const apiSpec = await discovery.discoverApi('https://api.example.com/openapi.json');

      expect(apiSpec.title).toBe('Test API');
      expect(apiSpec.tools.length).toBe(3);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    test('discover api with base url override', async () => {
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: async () => sampleOpenApiSpec,
      } as Response);

      const apiSpec = await discovery.discoverApi(
        'https://api.example.com/openapi.json',
        'https://custom.example.com'
      );

      expect(apiSpec.base_url).toBe('https://custom.example.com');
    });

    test('discover api failure', async () => {
      (global.fetch as jest.MockedFunction<typeof fetch>).mockRejectedValue(
        new Error('Network error')
      );

      await expect(
        discovery.discoverApi('https://api.example.com/openapi.json')
      ).rejects.toThrow('Network error');
    });
  });

  describe('Search Tools', () => {
    test('search tools', () => {
      // Create some sample tools
      const tools: OCPTool[] = [
        {
          name: 'list_users',
          description: 'Get all users from the system',
          method: 'GET',
          path: '/users',
          parameters: {},
          response_schema: {},
          operation_id: undefined,
          tags: [],
        },
        {
          name: 'create_user',
          description: 'Create a new user account',
          method: 'POST',
          path: '/users',
          parameters: {},
          response_schema: {},
          operation_id: undefined,
          tags: [],
        },
        {
          name: 'list_orders',
          description: 'Get customer orders',
          method: 'GET',
          path: '/orders',
          parameters: {},
          response_schema: {},
          operation_id: undefined,
          tags: [],
        },
      ];

      const apiSpec: OCPAPISpec = {
        title: 'Test API',
        version: '1.0.0',
        base_url: 'https://api.example.com',
        description: 'A test API for testing purposes',
        tools: tools,
        raw_spec: {},
      };

      // Test search by name
      const userTools = discovery.searchTools(apiSpec, 'user');
      expect(userTools.length).toBe(2);
      expect(
        userTools.every(
          (tool) =>
            tool.name.toLowerCase().includes('user') ||
            tool.description.toLowerCase().includes('user')
        )
      ).toBe(true);

      // Test search by description
      const createTools = discovery.searchTools(apiSpec, 'create');
      expect(createTools.length).toBe(1);
      expect(createTools[0].name).toBe('create_user');

      // Test no matches
      const noMatches = discovery.searchTools(apiSpec, 'nonexistent');
      expect(noMatches.length).toBe(0);
    });
  });

  describe('Generate Documentation', () => {
    test('generate tool documentation', () => {
      const tool: OCPTool = {
        name: 'create_user',
        description: 'Create a new user account',
        method: 'POST',
        path: '/users',
        parameters: {
          name: {
            type: 'string',
            description: "User's full name",
            required: true,
            location: 'body',
          },
          email: {
            type: 'string',
            description: "User's email address",
            required: true,
            location: 'body',
          },
          age: {
            type: 'integer',
            description: "User's age",
            required: false,
            location: 'body',
          },
        },
        response_schema: {},
        operation_id: undefined,
        tags: [],
      };

      const doc = discovery.generateToolDocumentation(tool);

      expect(doc).toContain('create_user');
      expect(doc).toContain('Create a new user account');
      expect(doc).toContain('POST');
      expect(doc).toContain('/users');
      expect(doc).toContain('name');
      expect(doc).toContain('email');
      expect(doc).toContain('age');
      expect(doc.toLowerCase()).toContain('required');
    });
  });

  describe('OCPTool', () => {
    test('tool creation', () => {
      const tool: OCPTool = {
        name: 'test_tool',
        description: 'A test tool',
        method: 'GET',
        path: '/test',
        parameters: { param: { type: 'string' } },
        response_schema: {},
        operation_id: undefined,
        tags: [],
      };

      expect(tool.name).toBe('test_tool');
      expect(tool.description).toBe('A test tool');
      expect(tool.method).toBe('GET');
      expect(tool.path).toBe('/test');
      expect(tool.parameters['param'].type).toBe('string');
    });
  });

  describe('OCPAPISpec', () => {
    test('api spec creation', () => {
      const tools: OCPTool[] = [
        {
          name: 'tool1',
          description: 'Description 1',
          method: 'GET',
          path: '/path1',
          parameters: {},
          response_schema: {},
          operation_id: undefined,
          tags: [],
        },
        {
          name: 'tool2',
          description: 'Description 2',
          method: 'POST',
          path: '/path2',
          parameters: {},
          response_schema: {},
          operation_id: undefined,
          tags: [],
        },
      ];

      const apiSpec: OCPAPISpec = {
        title: 'Test API',
        version: '1.0.0',
        base_url: 'https://api.example.com',
        description: 'A test API for testing purposes',
        tools: tools,
        raw_spec: {},
      };

      expect(apiSpec.title).toBe('Test API');
      expect(apiSpec.version).toBe('1.0.0');
      expect(apiSpec.base_url).toBe('https://api.example.com');
      expect(apiSpec.description).toBe('A test API for testing purposes');
      expect(apiSpec.tools.length).toBe(2);
      expect(apiSpec.tools[0].name).toBe('tool1');
      expect(apiSpec.tools[1].name).toBe('tool2');
    });
  });
});
