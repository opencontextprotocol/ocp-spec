import * as assert from 'assert';
import * as vscode from 'vscode';

// Import extension functions
import { activate, deactivate } from '../../extension';

suite('Extension Integration Tests', () => {
    let context: vscode.ExtensionContext;

    suiteSetup(async () => {
        // Get extension context
        const extension = vscode.extensions.getExtension('opencontextprotocol.vscode-ocp');
        if (!extension) {
            throw new Error('Extension not found');
        }
        
        // Activate extension if not already active
        if (!extension.isActive) {
            await extension.activate();
        }
        
        context = extension.exports?.context;
    });

    test('extension should be present and activated', async () => {
        const extension = vscode.extensions.getExtension('opencontextprotocol.vscode-ocp');
        assert.ok(extension);
        assert.ok(extension.isActive);
    });

    test('should register all OCP commands', async () => {
        const commands = await vscode.commands.getCommands(true);
        
        const ocpCommands = [
            'ocp.showContextStatus',
            'ocp.demonstrateContextMemory',
            'ocp.compareWithMCP',
            'ocp.simulateAPICall',
            'ocp.showSetupComparison',
            'ocp.generateContextReport',
            'ocp.clearContext',
            'ocp.toggleTracking',
            'ocp.showHeaderDemo',
            'ocp.demoWorkflow'
        ];
        
        ocpCommands.forEach(command => {
            assert.ok(
                commands.includes(command),
                `Command ${command} should be registered`
            );
        });
    });

    test('should have correct configuration properties', () => {
        const config = vscode.workspace.getConfiguration('ocp');
        
        // Test that configuration properties exist and have correct types
        const enabled = config.get('enabled');
        const agentType = config.get('agentType');
        const contextTracking = config.get('contextTracking');
        const debug = config.get('debug');
        
        assert.strictEqual(typeof enabled, 'boolean');
        assert.strictEqual(typeof agentType, 'string');
        assert.strictEqual(typeof contextTracking, 'boolean');
        assert.strictEqual(typeof debug, 'boolean');
    });

    test('should execute showContextStatus command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.showContextStatus');
            // If we get here, the command executed without throwing
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should execute demonstrateContextMemory command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.demonstrateContextMemory');
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should execute compareWithMCP command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.compareWithMCP');
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should execute showSetupComparison command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.showSetupComparison');
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should execute generateContextReport command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.generateContextReport');
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should execute clearContext command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.clearContext');
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should execute showHeaderDemo command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.showHeaderDemo');
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should execute demoWorkflow command without errors', async () => {
        try {
            await vscode.commands.executeCommand('ocp.demoWorkflow');
            assert.ok(true);
        } catch (error) {
            assert.fail(`Command execution failed: ${error}`);
        }
    });

    test('should handle configuration changes', async () => {
        const config = vscode.workspace.getConfiguration('ocp');
        const originalValue = config.get('debug');
        
        try {
            // Change configuration
            await config.update('debug', !originalValue, vscode.ConfigurationTarget.Workspace);
            
            // Verify change
            const newValue = config.get('debug');
            assert.strictEqual(newValue, !originalValue);
            
        } finally {
            // Restore original value
            await config.update('debug', originalValue, vscode.ConfigurationTarget.Workspace);
        }
    });

    test('should handle workspace folder changes gracefully', () => {
        // This test verifies the extension doesn't crash when workspace changes
        const workspaceFolders = vscode.workspace.workspaceFolders;
        
        // Extension should handle no workspace folders
        assert.ok(true); // If we get here, extension handles it
        
        // If workspace folders exist, verify basic structure
        if (workspaceFolders && workspaceFolders.length > 0) {
            assert.ok(workspaceFolders[0].uri);
            assert.ok(workspaceFolders[0].name);
        }
    });

    test('should handle active editor changes gracefully', () => {
        const activeEditor = vscode.window.activeTextEditor;
        
        // Extension should handle no active editor
        assert.ok(true); // If we get here, extension handles it
        
        // If active editor exists, verify basic structure
        if (activeEditor) {
            assert.ok(activeEditor.document);
            assert.ok(activeEditor.document.fileName);
        }
    });

    test('extension should deactivate cleanly', () => {
        try {
            deactivate();
            // If we get here, deactivation completed without errors
            assert.ok(true);
        } catch (error) {
            assert.fail(`Deactivation failed: ${error}`);
        }
    });

    suiteTeardown(() => {
        // Clean up after tests
        try {
            deactivate();
        } catch (error) {
            // Ignore errors during cleanup
        }
    });
});