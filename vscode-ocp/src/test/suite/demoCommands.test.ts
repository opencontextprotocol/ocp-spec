import * as assert from 'assert';
import * as vscode from 'vscode';
import { OCPDemoCommands } from '../../demoCommands';
import { OCPContextManager } from '../../contextManager';
import { OCPHttpInterceptor } from '../../httpInterceptor';

suite('OCP Demo Commands Tests', () => {
    let demoCommands: OCPDemoCommands;
    let contextManager: OCPContextManager;
    let httpInterceptor: OCPHttpInterceptor;
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
        httpInterceptor = new OCPHttpInterceptor(contextManager);
        demoCommands = new OCPDemoCommands(contextManager, httpInterceptor);
    });

    teardown(() => {
        if (contextManager) {
            contextManager.stopTracking();
        }
        if (httpInterceptor && httpInterceptor.isActive()) {
            httpInterceptor.stopIntercepting();
        }
    });

    test('should register all expected commands', () => {
        const commandsBefore = vscode.commands.getCommands();
        
        demoCommands.registerCommands(mockContext);
        
        // Check that subscriptions were added
        assert.ok(mockContext.subscriptions.length > 0);
        
        // Verify each command registration added a disposable
        const expectedCommandCount = 10; // Based on the commands in registerCommands
        assert.ok(mockContext.subscriptions.length >= expectedCommandCount);
    });

    test('should handle context status display', async () => {
        // Set up some context data
        contextManager.updateGoal('test_goal', 'test_summary');
        contextManager.addInteraction('test_action', 'test_api', 'success');
        contextManager.addRecentChange('test_change');
        
        // This would normally show a message to user
        // We can't easily test the UI interaction, but we can verify
        // the context data is properly structured
        const context = contextManager.getContext();
        const summary = contextManager.getContextSummary();
        
        assert.ok(context.context_id);
        assert.strictEqual(context.current_goal, 'test_goal');
        assert.strictEqual(context.context_summary, 'test_summary');
        assert.strictEqual(context.history.length, 1);
        assert.strictEqual(context.recent_changes.length, 1);
        assert.ok(summary.includes('test_goal'));
    });

    test('should demonstrate context memory properly', async () => {
        const initialHistoryCount = contextManager.getContext().history.length;
        
        // Simulate what demonstrateContextMemory does
        contextManager.updateGoal(
            'Demonstrate context memory',
            'Showing how OCP maintains state across interactions'
        );
        
        contextManager.addInteraction(
            'user_action',
            'vscode_command',
            'User opened context memory demo',
            { demo_step: 1 }
        );
        
        contextManager.addRecentChange('Created demo.py');
        contextManager.addRecentChange('Added function hello_world()');
        
        const context = contextManager.getContext();
        
        // Verify context memory demonstration setup
        assert.strictEqual(context.current_goal, 'Demonstrate context memory');
        assert.ok(context.context_summary?.includes('state across interactions'));
        assert.ok(context.history.length > initialHistoryCount);
        assert.ok(context.recent_changes.includes('Created demo.py'));
        assert.ok(context.recent_changes.includes('Added function hello_world()'));
    });

    test('should handle context clearing', () => {
        // Set up context with data
        contextManager.updateGoal('test_goal');
        contextManager.addInteraction('test_action', 'api', 'result');
        contextManager.addRecentChange('test_change');
        contextManager.setErrorContext('test_error');
        
        // Verify data exists
        let context = contextManager.getContext();
        assert.ok(context.history.length > 0);
        assert.ok(context.recent_changes.length > 0);
        assert.ok(context.error_context);
        assert.ok(context.session.interaction_count > 0);
        
        // Clear context
        contextManager.clearHistory();
        
        // Verify clearing worked
        context = contextManager.getContext();
        assert.strictEqual(context.history.length, 0);
        assert.strictEqual(context.recent_changes.length, 0);
        assert.strictEqual(context.error_context, undefined);
        assert.strictEqual(context.session.interaction_count, 0);
    });

    test('should generate valid context report data', () => {
        // Set up rich context for report
        contextManager.updateGoal('test_goal', 'test_summary');
        contextManager.addInteraction('action1', 'api1', 'result1');
        contextManager.addInteraction('action2', 'api2', 'result2');
        contextManager.addRecentChange('change1');
        contextManager.addRecentChange('change2');
        contextManager.addApiSpec('test_api', 'https://api.example.com');
        
        const context = contextManager.getContext();
        
        // Verify report data structure
        assert.ok(context.context_id);
        assert.ok(context.created_at);
        assert.ok(context.last_updated);
        assert.strictEqual(context.current_goal, 'test_goal');
        assert.strictEqual(context.context_summary, 'test_summary');
        assert.strictEqual(context.history.length, 2);
        assert.strictEqual(context.recent_changes.length, 2);
        assert.ok(context.api_specs['test_api']);
        
        // Verify timestamp formats
        assert.ok(!isNaN(Date.parse(context.created_at)));
        assert.ok(!isNaN(Date.parse(context.last_updated)));
        assert.ok(!isNaN(Date.parse(context.session.start_time)));
    });

    test('should handle session duration calculation', () => {
        const context = contextManager.getContext();
        const startTime = context.session.start_time;
        
        // Verify start time is valid
        assert.ok(!isNaN(Date.parse(startTime)));
        
        // Calculate duration (simplified version of what the demo does)
        const start = new Date(startTime);
        const now = new Date();
        const diffMs = now.getTime() - start.getTime();
        const diffSecs = Math.floor(diffMs / 1000);
        
        // Duration should be reasonable (less than a few seconds for test)
        assert.ok(diffSecs >= 0);
        assert.ok(diffSecs < 10); // Test should complete quickly
    });

    test('should demonstrate workflow steps', async () => {
        const initialInteractionCount = contextManager.getContext().session.interaction_count;
        
        // Simulate workflow steps
        contextManager.updateGoal('Complete OCP workflow demo');
        contextManager.addRecentChange('Demo step 1: Initialize OCP Context');
        contextManager.addRecentChange('Demo step 2: Track Workspace Changes');
        
        const context = contextManager.getContext();
        
        // Verify workflow progression
        assert.strictEqual(context.current_goal, 'Complete OCP workflow demo');
        assert.ok(context.recent_changes.some(change => change.includes('Initialize OCP Context')));
        assert.ok(context.recent_changes.some(change => change.includes('Track Workspace Changes')));
        assert.ok(context.session.interaction_count >= initialInteractionCount);
    });

    test('should handle API simulation setup', () => {
        const testUrl = 'https://api.github.com/user/repos';
        const testDescription = 'Test API call with OCP headers';
        
        // Simulate API call preparation (what simulateAPIRequest would do)
        const context = contextManager.getContext();
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        // Verify headers are generated correctly
        assert.ok(headers['X-OCP-Context-ID']);
        assert.ok(headers['X-OCP-Agent-Type']);
        assert.ok(Object.keys(headers).length > 5); // Should have multiple headers
        
        // Log the simulated request
        contextManager.addInteraction(
            'simulated_api_request',
            testUrl,
            testDescription,
            {
                method: 'GET',
                headers_count: Object.keys(headers).length,
                context_id: context.context_id
            }
        );
        
        const updatedContext = contextManager.getContext();
        const lastInteraction = updatedContext.history[updatedContext.history.length - 1];
        
        assert.strictEqual(lastInteraction.action, 'simulated_api_request');
        assert.strictEqual(lastInteraction.api_endpoint, testUrl);
        assert.strictEqual(lastInteraction.result, testDescription);
        assert.ok(lastInteraction.metadata?.headers_count);
    });

    test('should maintain context consistency across operations', () => {
        const originalContextId = contextManager.getContext().context_id;
        
        // Perform multiple operations
        contextManager.updateGoal('consistency_test');
        contextManager.addInteraction('op1', 'api1', 'result1');
        contextManager.addRecentChange('change1');
        contextManager.setErrorContext('error1');
        
        // Context ID should remain the same
        const updatedContext = contextManager.getContext();
        assert.strictEqual(updatedContext.context_id, originalContextId);
        
        // All operations should be reflected
        assert.strictEqual(updatedContext.current_goal, 'consistency_test');
        assert.ok(updatedContext.history.some(h => h.action === 'op1'));
        assert.ok(updatedContext.recent_changes.includes('change1'));
        assert.strictEqual(updatedContext.error_context, 'error1');
    });

    test('should generate comprehensive context summaries', () => {
        // Create rich context
        contextManager.updateGoal('comprehensive_test');
        contextManager.addInteraction('user_action', 'vscode', 'file_opened');
        contextManager.addInteraction('api_call', 'github', 'repos_fetched');
        contextManager.addRecentChange('modified_readme');
        contextManager.addRecentChange('added_tests');
        contextManager.setErrorContext('syntax_error', 'main.js');
        
        const summary = contextManager.getContextSummary();
        
        // Summary should include key elements
        assert.ok(summary.includes('comprehensive_test')); // Goal
        assert.ok(summary.includes('syntax_error')); // Error
        assert.ok(summary.includes('main.js')); // File
        assert.ok(summary.includes('added_tests')); // Recent change
        assert.ok(summary.includes('api_call')); // Recent action
    });
});