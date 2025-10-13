import * as vscode from 'vscode';

/**
 * OCP Context interface matching our Python library structure
 */
export interface OCPContext {
    context_id: string;
    agent_type: string;
    user?: string;
    workspace?: string;
    current_file?: string;
    session: {
        start_time: string;
        interaction_count: number;
        agent_type: string;
        [key: string]: any;
    };
    history: Array<{
        timestamp: string;
        action: string;
        api_endpoint?: string;
        result?: string;
        metadata?: { [key: string]: any };
    }>;
    current_goal?: string;
    context_summary?: string;
    error_context?: string;
    recent_changes: string[];
    api_specs: { [key: string]: string };
    created_at: string;
    last_updated: string;
}

/**
 * OCP Context Manager for VS Code
 * 
 * Automatically tracks workspace state, file changes, and user context
 * to provide intelligent context for AI agent interactions.
 */
export class OCPContextManager {
    private context: OCPContext;
    private disposables: vscode.Disposable[] = [];
    private extensionContext: vscode.ExtensionContext;
    private isTracking = false;

    constructor(extensionContext: vscode.ExtensionContext) {
        this.extensionContext = extensionContext;
        this.context = this.createInitialContext();
    }

    private createInitialContext(): OCPContext {
        const config = vscode.workspace.getConfiguration('ocp');
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const activeEditor = vscode.window.activeTextEditor;

        return {
            context_id: `ocp-${this.generateId()}`,
            agent_type: config.get('agentType', 'ide_copilot'),
            user: process.env.USER || process.env.USERNAME || 'vscode-user',
            workspace: workspaceFolder?.name,
            current_file: activeEditor?.document.fileName.split('/').pop(),
            session: {
                start_time: new Date().toISOString(),
                interaction_count: 0,
                agent_type: config.get('agentType', 'ide_copilot'),
                vscode_version: vscode.version,
                extension_version: '0.1.0'
            },
            history: [],
            current_goal: 'assist_with_coding',
            recent_changes: [],
            api_specs: {
                github: 'https://docs.github.com/en/rest'
            },
            created_at: new Date().toISOString(),
            last_updated: new Date().toISOString()
        };
    }

    private generateId(): string {
        return Math.random().toString(36).substring(2, 10);
    }

    public startTracking(): void {
        if (this.isTracking) {
            return;
        }

        this.isTracking = true;
        
        // Track file changes
        this.disposables.push(
            vscode.window.onDidChangeActiveTextEditor(editor => {
                if (editor) {
                    this.updateCurrentFile(editor.document.fileName);
                }
            })
        );

        // Track workspace changes
        this.disposables.push(
            vscode.workspace.onDidChangeWorkspaceFolders(event => {
                this.updateWorkspace();
            })
        );

        // Track configuration changes
        this.disposables.push(
            vscode.workspace.onDidChangeConfiguration(event => {
                if (event.affectsConfiguration('ocp')) {
                    this.updateFromConfiguration();
                }
            })
        );

        // Track document changes (for recent changes)
        this.disposables.push(
            vscode.workspace.onDidSaveTextDocument(document => {
                this.addRecentChange(`Saved ${document.fileName.split('/').pop()}`);
            })
        );

        // Track errors from problems
        this.disposables.push(
            vscode.languages.onDidChangeDiagnostics(event => {
                for (const uri of event.uris) {
                    const diagnostics = vscode.languages.getDiagnostics(uri);
                    const errors = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error);
                    if (errors.length > 0) {
                        this.setErrorContext(
                            `${errors.length} error(s) in ${uri.path.split('/').pop()}`,
                            uri.path.split('/').pop()
                        );
                    }
                }
            })
        );

        console.log('🔍 OCP context tracking started');
    }

    public stopTracking(): void {
        this.isTracking = false;
        this.disposables.forEach(d => d.dispose());
        this.disposables = [];
        console.log('⏹️ OCP context tracking stopped');
    }

    private updateCurrentFile(filePath: string): void {
        const fileName = filePath.split('/').pop();
        this.context.current_file = fileName;
        this.context.last_updated = new Date().toISOString();
        
        this.addInteraction(
            'file_changed',
            'vscode_event',
            `Switched to ${fileName}`,
            { file_path: filePath }
        );

        console.log(`📄 Current file: ${fileName}`);
    }

    private updateWorkspace(): void {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        this.context.workspace = workspaceFolder?.name;
        this.context.last_updated = new Date().toISOString();
        
        this.addInteraction(
            'workspace_changed',
            'vscode_event',
            `Workspace: ${workspaceFolder?.name}`,
            { workspace_path: workspaceFolder?.uri.fsPath }
        );

        console.log(`📁 Workspace: ${workspaceFolder?.name}`);
    }

    private updateFromConfiguration(): void {
        const config = vscode.workspace.getConfiguration('ocp');
        this.context.agent_type = config.get('agentType', 'ide_copilot');
        this.context.last_updated = new Date().toISOString();
        
        console.log(`⚙️ Configuration updated: ${this.context.agent_type}`);
    }

    public updateGoal(goal: string, summary?: string): void {
        this.context.current_goal = goal;
        if (summary) {
            this.context.context_summary = summary;
        }
        this.context.session.interaction_count++;
        this.context.last_updated = new Date().toISOString();
        
        console.log(`🎯 Goal updated: ${goal}`);
    }

    public addInteraction(
        action: string, 
        apiEndpoint?: string, 
        result?: string, 
        metadata?: { [key: string]: any }
    ): void {
        this.context.history.push({
            timestamp: new Date().toISOString(),
            action,
            api_endpoint: apiEndpoint,
            result,
            metadata: metadata || {}
        });
        
        this.context.last_updated = new Date().toISOString();
        
        if (this.isDebugEnabled()) {
            console.log(`📝 Interaction: ${action} -> ${result || 'completed'}`);
        }
    }

    public setErrorContext(error: string, filePath?: string): void {
        this.context.error_context = error;
        if (filePath) {
            this.context.current_file = filePath;
        }
        this.context.last_updated = new Date().toISOString();
        
        console.log(`❌ Error context: ${error}`);
    }

    public addRecentChange(change: string): void {
        this.context.recent_changes.push(change);
        
        // Keep only last 10 changes
        if (this.context.recent_changes.length > 10) {
            this.context.recent_changes = this.context.recent_changes.slice(-10);
        }
        
        this.context.last_updated = new Date().toISOString();
        
        if (this.isDebugEnabled()) {
            console.log(`🔄 Recent change: ${change}`);
        }
    }

    public addApiSpec(apiName: string, specUrl: string): void {
        this.context.api_specs[apiName] = specUrl;
        this.context.last_updated = new Date().toISOString();
    }

    public getContext(): OCPContext {
        return { ...this.context }; // Return copy to prevent mutation
    }

    public getContextSummary(): string {
        const parts: string[] = [];
        
        if (this.context.current_goal) {
            parts.push(`Goal: ${this.context.current_goal}`);
        }
        
        if (this.context.error_context) {
            parts.push(`Error: ${this.context.error_context}`);
        }
        
        if (this.context.current_file) {
            parts.push(`Working on: ${this.context.current_file}`);
        }
        
        if (this.context.recent_changes.length > 0) {
            parts.push(`Recent changes: ${this.context.recent_changes.slice(-3).join(', ')}`);
        }
        
        if (this.context.history.length > 0) {
            const recentActions = this.context.history.slice(-3).map(h => h.action);
            parts.push(`Recent actions: ${recentActions.join(', ')}`);
        }
        
        return parts.length > 0 ? parts.join(' | ') : 'New VS Code session';
    }

    public clearHistory(): void {
        this.context.history = [];
        this.context.recent_changes = [];
        this.context.error_context = undefined;
        this.context.session.interaction_count = 0;
        this.context.last_updated = new Date().toISOString();
        
        console.log('🗑️ Context history cleared');
    }

    public clone(): OCPContext {
        const cloned = { ...this.context };
        cloned.context_id = `ocp-${this.generateId()}`;
        return cloned;
    }

    private isDebugEnabled(): boolean {
        const config = vscode.workspace.getConfiguration('ocp');
        return config.get('debug', false);
    }

    private isEnabled(): boolean {
        const config = vscode.workspace.getConfiguration('ocp');
        return config.get('enabled', true);
    }
}