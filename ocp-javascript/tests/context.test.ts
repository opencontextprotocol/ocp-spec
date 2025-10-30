/**
 * Tests for AgentContext class functionality.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { AgentContext } from '../src/context.js';
import { OCPHeaders } from '../src/headers.js';

// Fixtures
let sampleContext: AgentContext;
let minimalContext: AgentContext;
let complexContext: AgentContext;

beforeEach(() => {
  // Sample context
  sampleContext = new AgentContext({
    agent_type: 'test_agent',
    user: 'test_user',
    workspace: 'test_workspace',
    current_file: 'test_file.js',
  });
  sampleContext.updateGoal('test_goal', 'Testing OCP functionality');
  sampleContext.addInteraction('test_action', 'test_endpoint', 'test_result');

  // Minimal context
  minimalContext = new AgentContext({ agent_type: 'minimal_agent' });

  // Complex context
  complexContext = new AgentContext({
    agent_type: 'complex_agent',
    user: 'complex_user',
    workspace: 'complex_workspace',
    current_file: 'complex_file.js',
  });

  // Set a goal first
  complexContext.updateGoal('complex_goal', 'Complex goal summary');

  // Add multiple interactions
  for (let i = 0; i < 5; i++) {
    complexContext.addInteraction(
      `action_${i}`,
      `endpoint_${i}`,
      `result_${i}`,
      { step: i }
    );
  }

  // Add recent changes
  for (let i = 0; i < 3; i++) {
    complexContext.addRecentChange(`change_${i}`);
  }

  // Add API specs
  complexContext.addApiSpec('github', 'https://api.github.com');
  complexContext.addApiSpec('stripe', 'https://api.stripe.com');

  // Set error context
  complexContext.setErrorContext('Test error message', 'error_file.js');
});

describe('Agent Context Creation', () => {
  test('minimal context creation', () => {
    const context = new AgentContext({ agent_type: 'test_agent' });

    expect(context.agent_type).toBe('test_agent');
    expect(context.context_id.startsWith('ocp-')).toBe(true);
    expect(context.context_id.length).toBeGreaterThan(8); // ocp- + at least 8 chars
    expect(typeof context.session).toBe('object');
    expect(Array.isArray(context.history)).toBe(true);
    expect(typeof context.api_specs).toBe('object');
    expect(context.created_at).toBeDefined();
    expect(context.last_updated).toBeDefined();
  });

  test('full context creation', () => {
    const context = new AgentContext({
      agent_type: 'ide_copilot',
      user: 'alice',
      workspace: 'my-project',
      current_file: 'main.js',
      current_goal: 'debug_issue',
    });

    expect(context.agent_type).toBe('ide_copilot');
    expect(context.user).toBe('alice');
    expect(context.workspace).toBe('my-project');
    expect(context.current_file).toBe('main.js');
    expect(context.current_goal).toBe('debug_issue');
  });

  test('session initialization', () => {
    const context = new AgentContext({ agent_type: 'test_agent' });

    expect(context.session.start_time).toBeDefined();
    expect(context.session.interaction_count).toBeDefined();
    expect(context.session.agent_type).toBeDefined();
    expect(context.session.agent_type).toBe('test_agent');
    expect(context.session.interaction_count).toBe(0);
  });
});

describe('Agent Context Updates', () => {
  test('update goal', () => {
    const originalCount = minimalContext.session.interaction_count;

    minimalContext.updateGoal('new_goal', 'new summary');

    expect(minimalContext.current_goal).toBe('new_goal');
    expect(minimalContext.context_summary).toBe('new summary');
    expect(minimalContext.session.interaction_count).toBe(originalCount + 1);
  });

  test('add interaction', () => {
    minimalContext.addInteraction(
      'test_action',
      'test_endpoint',
      'test_result',
      { key: 'value' }
    );

    expect(minimalContext.history.length).toBe(1);
    const interaction = minimalContext.history[0];

    expect(interaction.action).toBe('test_action');
    expect(interaction.api_endpoint).toBe('test_endpoint');
    expect(interaction.result).toBe('test_result');
    expect(interaction.metadata?.key).toBe('value');
    expect(interaction.timestamp).toBeDefined();
  });

  test('set error context', () => {
    minimalContext.setErrorContext('Test error', 'error_file.js');

    expect(minimalContext.error_context).toBe('Test error');
    expect(minimalContext.current_file).toBe('error_file.js');
  });

  test('add recent change', () => {
    minimalContext.addRecentChange('change 1');
    minimalContext.addRecentChange('change 2');

    expect(minimalContext.recent_changes.length).toBe(2);
    expect(minimalContext.recent_changes).toContain('change 1');
    expect(minimalContext.recent_changes).toContain('change 2');
  });

  test('recent changes limit', () => {
    // Add 15 changes
    for (let i = 0; i < 15; i++) {
      minimalContext.addRecentChange(`change ${i}`);
    }

    // Should only keep last 10
    expect(minimalContext.recent_changes.length).toBe(10);
    expect(minimalContext.recent_changes[0]).toBe('change 5'); // First kept change
    expect(minimalContext.recent_changes[9]).toBe('change 14'); // Last change
  });

  test('add api spec', () => {
    minimalContext.addApiSpec('github', 'https://api.github.com');

    expect(minimalContext.api_specs['github']).toBeDefined();
    expect(minimalContext.api_specs['github']).toBe('https://api.github.com');
  });
});

describe('Agent Context Serialization', () => {
  test('to dict', () => {
    const data = sampleContext.toDict();

    expect(typeof data).toBe('object');
    expect(data.context_id).toBe(sampleContext.context_id);
    expect(data.agent_type).toBe(sampleContext.agent_type);
    expect(data.user).toBe(sampleContext.user);
    expect(typeof data.created_at).toBe('string');
    expect(typeof data.last_updated).toBe('string');
  });

  test('from dict', () => {
    const data = sampleContext.toDict();
    const restoredContext = AgentContext.fromDict(data);

    expect(restoredContext.context_id).toBe(sampleContext.context_id);
    expect(restoredContext.agent_type).toBe(sampleContext.agent_type);
    expect(restoredContext.user).toBe(sampleContext.user);
    expect(restoredContext.workspace).toBe(sampleContext.workspace);
    expect(restoredContext.history.length).toBe(sampleContext.history.length);
  });

  test('json roundtrip', () => {
    // Convert to JSON and back
    const jsonData = JSON.stringify(sampleContext.toDict());
    const parsedData = JSON.parse(jsonData);
    const restoredContext = AgentContext.fromDict(parsedData);

    expect(restoredContext.context_id).toBe(sampleContext.context_id);
    expect(restoredContext.current_goal).toBe(sampleContext.current_goal);
    expect(restoredContext.history.length).toBe(sampleContext.history.length);
  });
});

describe('Agent Context Utilities', () => {
  test('get conversation summary', () => {
    const summary = complexContext.getConversationSummary();

    expect(typeof summary).toBe('string');
    expect(summary.length).toBeGreaterThan(0);
    expect(summary).toContain('Goal:'); // Should include goal
    expect(summary).toContain('Error:'); // Should include error context
    expect(summary).toContain('Working on:'); // Should include current file
  });

  test('conversation summary minimal', () => {
    const summary = minimalContext.getConversationSummary();

    expect(summary).toBe('New conversation');
  });

  test('clone context', () => {
    const cloned = sampleContext.clone();

    // Should have different ID
    expect(cloned.context_id).not.toBe(sampleContext.context_id);
    expect(cloned.context_id.startsWith('ocp-')).toBe(true);

    // But same data
    expect(cloned.agent_type).toBe(sampleContext.agent_type);
    expect(cloned.user).toBe(sampleContext.user);
    expect(cloned.workspace).toBe(sampleContext.workspace);
    expect(cloned.history.length).toBe(sampleContext.history.length);
  });
});

describe('Agent Context Edge Cases', () => {
  test('empty agent type', () => {
    // Should still work, though not recommended
    const context = new AgentContext({ agent_type: '' });
    expect(context.agent_type).toBe('');
    expect(context.context_id.startsWith('ocp-')).toBe(true);
  });

  test('none values', () => {
    const context = new AgentContext({
      agent_type: 'test',
      user: null,
      workspace: null,
      current_file: null,
    });

    expect(context.user).toBeNull();
    expect(context.workspace).toBeNull();
    expect(context.current_file).toBeNull();
  });

  test('unicode handling', () => {
    const context = new AgentContext({
      agent_type: 'test',
      user: '用户', // Chinese characters
      workspace: 'проект', // Cyrillic characters
      current_file: 'файл.js',
    });

    // Should serialize/deserialize properly
    const data = context.toDict();
    const restored = AgentContext.fromDict(data);

    expect(restored.user).toBe('用户');
    expect(restored.workspace).toBe('проект');
    expect(restored.current_file).toBe('файл.js');
  });
});

describe('Agent Context Convenience Methods', () => {
  test('to headers', () => {
    const context = new AgentContext({ agent_type: 'test', user: 'alice' });
    const headers = context.toHeaders();

    expect(typeof headers).toBe('object');
    const hasOCPHeader = Object.keys(headers).some((key) => key.startsWith('OCP-'));
    expect(hasOCPHeader).toBe(true);

    // Should be able to parse back using the headers module
    const parsed = OCPHeaders.decodeContext(headers);
    expect(parsed).not.toBeNull();
    expect(parsed!.agent_type).toBe('test');
    expect(parsed!.user).toBe('alice');
  });

  test('to headers with compression', () => {
    const context = new AgentContext({ agent_type: 'test' });

    const headersCompressed = context.toHeaders(true);
    const headersUncompressed = context.toHeaders(false);

    expect(typeof headersCompressed).toBe('object');
    expect(typeof headersUncompressed).toBe('object');

    // Both should work
    expect(OCPHeaders.decodeContext(headersCompressed)).not.toBeNull();
    expect(OCPHeaders.decodeContext(headersUncompressed)).not.toBeNull();
  });

  test('update from headers success', () => {
    const context = new AgentContext({ agent_type: 'test', current_goal: 'old goal' });
    const originalId = context.context_id;

    // Create new context with different goal
    const newContext = new AgentContext({ agent_type: 'test', current_goal: 'new goal' });
    const newHeaders = newContext.toHeaders();

    // Update should return true and change the goal
    const result = context.updateFromHeaders(newHeaders);
    expect(result).toBe(true);
    expect(context.current_goal).toBe('new goal');
    // Should preserve original context_id
    expect(context.context_id).toBe(originalId);
  });

  test('update from headers no ocp headers', () => {
    const context = new AgentContext({ agent_type: 'test', current_goal: 'original' });
    const headers = { 'content-type': 'application/json' };

    const result = context.updateFromHeaders(headers);
    expect(result).toBe(false);
    expect(context.current_goal).toBe('original'); // Unchanged
  });

  test('update from headers with headers object', () => {
    const context = new AgentContext({ agent_type: 'test' });
    const newContext = new AgentContext({ agent_type: 'test', current_goal: 'updated' });

    // Create headers object (simulating Headers API)
    const headersDict = newContext.toHeaders();
    const headersObj: any = {
      entries: function* () {
        for (const [key, value] of Object.entries(headersDict)) {
          yield [key, value];
        }
      },
    };

    const result = context.updateFromHeaders(headersObj);
    expect(result).toBe(true);
    expect(context.current_goal).toBe('updated');
  });

  test('update from headers with context summary', () => {
    const context = new AgentContext({ agent_type: 'test' });
    const newContext = new AgentContext({
      agent_type: 'test',
      context_summary: 'Updated summary',
    });

    const newHeaders = newContext.toHeaders();
    const result = context.updateFromHeaders(newHeaders);

    expect(result).toBe(true);
    expect(context.context_summary).toBe('Updated summary');
  });
});
