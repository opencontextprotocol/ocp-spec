/**
 * OCP Agent - Context-Aware API Discovery and Execution
 * 
 * Combines OCP's context management with automatic API discovery,
 * providing intelligent API interactions with zero infrastructure.
 */

import { AgentContext } from './context.js';
import { OCPSchemaDiscovery, OCPAPISpec, OCPTool } from './schema_discovery.js';
import { OCPHTTPClient, OCPResponse } from './http_client.js';
import { OCPRegistry } from './registry.js';
import { OCPStorage } from './storage.js';

/**
 * OCP Agent for Context-Aware API Interactions
 * 
 * Provides:
 * 1. API Discovery (from OpenAPI specs or community registry)
 * 2. Tool Invocation (with parameter validation)
 * 3. Context Management (persistent across calls)
 * 4. Zero Infrastructure (no servers required)
 */
export class OCPAgent {
    context: AgentContext;
    discovery: OCPSchemaDiscovery;
    registry: OCPRegistry;
    knownApis: Map<string, OCPAPISpec>;
    httpClient: OCPHTTPClient;
    storage: OCPStorage | null;

    /**
     * Initialize OCP Agent with context and schema discovery.
     * 
     * @param agentType - Type of AI agent (e.g., "ide_coding_assistant")
     * @param user - User identifier
     * @param workspace - Current workspace/project
     * @param agentGoal - Current objective or goal
     * @param registryUrl - Custom registry URL (uses OCP_REGISTRY_URL env var or default if not provided)
     * @param enableCache - Enable local API caching and session persistence (default: true)
     */
    constructor(
        agentType: string = 'ai_agent',
        user?: string,
        workspace?: string,
        agentGoal?: string,
        registryUrl?: string,
        enableCache: boolean = true
    ) {
        this.context = new AgentContext({
            agent_type: agentType,
            user,
            workspace,
            current_goal: agentGoal
        });
        this.discovery = new OCPSchemaDiscovery();
        this.registry = new OCPRegistry(registryUrl);
        this.knownApis = new Map();
        this.httpClient = new OCPHTTPClient(this.context);
        this.storage = enableCache ? new OCPStorage() : null;
    }

    /**
     * Register an API for discovery and usage.
     * 
     * @param name - Human-readable name for the API or registry API name
     * @param specUrl - URL to OpenAPI specification (optional if using registry lookup)
     * @param baseUrl - Optional override for API base URL
     * @returns Discovered API specification with available tools
     * 
     * @example
     * // Registry lookup (fast)
     * await agent.registerApi('github');
     * 
     * @example
     * // Direct OpenAPI discovery
     * await agent.registerApi('my-api', 'https://api.example.com/openapi.json');
     */
    async registerApi(name: string, specUrl?: string, baseUrl?: string): Promise<OCPAPISpec> {
        // Check memory first
        const existingSpec = this.knownApis.get(name);
        if (existingSpec) {
            return existingSpec;
        }

        // Check cache if storage enabled (7-day expiration)
        if (this.storage) {
            const cachedSpec = await this.storage.getCachedApi(name, 7);
            if (cachedSpec) {
                this.knownApis.set(name, cachedSpec);
                this.context.addApiSpec(name, 'cache');
                return cachedSpec;
            }
        }

        // Lookup chain: Registry or Direct OpenAPI discovery
        let apiSpec: OCPAPISpec;
        let source: string;

        if (specUrl) {
            // Direct OpenAPI discovery (existing behavior)
            apiSpec = await this.discovery.discoverApi(specUrl, baseUrl);
            source = specUrl;
        } else {
            // Registry lookup (new behavior)
            apiSpec = await this.registry.getApiSpec(name, baseUrl);
            source = `registry:${name}`;
        }

        // Store API spec in memory
        this.knownApis.set(name, apiSpec);

        // Cache to disk if storage enabled
        if (this.storage) {
            await this.storage.cacheApi(name, apiSpec, { source });
        }

        // Add to context's API specs
        this.context.addApiSpec(name, source);

        // Log API registration
        this.context.addInteraction(
            'api_registered',
            source,
            `Discovered ${apiSpec.tools.length} tools`,
            {
                api_name: name,
                api_title: apiSpec.title,
                tool_count: apiSpec.tools.length,
                base_url: apiSpec.base_url,
                source: specUrl ? 'openapi' : 'registry'
            }
        );

        return apiSpec;
    }

    /**
     * List available tools.
     * 
     * @param apiName - Optional API name to filter tools
     * @returns List of available tools
     */
    listTools(apiName?: string): OCPTool[] {
        if (apiName) {
            const apiSpec = this.knownApis.get(apiName);
            if (!apiSpec) {
                throw new Error(`Unknown API: ${apiName}`);
            }
            return apiSpec.tools;
        }

        // Return tools from all APIs
        const allTools: OCPTool[] = [];
        for (const apiSpec of this.knownApis.values()) {
            allTools.push(...apiSpec.tools);
        }

        return allTools;
    }

    /**
     * Get specific tool by name.
     * 
     * @param toolName - Name of the tool to find
     * @param apiName - Optional API name to search within
     * @returns Found tool or undefined
     */
    getTool(toolName: string, apiName?: string): OCPTool | undefined {
        const tools = this.listTools(apiName);

        for (const tool of tools) {
            if (tool.name === toolName) {
                return tool;
            }
        }

        return undefined;
    }

    /**
     * Search tools by name or description.
     * 
     * @param query - Search query
     * @param apiName - Optional API name to search within
     * @returns List of matching tools
     */
    searchTools(query: string, apiName?: string): OCPTool[] {
        if (apiName) {
            const apiSpec = this.knownApis.get(apiName);
            if (!apiSpec) {
                return [];
            }
            return this.discovery.searchTools(apiSpec, query);
        }

        // Search across all APIs
        const matches: OCPTool[] = [];
        for (const apiSpec of this.knownApis.values()) {
            matches.push(...this.discovery.searchTools(apiSpec, query));
        }

        return matches;
    }

    /**
     * Call a discovered tool with OCP context injection.
     * 
     * @param toolName - Name of the tool to call
     * @param parameters - Parameters for the tool call
     * @param apiName - Optional API name if tool name is ambiguous
     * @returns HTTP response from the API call
     */
    async callTool(
        toolName: string,
        parameters: Record<string, any> = {},
        apiName?: string
    ): Promise<OCPResponse> {
        // Find the tool
        const tool = this.getTool(toolName, apiName);
        if (!tool) {
            const availableTools = this.listTools(apiName).map(t => t.name);
            throw new Error(`Tool '${toolName}' not found. Available tools: ${availableTools.join(', ')}`);
        }

        // Find the API spec for this tool
        let apiSpec: OCPAPISpec | undefined;
        for (const spec of this.knownApis.values()) {
            if (spec.tools.includes(tool)) {
                apiSpec = spec;
                break;
            }
        }

        if (!apiSpec) {
            throw new Error(`Could not find API spec for tool '${toolName}'`);
        }

        // Validate parameters
        const validationErrors = this._validateParameters(tool, parameters);
        if (validationErrors.length > 0) {
            throw new Error(`Parameter validation failed: ${validationErrors.join(', ')}`);
        }

        // Build request
        const [url, requestParams] = this._buildRequest(apiSpec, tool, parameters);

        // Log the tool call
        this.context.addInteraction(
            `tool_call:${toolName}`,
            url,
            'executing',
            {
                tool_name: toolName,
                parameters,
                method: tool.method
            }
        );

        // Make the request with OCP context enhancement
        try {
            const response = await this.httpClient.request(tool.method, url, requestParams);

            // Log the result
            this.context.addInteraction(
                `tool_response:${toolName}`,
                url,
                `${response.status} ${response.statusText}`,
                {
                    status_code: response.status,
                    success: response.ok,
                    response_size: response.text.length
                }
            );

            return response;

        } catch (error) {
            // Log the error
            this.context.addInteraction(
                `tool_error:${toolName}`,
                url,
                `Error: ${error instanceof Error ? error.message : String(error)}`,
                {
                    error_type: error instanceof Error ? error.constructor.name : 'Unknown',
                    error_message: error instanceof Error ? error.message : String(error)
                }
            );
            throw error;
        }
    }

    /**
     * Validate parameters against tool schema.
     */
    private _validateParameters(tool: OCPTool, parameters: Record<string, any>): string[] {
        const errors: string[] = [];

        // Check required parameters
        for (const [paramName, paramInfo] of Object.entries(tool.parameters)) {
            if (paramInfo.required && !(paramName in parameters)) {
                errors.push(`Missing required parameter: ${paramName}`);
            }
        }

        // Check parameter types (basic validation)
        for (const [paramName, value] of Object.entries(parameters)) {
            if (paramName in tool.parameters) {
                const paramInfo = tool.parameters[paramName];
                const expectedType = paramInfo.type || 'string';

                // Basic type checking
                if (expectedType === 'integer' && !Number.isInteger(value)) {
                    errors.push(`Parameter '${paramName}' should be integer, got ${typeof value}`);
                } else if (expectedType === 'boolean' && typeof value !== 'boolean') {
                    errors.push(`Parameter '${paramName}' should be boolean, got ${typeof value}`);
                } else if (expectedType === 'array' && !Array.isArray(value)) {
                    errors.push(`Parameter '${paramName}' should be array, got ${typeof value}`);
                }
            }
        }

        return errors;
    }

    /**
     * Build HTTP request from tool and parameters.
     */
    private _buildRequest(
        apiSpec: OCPAPISpec,
        tool: OCPTool,
        parameters: Record<string, any>
    ): [string, any] {
        // Start with base URL and path
        let url = apiSpec.base_url.replace(/\/$/, '') + tool.path;

        // Separate parameters by location
        const pathParams: Record<string, any> = {};
        const queryParams: Record<string, any> = {};
        const bodyParams: Record<string, any> = {};
        const headerParams: Record<string, any> = {};

        for (const [paramName, value] of Object.entries(parameters)) {
            if (paramName in tool.parameters) {
                const location = tool.parameters[paramName].location || 'query';

                if (location === 'path') {
                    pathParams[paramName] = value;
                } else if (location === 'query') {
                    queryParams[paramName] = value;
                } else if (location === 'body') {
                    bodyParams[paramName] = value;
                } else if (location === 'header') {
                    headerParams[paramName] = value;
                }
            }
        }

        // Replace path parameters
        for (const [paramName, value] of Object.entries(pathParams)) {
            url = url.replace(`{${paramName}}`, String(value));
        }

        // Build request parameters
        const requestParams: any = {};

        if (Object.keys(queryParams).length > 0) {
            requestParams.params = queryParams;
        }

        if (Object.keys(bodyParams).length > 0) {
            requestParams.json = bodyParams;
        }

        if (Object.keys(headerParams).length > 0) {
            requestParams.headers = headerParams;
        }

        // Set timeout
        requestParams.timeout = 30000;

        return [url, requestParams];
    }

    /**
     * Get documentation for a specific tool.
     */
    getToolDocumentation(toolName: string, apiName?: string): string {
        const tool = this.getTool(toolName, apiName);
        if (!tool) {
            return `Tool '${toolName}' not found`;
        }

        return this.discovery.generateToolDocumentation(tool);
    }

    /**
     * Update agent goal and context.
     */
    updateGoal(goal: string, summary?: string): void {
        this.context.updateGoal(goal, summary);
    }
}
