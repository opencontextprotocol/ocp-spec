/**
 * Tests for OCP validation functionality.
 */

import { describe, test, expect } from '@jest/globals';
import {
  validateContext,
  validateContextDict,
  ValidationResult,
  getSchema,
  validateAndFixContext,
  OCP_CONTEXT_SCHEMA,
} from '../src/validation.js';
import { AgentContext } from '../src/context.js';

describe('ValidationResult', () => {
  test('valid result', () => {
    const result = new ValidationResult(true);
    expect(result.valid).toBe(true);
    expect(result.errors).toEqual([]);
    // In JavaScript, objects are always truthy, so we check .valid directly
    expect(result.valid).toBe(true);
    expect(result.toString()).toBe('Valid OCP context');
  });

  test('invalid result', () => {
    const errors = ['Error 1', 'Error 2'];
    const result = new ValidationResult(false, errors);
    expect(result.valid).toBe(false);
    expect(result.errors).toEqual(errors);
    // In JavaScript, objects are always truthy, so we check .valid directly
    expect(result.valid).toBe(false);
    expect(result.toString()).toBe('Invalid OCP context: Error 1; Error 2');
  });

  test('invalid result with no errors', () => {
    const result = new ValidationResult(false);
    expect(result.valid).toBe(false);
    expect(result.errors).toEqual([]);
    expect(result.toString()).toBe('Invalid OCP context: ');
  });
});

describe('Context Validation', () => {
  test('validate valid context', () => {
    const context = new AgentContext({
      agent_type: 'ide_copilot',
      user: 'test_user',
      workspace: 'test_workspace',
      current_goal: 'test_goal',
    });

    const result = validateContext(context);
    expect(result.valid).toBe(true);
    expect(result.errors).toEqual([]);
  });

  test('validate minimal context', () => {
    const context = new AgentContext({ agent_type: 'generic_agent' });

    const result = validateContext(context);
    expect(result.valid).toBe(true);
  });

  test('validate context with custom agent type', () => {
    const context = new AgentContext({ agent_type: 'custom_agent' });

    const result = validateContext(context);
    // Should be valid since any string is allowed
    expect(result.valid).toBe(true);
    expect(result.errors.length).toBe(0);
  });

  test('validate context missing agent type', () => {
    const context = new AgentContext({ agent_type: '' });

    const result = validateContext(context);
    // Empty string should still be valid if the schema allows it
    // The schema now just requires type: string, not specific values
    expect(result.valid).toBe(true);
  });

  test('validate context with all fields', () => {
    const context = new AgentContext({
      agent_type: 'ide_copilot',
      user: 'developer',
      workspace: '/home/user/project',
      current_file: 'main.js',
      current_goal: 'debug error',
      context_summary: 'Working on bug fix',
      error_context: 'NullPointerException at line 42',
    });

    // Add some history and changes
    context.addInteraction('tool_call', 'https://api.test.com', 'success');
    context.addRecentChange('Modified main.js');
    context.addApiSpec('test_api', 'https://api.test.com/openapi.json');

    const result = validateContext(context);
    expect(result.valid).toBe(true);
  });
});

describe('Dict Validation', () => {
  test('validate valid dict', () => {
    const contextDict = {
      context_id: 'ocp-12345678',
      agent_type: 'ide_copilot',
      user: 'test_user',
      workspace: 'test_workspace',
      current_file: null,
      session: {
        start_time: '2024-01-01T00:00:00Z',
        interaction_count: 0,
        agent_type: 'ide_copilot',
      },
      history: [],
      current_goal: 'test_goal',
      context_summary: null,
      error_context: null,
      recent_changes: [],
      api_specs: {},
      created_at: new Date().toISOString(),
      last_updated: new Date().toISOString(),
    };

    const result = validateContextDict(contextDict);
    expect(result.valid).toBe(true);
  });

  test('validate minimal dict', () => {
    const contextDict = {
      context_id: 'ocp-abcd1234',
      agent_type: 'generic_agent',
      user: null,
      workspace: null,
      current_file: null,
      session: {
        start_time: '2024-01-01T00:00:00Z',
        interaction_count: 0,
        agent_type: 'generic_agent',
      },
      history: [],
      current_goal: null,
      context_summary: null,
      error_context: null,
      recent_changes: [],
      api_specs: {},
      created_at: new Date().toISOString(),
      last_updated: new Date().toISOString(),
    };

    const result = validateContextDict(contextDict);
    expect(result.valid).toBe(true);
  });

  test('validate invalid context id', () => {
    const contextDict = {
      context_id: 'invalid-id',
      agent_type: 'generic_agent',
    };

    const result = validateContextDict(contextDict);
    // The validation should fail due to missing required fields more than pattern mismatch
    // This should fail validation
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  test('validate missing required fields', () => {
    const contextDict = {};

    const result = validateContextDict(contextDict);
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });
});

describe('Schema Utilities', () => {
  test('get schema', () => {
    const schema = getSchema();
    expect(typeof schema).toBe('object');
    expect(schema.$id).toBe('https://opencontextprotocol.org/schemas/ocp-context.json');
    expect(schema.title).toBe('OCP Context Object');
    expect(schema.properties).toBeDefined();
    expect(schema.properties.agent_type).toBeDefined();
  });
});

describe('Validate and Fix', () => {
  test('validate and fix valid context', () => {
    const context = new AgentContext({
      agent_type: 'ide_copilot',
      user: 'test_user',
    });

    const [fixedContext, result] = validateAndFixContext(context);
    expect(result.valid).toBe(true);
    expect(fixedContext.agent_type).toBe('ide_copilot');
    expect(fixedContext.user).toBe('test_user');
  });

  test('validate and fix custom agent type', () => {
    const context = new AgentContext({ agent_type: 'custom_type' });

    const [fixedContext, result] = validateAndFixContext(context);
    expect(result.valid).toBe(true);
    expect(fixedContext.agent_type).toBe('custom_type'); // Should be preserved
  });

  test('validate and fix preserves other data', () => {
    const context = new AgentContext({
      agent_type: 'my_custom_agent',
      user: 'test_user',
      workspace: 'test_workspace',
      current_goal: 'test_goal',
    });

    // Add some data
    context.addInteraction('test', 'endpoint', 'result');
    context.addRecentChange('change1');

    const [fixedContext, result] = validateAndFixContext(context);
    expect(result.valid).toBe(true);
    expect(fixedContext.agent_type).toBe('my_custom_agent'); // Should be preserved
    expect(fixedContext.user).toBe('test_user');
    expect(fixedContext.workspace).toBe('test_workspace');
    expect(fixedContext.current_goal).toBe('test_goal');
    expect(fixedContext.history.length).toBe(1);
    expect(fixedContext.recent_changes.length).toBe(1);
  });
});

describe('Schema Constants', () => {
  test('ocp context schema structure', () => {
    expect(typeof OCP_CONTEXT_SCHEMA).toBe('object');
    expect(OCP_CONTEXT_SCHEMA.$schema).toBeDefined();
    expect(OCP_CONTEXT_SCHEMA.$id).toBeDefined();
    expect(OCP_CONTEXT_SCHEMA.properties).toBeDefined();

    const properties = OCP_CONTEXT_SCHEMA.properties as any;
    const requiredFields = ['context_id', 'agent_type'];

    for (const field of requiredFields) {
      expect(properties[field]).toBeDefined();
    }
  });

  test('agent type schema structure', () => {
    const agentTypeProp = OCP_CONTEXT_SCHEMA.properties.agent_type as any;
    expect(agentTypeProp.type).toBeDefined();
    expect(agentTypeProp.type).toBe('string');
    expect(agentTypeProp.description).toBeDefined();
    // Should not have enum constraint anymore
    expect(agentTypeProp.enum).toBeUndefined();
  });
});

describe('Validation Edge Cases', () => {
  test('validate context none', () => {
    // None context should return validation error, not raise exception
    const result = validateContext(null as any);
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  test('validate dict none', () => {
    const result = validateContextDict(null as any);
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  test('validate dict invalid type', () => {
    const result = validateContextDict('not a dict' as any);
    expect(result.valid).toBe(false);
  });

  test('context with unicode data', () => {
    const context = new AgentContext({
      agent_type: 'ide_copilot',
      user: '用户', // Chinese
      workspace: 'проект', // Cyrillic
      current_goal: '修复错误', // Chinese
    });

    const result = validateContext(context);
    expect(result.valid).toBe(true);
  });

  test('context with very long strings', () => {
    const longString = 'x'.repeat(10000);
    const context = new AgentContext({
      agent_type: 'ide_copilot',
      user: longString,
      workspace: longString,
      current_goal: longString,
    });

    const result = validateContext(context);
    expect(result.valid).toBe(true);
  });
});
