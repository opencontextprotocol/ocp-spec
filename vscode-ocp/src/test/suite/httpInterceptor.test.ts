import * as assert from 'assert';
import * as vscode from 'vscode';
import { OCPHttpInterceptor } from '../../httpInterceptor';
import { OCPContextManager, OCPContext } from '../../contextManager';

suite('OCP HTTP Interceptor Tests', () => {
    let httpInterceptor: OCPHttpInterceptor;
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
        httpInterceptor = new OCPHttpInterceptor(contextManager);
    });

    teardown(() => {
        if (httpInterceptor && httpInterceptor.isActive()) {
            httpInterceptor.stopIntercepting();
        }
    });

    test('should generate OCP headers from context', () => {
        // Set up context
        contextManager.updateGoal('test_goal');
        contextManager.addRecentChange('test_change_1');
        contextManager.addRecentChange('test_change_2');
        contextManager.setErrorContext('test_error');
        
        const context = contextManager.getContext();
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        // Check core headers
        assert.ok(headers['X-OCP-Context-ID']);
        assert.strictEqual(headers['X-OCP-Agent-Type'], 'ide_copilot');
        assert.ok(headers['X-OCP-Session-ID']);
        
        // Check context headers
        assert.strictEqual(headers['X-OCP-Goal'], 'test_goal');
        assert.strictEqual(headers['X-OCP-Error-Context'], 'test_error');
        assert.ok(headers['X-OCP-Recent-Changes'].includes('test_change_1'));
        assert.ok(headers['X-OCP-Recent-Changes'].includes('test_change_2'));
        
        // Check session metrics
        assert.ok(headers['X-OCP-Interaction-Count']);
        assert.ok(headers['X-OCP-Session-Duration']);
        assert.ok(headers['X-OCP-Context-Summary']);
    });

    test('should handle optional context fields gracefully', () => {
        const context = contextManager.getContext();
        
        // Clear optional fields
        context.user = undefined;
        context.workspace = undefined;
        context.current_file = undefined;
        context.current_goal = undefined;
        context.error_context = undefined;
        context.recent_changes = [];
        
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        // Core headers should still exist
        assert.ok(headers['X-OCP-Context-ID']);
        assert.ok(headers['X-OCP-Agent-Type']);
        assert.ok(headers['X-OCP-Session-ID']);
        
        // Optional headers should not exist
        assert.strictEqual(headers['X-OCP-User'], undefined);
        assert.strictEqual(headers['X-OCP-Workspace'], undefined);
        assert.strictEqual(headers['X-OCP-Current-File'], undefined);
        assert.strictEqual(headers['X-OCP-Goal'], undefined);
        assert.strictEqual(headers['X-OCP-Error-Context'], undefined);
        assert.strictEqual(headers['X-OCP-Recent-Changes'], undefined);
    });

    test('should limit recent changes to last 3', () => {
        // Add 5 recent changes
        for (let i = 1; i <= 5; i++) {
            contextManager.addRecentChange(`change_${i}`);
        }
        
        const context = contextManager.getContext();
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        const recentChanges = headers['X-OCP-Recent-Changes'];
        const changes = recentChanges.split(';');
        
        // Should only include last 3 changes
        assert.strictEqual(changes.length, 3);
        assert.ok(changes.includes('change_3'));
        assert.ok(changes.includes('change_4'));
        assert.ok(changes.includes('change_5'));
    });

    test('should start and stop intercepting correctly', () => {
        assert.strictEqual(httpInterceptor.isActive(), false);
        
        httpInterceptor.startIntercepting();
        assert.strictEqual(httpInterceptor.isActive(), true);
        
        httpInterceptor.stopIntercepting();
        assert.strictEqual(httpInterceptor.isActive(), false);
    });

    test('should not start intercepting twice', () => {
        httpInterceptor.startIntercepting();
        const firstState = httpInterceptor.isActive();
        
        // Try to start again
        httpInterceptor.startIntercepting();
        const secondState = httpInterceptor.isActive();
        
        assert.strictEqual(firstState, true);
        assert.strictEqual(secondState, true);
        // Should not throw or cause issues
    });

    test('should not stop intercepting twice', () => {
        httpInterceptor.startIntercepting();
        httpInterceptor.stopIntercepting();
        const firstState = httpInterceptor.isActive();
        
        // Try to stop again
        httpInterceptor.stopIntercepting();
        const secondState = httpInterceptor.isActive();
        
        assert.strictEqual(firstState, false);
        assert.strictEqual(secondState, false);
        // Should not throw or cause issues
    });

    test('should calculate session duration correctly', () => {
        const context = contextManager.getContext();
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        const duration = headers['X-OCP-Session-Duration'];
        assert.ok(duration);
        assert.ok(duration.endsWith('m')); // Should end with 'm' for minutes
        
        const minutes = parseInt(duration.replace('m', ''));
        assert.ok(minutes >= 0);
    });

    test('should create context summary with key information', () => {
        // Set up rich context
        contextManager.updateGoal('implement_feature');
        contextManager.addRecentChange('added_function');
        contextManager.addRecentChange('fixed_bug');
        contextManager.setErrorContext('syntax_error', 'test.js');
        contextManager.addInteraction('code_edit', 'vscode', 'completed');
        
        const context = contextManager.getContext();
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        const summary = headers['X-OCP-Context-Summary'];
        assert.ok(summary);
        
        // Should contain key context indicators
        assert.ok(summary.includes('file:'));
        assert.ok(summary.includes('error:'));
        assert.ok(summary.includes('changes:'));
        assert.ok(summary.includes('last:'));
    });

    test('should handle context with no activity', () => {
        const context = contextManager.getContext();
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        const summary = headers['X-OCP-Context-Summary'];
        assert.ok(summary);
        // Summary should still be generated even with minimal context
        assert.ok(typeof summary === 'string');
    });

    test('should generate unique session IDs', () => {
        const context1 = contextManager.getContext();
        const headers1 = OCPHttpInterceptor.generateOCPHeaders(context1);
        
        // Increment interaction count
        contextManager.updateGoal('new_goal');
        
        const context2 = contextManager.getContext();
        const headers2 = OCPHttpInterceptor.generateOCPHeaders(context2);
        
        // Session IDs should be different due to interaction count change
        assert.notStrictEqual(headers1['X-OCP-Session-ID'], headers2['X-OCP-Session-ID']);
    });

    test('should include all expected header names', () => {
        const context = contextManager.getContext();
        
        // Set up full context
        context.user = 'test_user';
        context.workspace = 'test_workspace';
        context.current_file = 'test.js';
        context.current_goal = 'test_goal';
        context.error_context = 'test_error';
        context.recent_changes = ['change1', 'change2'];
        
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);
        
        const expectedHeaders = [
            'X-OCP-Context-ID',
            'X-OCP-Agent-Type',
            'X-OCP-Session-ID',
            'X-OCP-User',
            'X-OCP-Workspace',
            'X-OCP-Current-File',
            'X-OCP-Goal',
            'X-OCP-Error-Context',
            'X-OCP-Recent-Changes',
            'X-OCP-Interaction-Count',
            'X-OCP-Session-Duration',
            'X-OCP-Context-Summary'
        ];
        
        expectedHeaders.forEach(headerName => {
            assert.ok(headers[headerName] !== undefined, `Missing header: ${headerName}`);
        });
    });
});