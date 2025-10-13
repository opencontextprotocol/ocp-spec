import * as vscode from 'vscode';
import { OCPContextManager } from './contextManager';
import { OCPHttpInterceptor } from './httpInterceptor';
import { OCPDemoCommands } from './demoCommands';

/**
 * OCP VS Code Extension - Zero-infrastructure context for AI agents
 * 
 * This extension demonstrates how OCP provides superior context management
 * compared to MCP with zero server infrastructure.
 */

let contextManager: OCPContextManager;
let httpInterceptor: OCPHttpInterceptor;
let demoCommands: OCPDemoCommands;

export function activate(context: vscode.ExtensionContext) {
    console.log('🚀 OCP Agent Context extension is activating...');

    // Initialize OCP components
    contextManager = new OCPContextManager(context);
    httpInterceptor = new OCPHttpInterceptor(contextManager);
    demoCommands = new OCPDemoCommands(contextManager, httpInterceptor);

    // Register all commands
    registerCommands(context);

    // Start context tracking
    contextManager.startTracking();

    console.log('✅ OCP Agent Context extension is active!');
    
    // Show welcome message if first time
    const hasShownWelcome = context.globalState.get('ocp.hasShownWelcome', false);
    if (!hasShownWelcome) {
        showWelcomeMessage(context);
    }
}

function registerCommands(context: vscode.ExtensionContext) {
    // Use the demoCommands class to register all commands
    demoCommands.registerCommands(context);
}

async function showWelcomeMessage(context: vscode.ExtensionContext) {
    const message = `🚀 Welcome to OCP Agent Context!
    
This extension demonstrates zero-infrastructure context sharing for AI agents.

Key features:
• Automatic workspace and file context tracking
• HTTP request enhancement with OCP headers  
• Superior alternative to MCP with zero servers
• Working demos showing OCP vs MCP

Try: "OCP: Demo: MCP vs OCP Setup" to see the difference!`;

    const selection = await vscode.window.showInformationMessage(
        'Welcome to OCP Agent Context!',
        'Show Demo',
        'Configure',
        'Dismiss'
    );

    if (selection === 'Show Demo') {
        vscode.commands.executeCommand('ocp.compareWithMCP');
    } else if (selection === 'Configure') {
        vscode.commands.executeCommand('workbench.action.openSettings', 'ocp');
    }

    context.globalState.update('ocp.hasShownWelcome', true);
}

export function deactivate() {
    console.log('🛑 OCP Agent Context extension is deactivating...');
    
    if (contextManager) {
        contextManager.stopTracking();
    }
    
    if (httpInterceptor) {
        httpInterceptor.stopIntercepting();
    }
}