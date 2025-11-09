/**
 * OCP Schema Discovery
 * 
 * Automatic OpenAPI schema discovery and tool extraction for OCP agents.
 */

import { SchemaDiscoveryError } from './errors.js';

/**
 * Tool definition extracted from OpenAPI operation
 */
export interface OCPTool {
    name: string;
    description: string;
    method: string;
    path: string;
    parameters: Record<string, any>;
    response_schema?: Record<string, any>;
    operation_id?: string;
    tags?: string[];
}

/**
 * Complete API specification with tools
 */
export interface OCPAPISpec {
    base_url: string;
    title: string;
    version: string;
    description: string;
    tools: OCPTool[];
    raw_spec: Record<string, any>;
}

/**
 * OCP Schema Discovery Client
 * 
 * Discovers and parses OpenAPI specifications to extract available tools.
 */
export class OCPSchemaDiscovery {
    private cache: Map<string, OCPAPISpec>;

    constructor() {
        this.cache = new Map();
    }

    /**
     * Discover API from OpenAPI specification.
     * 
     * @param specUrl - URL to OpenAPI specification (JSON or YAML)
     * @param baseUrl - Optional override for API base URL
     * @returns API specification with extracted tools
     */
    async discoverApi(specUrl: string, baseUrl?: string): Promise<OCPAPISpec> {
        // Check cache
        if (this.cache.has(specUrl)) {
            return this.cache.get(specUrl)!;
        }

        try {
            const spec = await this._fetchSpec(specUrl);
            const apiSpec = this._parseOpenApiSpec(spec, baseUrl);
            
            // Cache the result
            this.cache.set(specUrl, apiSpec);
            
            return apiSpec;
        } catch (error) {
            throw new SchemaDiscoveryError(
                `Failed to discover API: ${error instanceof Error ? error.message : String(error)}`
            );
        }
    }

    /**
     * Fetch OpenAPI specification from URL.
     */
    private async _fetchSpec(specUrl: string): Promise<Record<string, any>> {
        try {
            const response = await fetch(specUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json() as Record<string, any>;
            
        } catch (error) {
            throw new SchemaDiscoveryError(
                `Failed to fetch OpenAPI spec from ${specUrl}: ${error instanceof Error ? error.message : String(error)}`
            );
        }
    }

    /**
     * Parse OpenAPI specification and extract tools.
     */
    private _parseOpenApiSpec(spec: Record<string, any>, baseUrlOverride?: string): OCPAPISpec {
        // Extract API info
        const info = spec.info || {};
        const title = info.title || 'Unknown API';
        const version = info.version || '1.0.0';
        const description = info.description || '';

        // Extract base URL
        let baseUrl = baseUrlOverride;
        if (!baseUrl && spec.servers && spec.servers.length > 0) {
            baseUrl = spec.servers[0].url;
        }
        if (!baseUrl) {
            throw new SchemaDiscoveryError('No base URL found in OpenAPI spec and none provided');
        }

        // Extract tools from paths
        const tools: OCPTool[] = [];
        const paths = spec.paths || {};

        for (const [path, pathItem] of Object.entries(paths)) {
            if (typeof pathItem !== 'object' || pathItem === null) continue;

            for (const [method, operation] of Object.entries(pathItem as Record<string, any>)) {
                if (!['get', 'post', 'put', 'delete', 'patch', 'options', 'head'].includes(method.toLowerCase())) {
                    continue;
                }

                const tool = this._createToolFromOperation(path, method, operation);
                if (tool) {
                    tools.push(tool);
                }
            }
        }

        return {
            base_url: baseUrl,
            title,
            version,
            description,
            tools,
            raw_spec: spec
        };
    }

    /**
     * Create tool definition from OpenAPI operation.
     */
    private _createToolFromOperation(path: string, method: string, operation: Record<string, any>): OCPTool | null {
        if (!operation || typeof operation !== 'object') {
            return null;
        }

        const operationId = operation.operationId || `${method}_${path.replace(/\//g, '_')}`;
        const summary = operation.summary || '';
        const description = operation.description || summary || operationId;
        const tags = operation.tags || [];

        // Parse parameters
        const parameters = this._parseParameters(operation.parameters || []);

        // Parse request body
        const bodyParams = this._parseRequestBody(operation.requestBody);
        Object.assign(parameters, bodyParams);

        // Parse response schema
        const responseSchema = this._parseResponses(operation.responses || {});

        return {
            name: operationId,
            description,
            method: method.toUpperCase(),
            path,
            parameters,
            response_schema: responseSchema,
            operation_id: operationId,
            tags
        };
    }

    /**
     * Parse OpenAPI parameters.
     */
    private _parseParameters(parameters: any[]): Record<string, any> {
        const result: Record<string, any> = {};

        for (const param of parameters) {
            if (!param || typeof param !== 'object') continue;

            const name = param.name;
            if (!name) continue;

            result[name] = {
                type: param.schema?.type || 'string',
                description: param.description || '',
                required: param.required || false,
                location: param.in || 'query',
                schema: param.schema || {}
            };
        }

        return result;
    }

    /**
     * Parse OpenAPI request body.
     */
    private _parseRequestBody(requestBody: any): Record<string, any> {
        if (!requestBody || typeof requestBody !== 'object') {
            return {};
        }

        const content = requestBody.content || {};
        const jsonContent = content['application/json'];
        
        if (!jsonContent || !jsonContent.schema) {
            return {};
        }

        const schema = jsonContent.schema;
        const properties = schema.properties || {};
        const required = schema.required || [];
        
        const result: Record<string, any> = {};

        for (const [name, propSchema] of Object.entries(properties)) {
            if (typeof propSchema !== 'object' || propSchema === null) continue;
            
            const prop = propSchema as Record<string, any>;
            result[name] = {
                type: prop.type || 'string',
                description: prop.description || '',
                required: required.includes(name),
                location: 'body',
                schema: prop
            };
        }

        return result;
    }

    /**
     * Parse OpenAPI responses.
     */
    private _parseResponses(responses: Record<string, any>): Record<string, any> | undefined {
        // Find first 2xx response
        for (const [statusCode, response] of Object.entries(responses)) {
            if (statusCode.startsWith('2') && typeof response === 'object' && response !== null) {
                const content = response.content || {};
                const jsonContent = content['application/json'];
                
                if (jsonContent && jsonContent.schema) {
                    return jsonContent.schema;
                }
            }
        }

        return undefined;
    }

    /**
     * Get tools filtered by tag.
     */
    getToolsByTag(apiSpec: OCPAPISpec, tag: string): OCPTool[] {
        return apiSpec.tools.filter(tool => 
            tool.tags && tool.tags.includes(tag)
        );
    }

    /**
     * Search tools by name or description.
     */
    searchTools(apiSpec: OCPAPISpec, query: string): OCPTool[] {
        const lowerQuery = query.toLowerCase();
        
        return apiSpec.tools.filter(tool => 
            tool.name.toLowerCase().includes(lowerQuery) ||
            tool.description.toLowerCase().includes(lowerQuery)
        );
    }

    /**
     * Generate human-readable tool documentation.
     */
    generateToolDocumentation(tool: OCPTool): string {
        const docLines = [
            `## ${tool.name}`,
            `**Method:** ${tool.method}`,
            `**Path:** ${tool.path}`,
            `**Description:** ${tool.description}`,
            ''
        ];

        if (Object.keys(tool.parameters).length > 0) {
            docLines.push('### Parameters:');
            for (const [paramName, paramInfo] of Object.entries(tool.parameters)) {
                const required = paramInfo.required ? ' (required)' : ' (optional)';
                const location = ` [${paramInfo.location || 'query'}]`;
                docLines.push(`- **${paramName}**${required}${location}: ${paramInfo.description || ''}`);
            }
            docLines.push('');
        }

        if (tool.tags && tool.tags.length > 0) {
            docLines.push(`**Tags:** ${tool.tags.join(', ')}`);
            docLines.push('');
        }

        return docLines.join('\n');
    }

    /**
     * Clear the discovery cache.
     */
    clearCache(): void {
        this.cache.clear();
    }
}
