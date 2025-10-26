/**
 * Tests for OCP Registry functionality.
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { OCPRegistry } from '../src/registry.js';
import type { OCPAPISpec, OCPTool } from '../src/schema_discovery.js';
import { RegistryUnavailable, APINotFound } from '../src/errors.js';

// Mock fetch globally
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

describe('OCP Registry', () => {
  let originalEnv: typeof process.env;

  beforeEach(() => {
    jest.clearAllMocks();
    // Save original environment
    originalEnv = { ...process.env };
  });

  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
  });

  const sampleApiEntry = {
    name: 'httpbin',
    display_name: 'HTTPBin Testing Service',
    description: 'HTTP testing service',
    openapi_url: 'https://httpbin.org/spec.json',
    base_url: 'https://httpbin.org/',
    category: 'development',
    auth_config: {
      type: 'none',
      header_name: null,
      instructions: 'No authentication required',
    },
    tags: ['testing', 'debugging'],
    tool_count: 2,
    tools: [
      {
        name: 'get_get',
        description: 'Returns GET request data',
        method: 'GET',
        path: '/get',
        parameters: {},
        response_schema: {},
      },
      {
        name: 'post_post',
        description: 'Returns POST request data',
        method: 'POST',
        path: '/post',
        parameters: {},
        response_schema: {},
      },
    ],
  };

  describe('Registry Initialization', () => {
    test('init default url', () => {
      const registry = new OCPRegistry();
      expect((registry as any).registryUrl).toBe('https://registry.ocp.dev');
    });

    test('init custom url', () => {
      const registry = new OCPRegistry('https://custom-registry.com');
      expect((registry as any).registryUrl).toBe('https://custom-registry.com');
    });

    test('init env var', () => {
      process.env.OCP_REGISTRY_URL = 'https://env-registry.com';
      const registry = new OCPRegistry();
      expect((registry as any).registryUrl).toBe('https://env-registry.com');
    });

    test('init invalid url', () => {
      expect(() => new OCPRegistry('invalid-url')).toThrow('Invalid registry URL');
    });
  });

  describe('Get API Spec', () => {
    test('get api spec success', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      // Mock fetch
      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => sampleApiEntry,
      } as Response);

      const apiSpec = await registry.getApiSpec('httpbin');

      expect(apiSpec.title).toBe('HTTPBin Testing Service');
      expect(apiSpec.base_url).toBe('https://httpbin.org/');
      expect(apiSpec.tools.length).toBe(2);
      expect(apiSpec.tools[0].name).toBe('get_get');
      expect(apiSpec.tools[1].name).toBe('post_post');
    });

    test('get api spec with base url override', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => sampleApiEntry,
      } as Response);

      const apiSpec = await registry.getApiSpec('httpbin', 'https://custom.httpbin.org');

      expect(apiSpec.base_url).toBe('https://custom.httpbin.org');
    });

    test('get api spec not found', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      let callCount = 0;
      (global.fetch as jest.MockedFunction<typeof fetch>).mockImplementation(async (url) => {
        callCount++;
        if (callCount === 1) {
          // First call: API not found
          return {
            ok: false,
            status: 404,
          } as Response;
        } else {
          // Second call: Search returns suggestions
          return {
            ok: true,
            status: 200,
            json: async () => ({ results: [{ name: 'httpbin' }] }),
          } as Response;
        }
      });

      await expect(registry.getApiSpec('nonexistent')).rejects.toThrow(APINotFound);
      
      try {
        await registry.getApiSpec('nonexistent');
      } catch (error) {
        expect((error as APINotFound).apiName).toBe('nonexistent');
        expect((error as APINotFound).suggestions).toContain('httpbin');
      }
    });

    test('get api spec registry unavailable', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      (global.fetch as jest.MockedFunction<typeof fetch>).mockRejectedValue(
        new Error('Connection failed')
      );

      await expect(registry.getApiSpec('httpbin')).rejects.toThrow(RegistryUnavailable);
      
      try {
        await registry.getApiSpec('httpbin');
      } catch (error) {
        expect((error as RegistryUnavailable).registryUrl).toContain('test-registry.ocp.dev');
      }
    });
  });

  describe('Search APIs', () => {
    test('search apis success', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      const searchResponse = {
        results: [{ name: 'github' }, { name: 'gitlab' }],
      };

      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => searchResponse,
      } as Response);

      const results = await registry.searchApis('git');

      expect(results).toEqual(['github', 'gitlab']);
    });

    test('search apis failure', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      (global.fetch as jest.MockedFunction<typeof fetch>).mockRejectedValue(
        new Error('Connection failed')
      );

      const results = await registry.searchApis('git');

      // Should return empty array on failure
      expect(results).toEqual([]);
    });
  });

  describe('List APIs', () => {
    test('list apis success', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      const apiList = [{ name: 'github' }, { name: 'stripe' }, { name: 'httpbin' }];

      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => apiList,
      } as Response);

      const results = await registry.listApis();

      expect(results).toEqual(['github', 'stripe', 'httpbin']);
    });

    test('list apis failure', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      (global.fetch as jest.MockedFunction<typeof fetch>).mockRejectedValue(
        new Error('Connection failed')
      );

      const results = await registry.listApis();

      // Should return empty array on failure
      expect(results).toEqual([]);
    });
  });

  describe('Internal Methods', () => {
    test('entry to spec conversion', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      const apiSpec = await (registry as any)._entryToSpec(sampleApiEntry);

      expect(apiSpec.title).toBe('HTTPBin Testing Service');
      expect(apiSpec.version).toBe('1.0.0');
      expect(apiSpec.base_url).toBe('https://httpbin.org/');

      // Check tools conversion
      expect(apiSpec.tools.length).toBe(2);
      const tool1 = apiSpec.tools[0];
      expect(tool1.name).toBe('get_get');
      expect(tool1.method).toBe('GET');
      expect(tool1.path).toBe('/get');
    });

    test('get suggestions exact match', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      (global.fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ results: [{ name: 'github' }] }),
      } as Response);

      const suggestions = await (registry as any)._getSuggestions('github');

      expect(suggestions).toEqual(['github']);
    });

    test('get suggestions partial match', async () => {
      const registry = new OCPRegistry('https://test-registry.ocp.dev');

      let callCount = 0;
      (global.fetch as jest.MockedFunction<typeof fetch>).mockImplementation(async (url) => {
        callCount++;
        if (callCount === 1) {
          // First call returns no results
          return {
            ok: true,
            status: 200,
            json: async () => ({ results: [] }),
          } as Response;
        } else {
          // Second call with partial query returns results
          return {
            ok: true,
            status: 200,
            json: async () => ({ results: [{ name: 'github' }] }),
          } as Response;
        }
      });

      const suggestions = await (registry as any)._getSuggestions('unknown');

      expect(suggestions).toEqual(['github']);
    });
  });
});
