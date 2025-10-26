/**
 * OCP Registry Client
 * 
 * Client for accessing pre-discovered API specifications from the OCP registry.
 */

import { OCPAPISpec, OCPTool } from './schema_discovery.js';
import { RegistryUnavailable, APINotFound } from './errors.js';

const DEFAULT_REGISTRY_URL = 'https://registry.ocp.dev';

/**
 * Registry API entry structure
 */
interface RegistryAPIEntry {
    name: string;
    display_name?: string;
    description?: string;
    base_url?: string;
    tools?: Array<{
        name: string;
        description: string;
        method: string;
        path: string;
        parameters?: Record<string, any>;
        response_schema?: Record<string, any>;
        operation_id?: string;
        tags?: string[];
    }>;
}

/**
 * OCP Registry Client
 * 
 * Access pre-discovered API specifications from the OCP community registry.
 */
export class OCPRegistry {
    private registryUrl: string;

    /**
     * Initialize registry client.
     * 
     * @param registryUrl - Registry URL (defaults to OCP_REGISTRY_URL env var or registry.ocp.dev)
     */
    constructor(registryUrl?: string) {
        this.registryUrl = (registryUrl || process.env.OCP_REGISTRY_URL || DEFAULT_REGISTRY_URL).replace(/\/$/, '');
        
        // Validate URL format
        if (!this.registryUrl.startsWith('http://') && !this.registryUrl.startsWith('https://')) {
            throw new Error(`Invalid registry URL: ${this.registryUrl}`);
        }
    }

    /**
     * Get API specification from registry.
     * 
     * @param name - API name in registry
     * @param baseUrl - Optional override for API base URL
     * @returns API specification with tools
     * @throws RegistryUnavailable if registry is unreachable
     * @throws APINotFound if API is not found in registry
     */
    async getApiSpec(name: string, baseUrl?: string): Promise<OCPAPISpec> {
        try {
            const response = await fetch(`${this.registryUrl}/api/v1/registry/${name}`, {
                timeout: 10000
            } as any);
            
            if (response.status === 404) {
                const suggestions = await this._getSuggestions(name);
                throw new APINotFound(name, suggestions);
            }
            
            if (!response.ok) {
                throw new RegistryUnavailable(
                    this.registryUrl,
                    `${response.statusText}`
                );
            }
            
            const entry = await response.json() as RegistryAPIEntry;
            return await this._entryToSpec(entry, baseUrl);
            
        } catch (error) {
            if (error instanceof APINotFound || error instanceof RegistryUnavailable) {
                throw error;
            }
            
            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new RegistryUnavailable(
                    this.registryUrl,
                    `Could not connect to registry`
                );
            }
            
            throw new RegistryUnavailable(
                this.registryUrl,
                String(error)
            );
        }
    }

    /**
     * Search for APIs in the registry.
     * 
     * @param query - Search query string
     * @returns List of API names matching query
     */
    async searchApis(query: string): Promise<string[]> {
        try {
            const params = new URLSearchParams({ 
                q: query,
                per_page: '10'
            });
            
            const url = `${this.registryUrl}/api/v1/search?${params.toString()}`;
            const response = await fetch(url, {
                timeout: 5000
            } as any);
            
            if (!response.ok) {
                return [];
            }
            
            const searchResults = await response.json() as { results?: Array<{ name: string }> };
            return (searchResults.results || []).map(r => r.name);
            
        } catch {
            // If search fails, return empty list (non-critical)
            return [];
        }
    }

    /**
     * List all APIs in the registry.
     * 
     * @returns List of API names
     */
    async listApis(): Promise<string[]> {
        try {
            const response = await fetch(`${this.registryUrl}/api/v1/registry`, {
                timeout: 10000
            } as any);
            
            if (!response.ok) {
                return [];
            }
            
            const apis = await response.json() as Array<{ name: string }>;
            return apis.map(api => api.name);
            
        } catch {
            // If list fails, return empty list (non-critical)
            return [];
        }
    }

    /**
     * Convert registry entry to API spec.
     */
    private async _entryToSpec(entry: RegistryAPIEntry, baseUrlOverride?: string): Promise<OCPAPISpec> {
        // Use override base_url if provided, otherwise use registry's base_url
        const baseUrl = baseUrlOverride || entry.base_url || '';
        
        // Convert tools from registry format to OCPTool objects
        const tools: OCPTool[] = [];
        if (entry.tools) {
            for (const toolDict of entry.tools) {
                const tool: OCPTool = {
                    name: toolDict.name,
                    description: toolDict.description,
                    method: toolDict.method,
                    path: toolDict.path,
                    parameters: toolDict.parameters || {},
                    response_schema: toolDict.response_schema || {},
                    operation_id: toolDict.operation_id,
                    tags: toolDict.tags || []
                };
                tools.push(tool);
            }
        }
        
        // Create OCPAPISpec (matching dataclass field order)
        return {
            base_url: baseUrl,
            title: entry.display_name || entry.name,
            version: '1.0.0',  // Registry doesn't store version
            description: entry.description || '',
            tools,
            raw_spec: entry  // Store the original registry entry
        };
    }

    /**
     * Get API name suggestions for error messages.
     */
    private async _getSuggestions(apiName: string): Promise<string[]> {
        try {
            // Try exact search first
            let suggestions = await this.searchApis(apiName);
            
            // If no results, try partial matches
            if (suggestions.length === 0 && apiName.length > 2) {
                suggestions = await this.searchApis(apiName.slice(0, 3));
            }
            
            return suggestions.slice(0, 3);
            
        } catch {
            return [];
        }
    }
}
