import * as vscode from 'vscode';
import { OCPContextManager } from './contextManager';
import { OCPHttpInterceptor } from './httpInterceptor';

/**
 * Demo Commands for OCP Extension
 * 
 * Provides interactive demonstrations of OCP vs MCP capabilities
 */
export class OCPDemoCommands {
    private contextManager: OCPContextManager;
    private httpInterceptor: OCPHttpInterceptor;

    constructor(contextManager: OCPContextManager, httpInterceptor: OCPHttpInterceptor) {
        this.contextManager = contextManager;
        this.httpInterceptor = httpInterceptor;
    }

    /**
     * Register all demo commands with VS Code
     */
    public registerCommands(context: vscode.ExtensionContext): void {
        const commands = [
            vscode.commands.registerCommand('ocp.showContextStatus', () => this.showContextStatus()),
            vscode.commands.registerCommand('ocp.demonstrateContextMemory', () => this.demonstrateContextMemory()),
            vscode.commands.registerCommand('ocp.compareWithMCP', () => this.compareWithMCP()),
            vscode.commands.registerCommand('ocp.simulateAPICall', () => this.simulateAPICall()),
            vscode.commands.registerCommand('ocp.showSetupComparison', () => this.showSetupComparison()),
            vscode.commands.registerCommand('ocp.generateContextReport', () => this.generateContextReport()),
            vscode.commands.registerCommand('ocp.clearContext', () => this.clearContext()),
            vscode.commands.registerCommand('ocp.toggleTracking', () => this.toggleTracking()),
            vscode.commands.registerCommand('ocp.showHeaderDemo', () => this.showHeaderDemo()),
            vscode.commands.registerCommand('ocp.demoWorkflow', () => this.demoWorkflow())
        ];

        commands.forEach(disposable => context.subscriptions.push(disposable));
    }

    /**
     * Show current OCP context status
     */
    private async showContextStatus(): Promise<void> {
        const context = this.contextManager.getContext();
        const summary = this.contextManager.getContextSummary();

        const statusMessage = `
🔍 OCP Context Status

📊 Session Info:
• Context ID: ${context.context_id}
• Agent Type: ${context.agent_type}
• Interaction Count: ${context.session.interaction_count}
• Session Duration: ${this.getSessionDuration(context.session.start_time)}

🎯 Current State:
• Goal: ${context.current_goal || 'None set'}
• Workspace: ${context.workspace || 'None'}
• Current File: ${context.current_file || 'None'}
• Error Context: ${context.error_context || 'None'}

📈 Activity:
• Recent Changes: ${context.recent_changes.length}
• History Items: ${context.history.length}
• API Specs: ${Object.keys(context.api_specs).length}

📝 Summary: ${summary}
        `;

        await vscode.window.showInformationMessage(
            'OCP Context Status',
            { modal: true, detail: statusMessage }
        );
    }

    /**
     * Demonstrate OCP's context memory capabilities
     */
    private async demonstrateContextMemory(): Promise<void> {
        // Update goal to demonstrate context persistence
        this.contextManager.updateGoal(
            'Demonstrate context memory',
            'Showing how OCP maintains state across interactions'
        );

        // Add some sample interactions
        this.contextManager.addInteraction(
            'user_action',
            'vscode_command',
            'User opened context memory demo',
            { demo_step: 1 }
        );

        // Simulate file changes
        this.contextManager.addRecentChange('Created demo.py');
        this.contextManager.addRecentChange('Added function hello_world()');

        const context = this.contextManager.getContext();

        const memoryDemo = `
🧠 OCP Context Memory Demo

🎯 Goal Persistence:
Current Goal: "${context.current_goal}"
Context Summary: "${context.context_summary}"

📚 Interaction History (Last 3):
${context.history.slice(-3).map((h, i) => 
    `${i + 1}. [${new Date(h.timestamp).toLocaleTimeString()}] ${h.action}: ${h.result || 'completed'}`
).join('\n')}

🔄 Recent Activity:
${context.recent_changes.map((change, i) => `${i + 1}. ${change}`).join('\n')}

💡 Key Advantage:
Unlike MCP which requires manual context setup for each interaction,
OCP automatically maintains and evolves context throughout your session.

🔥 This means AI agents get smarter over time and understand your
workflow patterns, current objectives, and development context!
        `;

        await vscode.window.showInformationMessage(
            'OCP Context Memory Demonstration',
            { modal: true, detail: memoryDemo }
        );

        // Log this demonstration
        this.contextManager.addInteraction(
            'demo_completed',
            'context_memory',
            'Showed context memory capabilities to user'
        );
    }

    /**
     * Compare OCP vs MCP setup complexity
     */
    private async showSetupComparison(): Promise<void> {
        const comparison = `
⚡ OCP vs MCP Setup Comparison

🔥 OCP Setup (Open Context Protocol):
1. Install VS Code extension ✅
2. Done! Context flows automatically 🎉

❄️ MCP Setup (Model Context Protocol):
1. Install MCP client library
2. Configure server endpoints
3. Set up authentication tokens
4. Define custom tools and schemas
5. Implement context serialization
6. Handle server lifecycle management
7. Debug connection issues
8. Manually pass context in each request

📊 Comparison:
• OCP Steps: 2
• MCP Steps: 8+
• Setup Time: OCP (1 min) vs MCP (1+ hour)
• Maintenance: OCP (automatic) vs MCP (manual)

🎯 Why OCP Wins:
• Zero-infrastructure setup
• Automatic context discovery
• Built-in HTTP enhancement
• Works with any AI service
• No server management
• Instant context sharing

🚀 Result: 
OCP gets you productive immediately while MCP requires
significant setup and ongoing maintenance overhead!
        `;

        await vscode.window.showInformationMessage(
            'Setup Complexity: OCP vs MCP',
            { modal: true, detail: comparison }
        );
    }

    /**
     * Compare OCP vs MCP during runtime
     */
    private async compareWithMCP(): Promise<void> {
        await this.httpInterceptor.showHeaderComparison();
    }

    /**
     * Simulate API call with OCP headers
     */
    private async simulateAPICall(): Promise<void> {
        const apiOptions = [
            { label: 'GitHub API', url: 'https://api.github.com/user/repos' },
            { label: 'OpenAI API', url: 'https://api.openai.com/v1/chat/completions' },
            { label: 'Custom AI Service', url: 'https://myai.example.com/api/chat' }
        ];

        const selected = await vscode.window.showQuickPick(apiOptions, {
            placeHolder: 'Select API to simulate call with OCP headers'
        });

        if (selected) {
            await this.httpInterceptor.simulateAPIRequest(selected.url, {
                method: 'POST',
                description: `Simulated call to ${selected.label} with full OCP context`
            });
        }
    }

    /**
     * Show HTTP header demonstration
     */
    private async showHeaderDemo(): Promise<void> {
        await this.httpInterceptor.showHeaderComparison();
    }

    /**
     * Generate detailed context report
     */
    private async generateContextReport(): Promise<void> {
        const context = this.contextManager.getContext();
        
        const report = `
📋 OCP Context Report
Generated: ${new Date().toLocaleString()}

🔍 Context Overview:
• ID: ${context.context_id}
• Agent: ${context.agent_type}
• User: ${context.user}
• Created: ${new Date(context.created_at).toLocaleString()}
• Last Updated: ${new Date(context.last_updated).toLocaleString()}

🎯 Current Session:
• Start Time: ${new Date(context.session.start_time).toLocaleString()}
• Duration: ${this.getSessionDuration(context.session.start_time)}
• Interactions: ${context.session.interaction_count}
• Goal: ${context.current_goal || 'Not set'}

📁 Workspace Context:
• Workspace: ${context.workspace || 'None'}
• Current File: ${context.current_file || 'None'}
• Error Context: ${context.error_context || 'None'}

🔄 Recent Activity:
${context.recent_changes.length > 0 ? 
    context.recent_changes.map((change, i) => `${i + 1}. ${change}`).join('\n') : 
    'No recent changes'
}

📚 Interaction History:
${context.history.length > 0 ? 
    context.history.slice(-5).map((h, i) => 
        `${i + 1}. [${new Date(h.timestamp).toLocaleTimeString()}] ${h.action}${h.api_endpoint ? ` -> ${h.api_endpoint}` : ''}: ${h.result || 'completed'}`
    ).join('\n') : 
    'No interactions yet'
}

🌐 API Specifications:
${Object.entries(context.api_specs).map(([name, url]) => `• ${name}: ${url}`).join('\n')}

📊 Context Summary:
${this.contextManager.getContextSummary()}
        `;

        // Create a new document with the report
        const doc = await vscode.workspace.openTextDocument({
            content: report,
            language: 'markdown'
        });
        
        await vscode.window.showTextDocument(doc);
        
        this.contextManager.addInteraction(
            'report_generated',
            'vscode_command',
            'Generated detailed context report'
        );
    }

    /**
     * Clear context history
     */
    private async clearContext(): Promise<void> {
        const confirm = await vscode.window.showWarningMessage(
            'Clear OCP context history?',
            { modal: true },
            'Clear',
            'Cancel'
        );

        if (confirm === 'Clear') {
            this.contextManager.clearHistory();
            vscode.window.showInformationMessage('🗑️ OCP context history cleared');
        }
    }

    /**
     * Toggle context tracking
     */
    private async toggleTracking(): Promise<void> {
        // This is a simplified toggle - the actual implementation would check current state
        vscode.window.showInformationMessage(
            '🔄 Context tracking toggled (feature in development)'
        );
    }

    /**
     * Run complete OCP workflow demonstration
     */
    private async demoWorkflow(): Promise<void> {
        const steps = [
            'Initialize OCP Context',
            'Track Workspace Changes',
            'Demonstrate Context Memory',
            'Show API Integration',
            'Compare with MCP'
        ];

        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            
            await vscode.window.showInformationMessage(
                `🚀 OCP Demo Workflow - Step ${i + 1}/${steps.length}`,
                { detail: step }
            );

            // Simulate workflow steps
            switch (i) {
                case 0:
                    this.contextManager.updateGoal('Complete OCP workflow demo');
                    break;
                case 1:
                    this.contextManager.addRecentChange(`Demo step ${i + 1}: ${step}`);
                    break;
                case 2:
                    await this.demonstrateContextMemory();
                    continue; // Skip the generic delay
                case 3:
                    await this.simulateAPICall();
                    continue; // Skip the generic delay
                case 4:
                    await this.compareWithMCP();
                    continue; // Skip the generic delay
            }

            // Small delay between steps
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        vscode.window.showInformationMessage(
            '🎉 OCP Workflow Demo Complete!',
            { detail: 'You\'ve seen how OCP provides seamless context management with zero setup overhead.' }
        );
    }

    /**
     * Helper to calculate session duration
     */
    private getSessionDuration(startTime: string): string {
        const start = new Date(startTime);
        const now = new Date();
        const diffMs = now.getTime() - start.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffSecs = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        if (diffMins > 0) {
            return `${diffMins}m ${diffSecs}s`;
        } else {
            return `${diffSecs}s`;
        }
    }
}