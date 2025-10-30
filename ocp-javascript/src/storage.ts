/**
 * OCPStorage - Local storage for API caching and session persistence.
 *
 * Provides optional local storage for OCP agents to cache API specifications
 * and persist session contexts across application restarts.
 */

import * as fs from 'fs/promises';
import * as fsSync from 'fs';
import * as path from 'path';
import * as os from 'os';
import { AgentContext } from './context.js';
import type { OCPAPISpec, OCPTool } from './schema_discovery.js';

/**
 * Local storage manager for OCP API cache and session persistence.
 *
 * Storage directory structure:
 *     ~/.ocp/
 *     ├── cache/
 *     │   └── apis/
 *     │       ├── github.json
 *     │       ├── stripe.json
 *     │       └── ...
 *     └── sessions/
 *         ├── vscode-chat-abc123.json
 *         ├── cli-session-xyz789.json
 *         └── ...
 *
 * Design principles:
 * - Per-file storage for surgical reads/writes
 * - Fail-safe: storage errors don't break functionality
 * - Consumer-agnostic: doesn't manage consumer config
 */
export class OCPStorage {
    public readonly basePath: string;
    public readonly cacheDir: string;
    public readonly sessionsDir: string;

    /**
     * Initialize storage with base directory.
     *
     * @param basePath - Base storage directory (defaults to ~/.ocp/)
     */
    constructor(basePath?: string) {
        this.basePath = basePath ?? path.join(os.homedir(), '.ocp');
        this.cacheDir = path.join(this.basePath, 'cache', 'apis');
        this.sessionsDir = path.join(this.basePath, 'sessions');

        // Create directories synchronously in constructor
        this.ensureDirsSync();
    }

    /**
     * Create storage directories if they don't exist (synchronous).
     */
    private ensureDirsSync(): void {
        try {
            fsSync.mkdirSync(this.cacheDir, { recursive: true });
            fsSync.mkdirSync(this.sessionsDir, { recursive: true });
        } catch (err) {
            // Non-fatal: log but don't throw
            console.warn(`Warning: Failed to create storage directories: ${err}`);
        }
    }

    // ==================== API Caching ====================

    /**
     * Cache an API specification locally.
     *
     * @param name - API name (used as filename)
     * @param spec - API specification to cache
     * @param metadata - Optional metadata (source, cached_at, etc.)
     * @returns True if cached successfully, false on error
     */
    async cacheApi(
        name: string,
        spec: OCPAPISpec,
        metadata?: Record<string, any>
    ): Promise<boolean> {
        try {
            const cacheFile = path.join(this.cacheDir, `${name}.json`);

            const cacheData = {
                api_name: name,
                title: spec.title,
                version: spec.version,
                base_url: spec.base_url,
                cached_at: new Date().toISOString(),
                source: metadata?.source ?? 'unknown',
                raw_spec: spec.raw_spec,
                tools: spec.tools.map((tool: OCPTool) => ({
                    name: tool.name,
                    method: tool.method,
                    path: tool.path,
                    description: tool.description,
                    parameters: tool.parameters,
                    response_schema: tool.response_schema,
                    operation_id: tool.operation_id,
                    tags: tool.tags
                }))
            };

            if (spec.description) {
                (cacheData as any).description = spec.description;
            }

            await fs.writeFile(
                cacheFile,
                JSON.stringify(cacheData, null, 2),
                'utf-8'
            );

            return true;
        } catch (err) {
            console.warn(`Warning: Failed to cache API '${name}': ${err}`);
            return false;
        }
    }

    /**
     * Retrieve cached API specification.
     *
     * @param name - API name to retrieve
     * @param maxAgeDays - Maximum age in days (0 = no expiration check)
     * @returns Cached API spec or null if not found/expired
     */
    async getCachedApi(
        name: string,
        maxAgeDays: number = 7
    ): Promise<OCPAPISpec | null> {
        try {
            const cacheFile = path.join(this.cacheDir, `${name}.json`);
            const content = await fs.readFile(cacheFile, 'utf-8');
            const data = JSON.parse(content);

            // Check expiration if maxAgeDays > 0
            if (maxAgeDays > 0 && data.cached_at) {
                const cachedAt = new Date(data.cached_at);
                const now = new Date();
                const ageMs = now.getTime() - cachedAt.getTime();
                const ageDays = ageMs / (1000 * 60 * 60 * 24);

                if (ageDays > maxAgeDays) {
                    return null; // Expired
                }
            }

            // Reconstruct OCPAPISpec
            const spec: OCPAPISpec = {
                title: data.title,
                version: data.version,
                base_url: data.base_url,
                description: data.description || '',
                raw_spec: data.raw_spec,
                tools: data.tools.map((tool: any) => ({
                    name: tool.name,
                    method: tool.method,
                    path: tool.path,
                    description: tool.description,
                    parameters: tool.parameters,
                    response_schema: tool.response_schema,
                    operation_id: tool.operation_id,
                    tags: tool.tags
                }))
            };

            return spec;
        } catch (err) {
            // File not found or parse error
            return null;
        }
    }

    /**
     * Search cached APIs by name or description.
     *
     * @param query - Search query (case-insensitive)
     * @returns List of matching API metadata
     */
    async searchCache(query: string): Promise<Array<Record<string, any>>> {
        try {
            const files = await fs.readdir(this.cacheDir);
            const results: Array<Record<string, any>> = [];
            const lowerQuery = query.toLowerCase();

            for (const file of files) {
                if (!file.endsWith('.json')) continue;

                try {
                    const filePath = path.join(this.cacheDir, file);
                    const content = await fs.readFile(filePath, 'utf-8');
                    const data = JSON.parse(content);

                    // Search in name, title, description, and tool descriptions
                    const searchText = [
                        data.api_name || '',
                        data.title || '',
                        data.description || '',
                        ...(data.tools || []).map((t: any) => t.description || '')
                    ].join(' ').toLowerCase();

                    if (searchText.includes(lowerQuery)) {
                        results.push({
                            api_name: data.api_name,
                            title: data.title,
                            version: data.version,
                            description: data.description,
                            cached_at: data.cached_at,
                            source: data.source,
                            tool_count: data.tools?.length || 0
                        });
                    }
                } catch {
                    // Skip files that can't be parsed
                    continue;
                }
            }

            return results;
        } catch (err) {
            console.warn(`Warning: Failed to search cache: ${err}`);
            return [];
        }
    }

    /**
     * List all cached API names.
     *
     * @returns List of cached API names
     */
    async listCachedApis(): Promise<string[]> {
        try {
            const files = await fs.readdir(this.cacheDir);
            return files
                .filter(f => f.endsWith('.json'))
                .map(f => f.replace('.json', ''));
        } catch (err) {
            console.warn(`Warning: Failed to list cached APIs: ${err}`);
            return [];
        }
    }

    /**
     * Clear cached API(s).
     *
     * @param name - API name to clear, or null to clear all
     * @returns True if cleared successfully
     */
    async clearCache(name?: string): Promise<boolean> {
        try {
            if (name) {
                // Clear specific API
                const cacheFile = path.join(this.cacheDir, `${name}.json`);
                await fs.unlink(cacheFile);
            } else {
                // Clear all APIs
                const files = await fs.readdir(this.cacheDir);
                for (const file of files) {
                    if (file.endsWith('.json')) {
                        await fs.unlink(path.join(this.cacheDir, file));
                    }
                }
            }
            return true;
        } catch (err) {
            console.warn(`Warning: Failed to clear cache: ${err}`);
            return false;
        }
    }

    // ==================== Session Persistence ====================

    /**
     * Save session context to disk.
     *
     * @param sessionId - Unique session identifier
     * @param context - AgentContext to save
     * @returns True if saved successfully
     */
    async saveSession(sessionId: string, context: AgentContext): Promise<boolean> {
        try {
            const sessionFile = path.join(this.sessionsDir, `${sessionId}.json`);

            const sessionData = {
                session_id: sessionId,
                saved_at: new Date().toISOString(),
                context: context.toDict()
            };

            await fs.writeFile(
                sessionFile,
                JSON.stringify(sessionData, null, 2),
                'utf-8'
            );

            return true;
        } catch (err) {
            console.warn(`Warning: Failed to save session '${sessionId}': ${err}`);
            return false;
        }
    }

    /**
     * Load session context from disk.
     *
     * @param sessionId - Session identifier
     * @returns AgentContext or null if not found
     */
    async loadSession(sessionId: string): Promise<AgentContext | null> {
        try {
            const sessionFile = path.join(this.sessionsDir, `${sessionId}.json`);
            const content = await fs.readFile(sessionFile, 'utf-8');
            const data = JSON.parse(content);

            return AgentContext.fromDict(data.context);
        } catch (err) {
            // File not found or parse error
            return null;
        }
    }

    /**
     * List all session metadata.
     *
     * @param limit - Maximum number of sessions to return (0 = all)
     * @returns List of session metadata, sorted by most recent first
     */
    async listSessions(limit: number = 0): Promise<Array<Record<string, any>>> {
        try {
            const files = await fs.readdir(this.sessionsDir);
            const sessions: Array<Record<string, any>> = [];

            for (const file of files) {
                if (!file.endsWith('.json')) continue;

                try {
                    const filePath = path.join(this.sessionsDir, file);
                    const content = await fs.readFile(filePath, 'utf-8');
                    const data = JSON.parse(content);

                    sessions.push({
                        session_id: data.session_id,
                        saved_at: data.saved_at,
                        agent_type: data.context?.agent_type,
                        user: data.context?.user,
                        workspace: data.context?.workspace
                    });
                } catch {
                    // Skip files that can't be parsed
                    continue;
                }
            }

            // Sort by saved_at descending (most recent first)
            sessions.sort((a, b) => {
                const dateA = new Date(a.saved_at).getTime();
                const dateB = new Date(b.saved_at).getTime();
                return dateB - dateA;
            });

            // Apply limit if specified
            if (limit > 0) {
                return sessions.slice(0, limit);
            }

            return sessions;
        } catch (err) {
            console.warn(`Warning: Failed to list sessions: ${err}`);
            return [];
        }
    }

    /**
     * Clean up old sessions, keeping only the most recent N.
     *
     * @param keepRecent - Number of recent sessions to keep
     * @returns Number of sessions deleted
     */
    async cleanupSessions(keepRecent: number = 10): Promise<number> {
        try {
            const sessions = await this.listSessions();

            if (sessions.length <= keepRecent) {
                return 0; // Nothing to clean up
            }

            const toDelete = sessions.slice(keepRecent);
            let deletedCount = 0;

            for (const session of toDelete) {
                try {
                    const sessionFile = path.join(
                        this.sessionsDir,
                        `${session.session_id}.json`
                    );
                    await fs.unlink(sessionFile);
                    deletedCount++;
                } catch {
                    // Continue even if deletion fails
                    continue;
                }
            }

            return deletedCount;
        } catch (err) {
            console.warn(`Warning: Failed to cleanup sessions: ${err}`);
            return 0;
        }
    }
}
