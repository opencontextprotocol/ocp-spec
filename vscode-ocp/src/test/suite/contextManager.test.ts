import * as assert from 'assert';
import * as vscode from 'vscode';
import { OCPContextManager, OCPContext } from '../../contextManager';

suite('OCP Context Manager Tests', () => {
    let contextManager: OCPContextManager;
    let mockContext: vscode.ExtensionContext;

    setup(() => {
        // Create a simplified mock extension context for testing
        mockContext = {
            subscriptions: [],
            workspaceState: {
                get: () => undefined,
                update: () => Promise.resolve(),
                keys: () => []
            },
            globalState: {
                get: () => undefined,
                update: () => Promise.resolve(),
                setKeysForSync: () => {},
                keys: () => []
            },
            extensionUri: vscode.Uri.file('/mock/path'),
            extensionPath: '/mock/path'
        } as any; // Use 'any' to bypass the complete interface requirement for testing

        contextManager = new OCPContextManager(mockContext);
    });

    teardown(() => {
        if (contextManager) {
            contextManager.stopTracking();
        }
    });

    test('should create initial context with correct structure', () => {
        const context = contextManager.getContext();
        
        assert.ok(context.context_id);
        assert.ok(context.context_id.startsWith('ocp-'));
        assert.strictEqual(context.agent_type, 'ide_copilot');
        assert.ok(context.session);
        assert.ok(context.session.start_time);
        assert.strictEqual(context.session.interaction_count, 0);
        assert.ok(Array.isArray(context.history));
        assert.ok(Array.isArray(context.recent_changes));
        assert.ok(context.api_specs);
        assert.ok(context.created_at);
        assert.ok(context.last_updated);
    });

    test('should update goal and increment interaction count', () => {
        const goal = 'test_goal';
        const summary = 'test_summary';
        
        contextManager.updateGoal(goal, summary);
        
        const context = contextManager.getContext();
        assert.strictEqual(context.current_goal, goal);
        assert.strictEqual(context.context_summary, summary);
        assert.strictEqual(context.session.interaction_count, 1);
    });

    test('should add interactions to history', () => {
        const action = 'test_action';
        const apiEndpoint = 'https://api.example.com';
        const result = 'test_result';
        const metadata = { test: 'data' };
        
        contextManager.addInteraction(action, apiEndpoint, result, metadata);
        
        const context = contextManager.getContext();
        assert.strictEqual(context.history.length, 1);
        
        const interaction = context.history[0];
        assert.strictEqual(interaction.action, action);
        assert.strictEqual(interaction.api_endpoint, apiEndpoint);
        assert.strictEqual(interaction.result, result);
        assert.deepStrictEqual(interaction.metadata, metadata);
        assert.ok(interaction.timestamp);
    });

    test('should set and track error context', () => {
        const error = 'test_error';
        const filePath = 'test.js';
        
        contextManager.setErrorContext(error, filePath);
        
        const context = contextManager.getContext();
        assert.strictEqual(context.error_context, error);
        assert.strictEqual(context.current_file, filePath);
    });

    test('should manage recent changes with limit', () => {
        // Add 12 changes (more than the 10 limit)
        for (let i = 1; i <= 12; i++) {
            contextManager.addRecentChange(`change_${i}`);
        }
        
        const context = contextManager.getContext();
        
        // Should only keep last 10 changes
        assert.strictEqual(context.recent_changes.length, 10);
        assert.strictEqual(context.recent_changes[0], 'change_3'); // First kept change
        assert.strictEqual(context.recent_changes[9], 'change_12'); // Last change
    });

    test('should add API specifications', () => {
        const apiName = 'test_api';
        const specUrl = 'https://api.example.com/spec';
        
        contextManager.addApiSpec(apiName, specUrl);
        
        const context = contextManager.getContext();
        assert.strictEqual(context.api_specs[apiName], specUrl);
    });

    test('should generate context summary', () => {
        contextManager.updateGoal('test_goal');
        contextManager.setErrorContext('test_error');
        contextManager.addRecentChange('test_change');
        contextManager.addInteraction('test_action', 'api', 'result');
        
        const summary = contextManager.getContextSummary();
        
        assert.ok(summary.includes('test_goal'));
        assert.ok(summary.includes('test_error'));
        assert.ok(summary.includes('test_change'));
        assert.ok(summary.includes('test_action'));
    });

    test('should clear history and reset counters', () => {
        // Add some data
        contextManager.updateGoal('test_goal');
        contextManager.addInteraction('test_action', 'api', 'result');
        contextManager.addRecentChange('test_change');
        contextManager.setErrorContext('test_error');
        
        // Clear history
        contextManager.clearHistory();
        
        const context = contextManager.getContext();
        assert.strictEqual(context.history.length, 0);
        assert.strictEqual(context.recent_changes.length, 0);
        assert.strictEqual(context.error_context, undefined);
        assert.strictEqual(context.session.interaction_count, 0);
    });

    test('should clone context with new ID', () => {
        contextManager.updateGoal('test_goal');
        contextManager.addInteraction('test_action', 'api', 'result');
        
        const originalContext = contextManager.getContext();
        const clonedContext = contextManager.clone();
        
        // Should have different IDs
        assert.notStrictEqual(clonedContext.context_id, originalContext.context_id);
        
        // Should have same data otherwise
        assert.strictEqual(clonedContext.current_goal, originalContext.current_goal);
        assert.strictEqual(clonedContext.history.length, originalContext.history.length);
    });

    test('should return immutable context copy', () => {
        const context1 = contextManager.getContext();
        const context2 = contextManager.getContext();
        
        // Should be different object instances
        assert.notStrictEqual(context1, context2);
        
        // But with same data
        assert.strictEqual(context1.context_id, context2.context_id);
        
        // Modifying returned context should not affect internal state
        context1.current_goal = 'modified_goal';
        const context3 = contextManager.getContext();
        assert.notStrictEqual(context3.current_goal, 'modified_goal');
    });

    test('should update timestamps on modifications', () => {
        const initialContext = contextManager.getContext();
        const initialTimestamp = initialContext.last_updated;
        
        // Wait a bit to ensure timestamp difference
        setTimeout(() => {
            contextManager.updateGoal('new_goal');
            
            const updatedContext = contextManager.getContext();
            assert.notStrictEqual(updatedContext.last_updated, initialTimestamp);
        }, 10);
    });
});