/**
 * OCP HTTP Client
 * 
 * HTTP client wrapper that automatically injects OCP context headers.
 */

import { AgentContext } from './context.js';
import { createOCPHeaders } from './headers.js';

/**
 * HTTP request options
 */
interface RequestOptions {
    params?: Record<string, string | number | boolean>;
    json?: any;
    headers?: Record<string, string>;
    timeout?: number;
}

/**
 * HTTP response wrapper
 */
export interface OCPResponse {
    status: number;
    statusText: string;
    ok: boolean;
    headers: Headers;
    data: any;
    text: string;
    json: () => Promise<any>;
}

/**
 * OCP HTTP Client
 * 
 * Wraps HTTP requests to automatically inject OCP context headers
 * and log interactions.
 */
export class OCPHTTPClient {
    private context: AgentContext;
    private autoUpdateContext: boolean;

    constructor(context: AgentContext, autoUpdateContext: boolean = true) {
        this.context = context;
        this.autoUpdateContext = autoUpdateContext;
    }

    /**
     * Prepare headers with OCP context.
     */
    private _prepareHeaders(additionalHeaders?: Record<string, string>): Record<string, string> {
        const ocpHeaders = createOCPHeaders(this.context);
        
        return {
            ...ocpHeaders,
            ...additionalHeaders
        };
    }

    /**
     * Log API interaction to context.
     */
    private _logInteraction(method: string, url: string, statusCode?: number, error?: Error): void {
        if (!this.autoUpdateContext) {
            return;
        }

        this.context.addInteraction(
            `api_call_${method.toLowerCase()}`,
            url,
            error ? `Error: ${error.message}` : (statusCode !== undefined ? `${statusCode}` : undefined),
            {
                method,
                status_code: statusCode,
                success: !error && statusCode ? statusCode >= 200 && statusCode < 300 : false,
                error: error ? error.message : undefined
            }
        );
    }

    /**
     * Make HTTP request.
     */
    async request(method: string, url: string, options: RequestOptions = {}): Promise<OCPResponse> {
        const { params, json, headers, timeout = 30000 } = options;

        // Build URL with query parameters
        const finalUrl = new URL(url);
        if (params) {
            for (const [key, value] of Object.entries(params)) {
                finalUrl.searchParams.append(key, String(value));
            }
        }

        // Prepare headers
        const finalHeaders = this._prepareHeaders(headers);
        
        // Add content-type for JSON
        if (json !== undefined) {
            finalHeaders['Content-Type'] = 'application/json';
        }

        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(finalUrl.toString(), {
                method: method.toUpperCase(),
                headers: finalHeaders,
                body: json !== undefined ? JSON.stringify(json) : undefined,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // Read response text
            const text = await response.text();
            
            // Parse JSON if possible
            let data: any;
            try {
                data = JSON.parse(text);
            } catch {
                data = text;
            }

            const ocpResponse: OCPResponse = {
                status: response.status,
                statusText: response.statusText,
                ok: response.ok,
                headers: response.headers,
                data,
                text,
                json: async () => JSON.parse(text)
            };

            this._logInteraction(method, finalUrl.toString(), response.status);

            return ocpResponse;

        } catch (error) {
            clearTimeout(timeoutId);
            
            const err = error instanceof Error ? error : new Error(String(error));
            this._logInteraction(method, finalUrl.toString(), undefined, err);
            
            throw err;
        }
    }

    /**
     * GET request.
     */
    async get(url: string, options: RequestOptions = {}): Promise<OCPResponse> {
        return this.request('GET', url, options);
    }

    /**
     * POST request.
     */
    async post(url: string, options: RequestOptions = {}): Promise<OCPResponse> {
        return this.request('POST', url, options);
    }

    /**
     * PUT request.
     */
    async put(url: string, options: RequestOptions = {}): Promise<OCPResponse> {
        return this.request('PUT', url, options);
    }

    /**
     * DELETE request.
     */
    async delete(url: string, options: RequestOptions = {}): Promise<OCPResponse> {
        return this.request('DELETE', url, options);
    }

    /**
     * PATCH request.
     */
    async patch(url: string, options: RequestOptions = {}): Promise<OCPResponse> {
        return this.request('PATCH', url, options);
    }
}

/**
 * Create API-specific HTTP client.
 * 
 * @param context - Agent context
 * @param baseUrl - API base URL
 * @param headers - Optional headers to include in all requests
 * @returns Configured HTTP client
 */
export function wrapApi(context: AgentContext, baseUrl: string, headers?: Record<string, string>): OCPHTTPClient {
    const client = new OCPHTTPClient(context);
    
    // Normalize base URL (remove trailing slash)
    const normalizedBase = baseUrl.replace(/\/$/, '');
    
    // Helper to build full URL
    const buildUrl = (path: string): string => {
        // If path is absolute URL, return it unchanged
        if (path.startsWith('http://') || path.startsWith('https://')) {
            return path;
        }
        // Otherwise, concatenate with base URL
        return `${normalizedBase}${path}`;
    };
    
    // Override request method to handle base URL and additional headers (like Python)
    const originalRequest = client.request.bind(client);
    client.request = (method: string, path: string, options: RequestOptions = {}) => {
        const opts = { ...options };
        if (headers) {
            opts.headers = { ...headers, ...opts.headers };
        }
        return originalRequest(method, buildUrl(path), opts);
    };

    return client;
}
