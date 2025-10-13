import * as vscode from 'vscode';
import { OCPContextManager, OCPContext } from './contextManager';

/**
 * HTTP Interceptor for OCP
 * 
 * Demonstrates how OCP headers can be automatically added to outgoing requests
 * to provide context to AI agents and API services.
 */
export class OCPHttpInterceptor {
    private contextManager: OCPContextManager;
    private originalFetch?: typeof fetch;
    private isIntercepting = false;

    constructor(contextManager: OCPContextManager) {
        this.contextManager = contextManager;
    }

    public startIntercepting(): void {
        if (this.isIntercepting) {
            return;
        }

        this.isIntercepting = true;
        
        // Store original fetch if available
        if (typeof globalThis.fetch !== 'undefined') {
            this.originalFetch = globalThis.fetch;
            globalThis.fetch = this.createInterceptedFetch();
        }

        vscode.window.showInformationMessage(
            '🔍 OCP HTTP interceptor started - requests will include context headers'
        );
    }

    public stopIntercepting(): void {
        if (!this.isIntercepting) {
            return;
        }

        this.isIntercepting = false;

        // Restore original fetch
        if (this.originalFetch && typeof globalThis.fetch !== 'undefined') {
            globalThis.fetch = this.originalFetch;
        }

        vscode.window.showInformationMessage(
            '⏹️ OCP HTTP interceptor stopped'
        );
    }

    private createInterceptedFetch(): typeof fetch {
        const originalFetch = this.originalFetch!;
        const contextManager = this.contextManager;

        return async function(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
            // Create enhanced request with OCP headers
            const enhancedInit = { ...init };
            enhancedInit.headers = {
                ...enhancedInit.headers,
                ...OCPHttpInterceptor.generateOCPHeaders(contextManager.getContext())
            };

            // Log the request for demonstration
            const url = typeof input === 'string' ? input : input.toString();
            contextManager.addInteraction(
                'http_request',
                url,
                'Request enhanced with OCP headers',
                {
                    method: enhancedInit.method || 'GET',
                    has_ocp_headers: true,
                    url: url
                }
            );

            // Make the actual request
            try {
                const response = await originalFetch(input, enhancedInit);
                
                contextManager.addInteraction(
                    'http_response',
                    url,
                    `${response.status} ${response.statusText}`,
                    {
                        status: response.status,
                        status_text: response.statusText,
                        success: response.ok
                    }
                );

                return response;
            } catch (error) {
                contextManager.addInteraction(
                    'http_error',
                    url,
                    `Request failed: ${error}`,
                    {
                        error: error instanceof Error ? error.message : String(error)
                    }
                );
                throw error;
            }
        };
    }

    /**
     * Generate OCP headers from context
     */
    public static generateOCPHeaders(context: OCPContext): Record<string, string> {
        const headers: Record<string, string> = {};

        // Core OCP headers
        headers['X-OCP-Context-ID'] = context.context_id;
        headers['X-OCP-Agent-Type'] = context.agent_type;
        headers['X-OCP-Session-ID'] = `${context.session.start_time}-${context.session.interaction_count}`;

        // Context information
        if (context.user) {
            headers['X-OCP-User'] = context.user;
        }

        if (context.workspace) {
            headers['X-OCP-Workspace'] = context.workspace;
        }

        if (context.current_file) {
            headers['X-OCP-Current-File'] = context.current_file;
        }

        if (context.current_goal) {
            headers['X-OCP-Goal'] = context.current_goal;
        }

        // Error context for debugging
        if (context.error_context) {
            headers['X-OCP-Error-Context'] = context.error_context;
        }

        // Recent activity summary
        if (context.recent_changes.length > 0) {
            headers['X-OCP-Recent-Changes'] = context.recent_changes.slice(-3).join(';');
        }

        // Session metrics
        headers['X-OCP-Interaction-Count'] = context.session.interaction_count.toString();
        headers['X-OCP-Session-Duration'] = OCPHttpInterceptor.getSessionDuration(context.session.start_time);

        // Context summary for quick understanding
        headers['X-OCP-Context-Summary'] = OCPHttpInterceptor.createContextSummary(context);

        return headers;
    }

    private static getSessionDuration(startTime: string): string {
        const start = new Date(startTime);
        const now = new Date();
        const diffMs = now.getTime() - start.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));
        return `${diffMins}m`;
    }

    private static createContextSummary(context: OCPContext): string {
        const parts: string[] = [];

        if (context.current_file) {
            parts.push(`file:${context.current_file}`);
        }

        if (context.error_context) {
            parts.push(`error:${context.error_context.substring(0, 30)}`);
        }

        if (context.recent_changes.length > 0) {
            parts.push(`changes:${context.recent_changes.length}`);
        }

        if (context.history.length > 0) {
            const lastAction = context.history[context.history.length - 1];
            parts.push(`last:${lastAction.action}`);
        }

        return parts.join('|');
    }

    /**
     * Simulate making an API request with OCP headers
     */
    public async simulateAPIRequest(url: string, options: {
        method?: string;
        body?: any;
        description?: string;
    } = {}): Promise<void> {
        const context = this.contextManager.getContext();
        const headers = OCPHttpInterceptor.generateOCPHeaders(context);

        // Show the headers that would be sent
        const headerDisplay = Object.entries(headers)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n');

        await vscode.window.showInformationMessage(
            `🌐 Simulated API Request to ${url}`,
            { modal: true, detail: `Headers that would be sent:\n\n${headerDisplay}` }
        );

        // Log the simulated request
        this.contextManager.addInteraction(
            'simulated_api_request',
            url,
            options.description || 'API request with OCP headers',
            {
                method: options.method || 'GET',
                headers_count: Object.keys(headers).length,
                context_id: context.context_id
            }
        );
    }

    /**
     * Demo function to show OCP vs MCP header comparison
     */
    public async showHeaderComparison(): Promise<void> {
        const context = this.contextManager.getContext();
        const ocpHeaders = OCPHttpInterceptor.generateOCPHeaders(context);

        // Mock MCP headers (minimal context)
        const mcpHeaders = {
            'Authorization': 'Bearer <token>',
            'Content-Type': 'application/json',
            'User-Agent': 'MCP-Client/1.0'
        };

        const comparison = `
🔥 OCP Headers (Rich Context):
${Object.entries(ocpHeaders).map(([k, v]) => `  ${k}: ${v}`).join('\n')}

❄️ MCP Headers (Minimal Context):
${Object.entries(mcpHeaders).map(([k, v]) => `  ${k}: ${v}`).join('\n')}

📊 Comparison:
• OCP Headers: ${Object.keys(ocpHeaders).length}
• MCP Headers: ${Object.keys(mcpHeaders).length}
• Context Advantage: ${Object.keys(ocpHeaders).length - Object.keys(mcpHeaders).length}x more context!

🎯 OCP provides automatic context about:
- Current workspace and file
- User goals and recent activity
- Error states and debugging info
- Session continuity and metrics
        `;

        await vscode.window.showInformationMessage(
            'OCP vs MCP Header Comparison',
            { modal: true, detail: comparison }
        );
    }

    public isActive(): boolean {
        return this.isIntercepting;
    }
}