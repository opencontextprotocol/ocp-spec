/**
 * Tests for OCP Storage functionality.
 */

import { describe, test, expect, beforeEach, afterEach } from '@jest/globals';
import { OCPStorage } from '../src/storage.js';
import { AgentContext } from '../src/context.js';
import type { OCPAPISpec } from '../src/schema_discovery.js';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';

describe('OCP Storage', () => {
    let storage: OCPStorage;
    let tempDir: string;

    // Sample API spec for testing
    const sampleApiSpec: OCPAPISpec = {
        title: 'Test API',
        version: '1.0.0',
        base_url: 'https://api.test.com',
        description: 'A test API for testing',
        raw_spec: {
            openapi: '3.0.0',
            info: {
                title: 'Test API',
                version: '1.0.0',
                description: 'A test API for testing'
            },
            servers: [{ url: 'https://api.test.com' }],
            paths: {}
        },
        tools: [
            {
                name: 'get_items',
                description: 'Get all items',
                method: 'GET',
                path: '/items',
                parameters: {},
                response_schema: { type: 'object' },
                operation_id: 'getItems',
                tags: ['items']
            }
        ]
    };

    // Sample context for testing
    const createSampleContext = (): AgentContext => {
        return new AgentContext({
            agent_type: 'test_agent',
            user: 'test_user',
            workspace: 'test_workspace',
            current_goal: 'Testing storage'
        });
    };

    beforeEach(async () => {
        // Create temporary directory for tests
        tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'ocp-storage-test-'));
        storage = new OCPStorage(tempDir);
    });

    afterEach(async () => {
        // Clean up temporary directory
        try {
            await fs.rm(tempDir, { recursive: true, force: true });
        } catch (err) {
            // Ignore cleanup errors
        }
    });

    // ========================================
    // Initialization Tests
    // ========================================

    describe('Initialization', () => {
        test('should initialize with default path', () => {
            const defaultStorage = new OCPStorage();
            expect(defaultStorage.basePath).toBe(path.join(os.homedir(), '.ocp'));
        });

        test('should initialize with custom path', () => {
            expect(storage.basePath).toBe(tempDir);
            expect(storage.cacheDir).toBe(path.join(tempDir, 'cache', 'apis'));
            expect(storage.sessionsDir).toBe(path.join(tempDir, 'sessions'));
        });

        test('should create directories on initialization', async () => {
            // Give it a moment to create directories
            await new Promise(resolve => setTimeout(resolve, 100));

            const cacheDirExists = await fs.access(storage.cacheDir).then(() => true).catch(() => false);
            const sessionsDirExists = await fs.access(storage.sessionsDir).then(() => true).catch(() => false);

            expect(cacheDirExists).toBe(true);
            expect(sessionsDirExists).toBe(true);
        });
    });

    // ========================================
    // API Caching Tests
    // ========================================

    describe('API Caching', () => {
        test('should cache API successfully', async () => {
            const result = await storage.cacheApi('test_api', sampleApiSpec);
            expect(result).toBe(true);

            // Verify file exists
            const cacheFile = path.join(storage.cacheDir, 'test_api.json');
            const exists = await fs.access(cacheFile).then(() => true).catch(() => false);
            expect(exists).toBe(true);
        });

        test('should cache API with metadata', async () => {
            const metadata = { source: 'registry', custom_field: 'value' };
            const result = await storage.cacheApi('test_api', sampleApiSpec, metadata);
            
            expect(result).toBe(true);
            
            // Verify file content includes metadata
            const cacheFile = path.join(storage.cacheDir, 'test_api.json');
            const content = await fs.readFile(cacheFile, 'utf-8');
            const data = JSON.parse(content);
            
            expect(data.source).toBe('registry');
            expect(data.custom_field).toBe('value');
            expect(data.api_name).toBe('test_api');
            expect(data.cached_at).toBeDefined();
        });

        test('should retrieve cached API', async () => {
            await storage.cacheApi('test_api', sampleApiSpec);

            const retrieved = await storage.getCachedApi('test_api');
            expect(retrieved).not.toBeNull();
            expect(retrieved?.title).toBe('Test API');
            expect(retrieved?.tools.length).toBe(1);
        });

        test('should return null for non-existent API', async () => {
            const retrieved = await storage.getCachedApi('non_existent');
            expect(retrieved).toBeNull();
        });

        test('should respect expiration when retrieving', async () => {
            await storage.cacheApi('test_api', sampleApiSpec);

            // Manually modify cached_at to be 8 days old
            const cacheFile = path.join(storage.cacheDir, 'test_api.json');
            const content = await fs.readFile(cacheFile, 'utf-8');
            const data = JSON.parse(content);

            const eightDaysAgo = new Date();
            eightDaysAgo.setDate(eightDaysAgo.getDate() - 8);
            data.cached_at = eightDaysAgo.toISOString();

            await fs.writeFile(cacheFile, JSON.stringify(data, null, 2), 'utf-8');

            // Should be expired with 7 day limit
            const retrieved = await storage.getCachedApi('test_api', 7);
            expect(retrieved).toBeNull();
        });

        test('should ignore expiration when maxAgeDays is null', async () => {
            await storage.cacheApi('test_api', sampleApiSpec);

            // Manually modify cached_at to be 8 days old
            const cacheFile = path.join(storage.cacheDir, 'test_api.json');
            const content = await fs.readFile(cacheFile, 'utf-8');
            const data = JSON.parse(content);

            const eightDaysAgo = new Date();
            eightDaysAgo.setDate(eightDaysAgo.getDate() - 8);
            data.cached_at = eightDaysAgo.toISOString();

            await fs.writeFile(cacheFile, JSON.stringify(data, null, 2), 'utf-8');

            // Should still be retrieved when no expiration limit is set
            const retrieved = await storage.getCachedApi('test_api', null);
            expect(retrieved).not.toBeNull();
        });

        test('should list cached APIs', async () => {
            await storage.cacheApi('github', sampleApiSpec);
            await storage.cacheApi('stripe', sampleApiSpec);

            const apis = await storage.listCachedApis();
            expect(apis).toContain('github');
            expect(apis).toContain('stripe');
            expect(apis.length).toBe(2);
        });

        test('should return empty list when cache is empty', async () => {
            const apis = await storage.listCachedApis();
            expect(apis).toEqual([]);
        });

        test('should search cache by name and description', async () => {
            // Create different API specs
            const githubSpec: OCPAPISpec = {
                title: 'GitHub API',
                version: '1.0.0',
                base_url: 'https://api.github.com',
                description: 'GitHub REST API',
                raw_spec: {},
                tools: [
                    {
                        name: 'list_repos',
                        description: 'List repositories',
                        method: 'GET',
                        path: '/repos',
                        parameters: {},
                        response_schema: {},
                        operation_id: 'listRepos',
                        tags: ['repos']
                    }
                ]
            };
            
            const stripeSpec: OCPAPISpec = {
                title: 'Stripe API',
                version: '1.0.0',
                base_url: 'https://api.stripe.com',
                description: 'Stripe payment API',
                raw_spec: {},
                tools: [
                    {
                        name: 'create_payment',
                        description: 'Create payment intent',
                        method: 'POST',
                        path: '/payments',
                        parameters: {},
                        response_schema: {},
                        operation_id: 'createPayment',
                        tags: ['payments']
                    }
                ]
            };
            
            await storage.cacheApi('github', githubSpec);
            await storage.cacheApi('stripe', stripeSpec);
            
            // Search by name
            let results = await storage.searchCache('github');
            expect(results).toHaveLength(1);
            expect(results[0].name).toBe('github');
            
            // Search by description
            results = await storage.searchCache('payment');
            expect(results).toHaveLength(1);
            expect(results[0].name).toBe('stripe');
            
            // Search by tool description
            results = await storage.searchCache('repositories');
            expect(results).toHaveLength(1);
            expect(results[0].name).toBe('github');
            
            // Case-insensitive search
            results = await storage.searchCache('GITHUB');
            expect(results).toHaveLength(1);
            expect(results[0].name).toBe('github');
            
            // Verify result format
            expect(results[0]).toEqual(expect.objectContaining({
                name: expect.any(String),
                title: expect.any(String),
                version: expect.any(String),
                base_url: expect.any(String),
                cached_at: expect.any(String),
                tool_count: expect.any(Number)
            }));
        });

        test('should clear specific cached API', async () => {
            await storage.cacheApi('github', sampleApiSpec);
            await storage.cacheApi('stripe', sampleApiSpec);

            const result = await storage.clearCache('github');
            expect(result).toBe(true);

            const apis = await storage.listCachedApis();
            expect(apis).not.toContain('github');
            expect(apis).toContain('stripe');
        });

        test('should clear all cached APIs', async () => {
            await storage.cacheApi('github', sampleApiSpec);
            await storage.cacheApi('stripe', sampleApiSpec);

            const result = await storage.clearCache();
            expect(result).toBe(true);

            const apis = await storage.listCachedApis();
            expect(apis).toEqual([]);
        });
    });

    // ========================================
    // Session Persistence Tests
    // ========================================

    describe('Session Persistence', () => {
        test('should save session successfully', async () => {
            const context = createSampleContext();
            const result = await storage.saveSession('test-session-123', context);
            expect(result).toBe(true);

            // Verify file exists
            const sessionFile = path.join(storage.sessionsDir, 'test-session-123.json');
            const exists = await fs.access(sessionFile).then(() => true).catch(() => false);
            expect(exists).toBe(true);
            
            // Verify file content structure
            const content = await fs.readFile(sessionFile, 'utf-8');
            const data = JSON.parse(content);
            
            expect(data).toEqual(expect.objectContaining({
                session_id: 'test-session-123',
                context_id: expect.any(String),
                agent_type: 'test_agent',
                user: 'test_user',
                workspace: 'test_workspace',
                current_file: null,
                session: expect.any(Object),
                history: expect.any(Array),
                current_goal: 'Testing storage',
                context_summary: null,
                error_context: null,
                recent_changes: expect.any(Array),
                api_specs: expect.any(Object),
                created_at: expect.any(String),
                last_updated: expect.any(String)
            }));
        });

        test('should load session successfully', async () => {
            const context = createSampleContext();
            await storage.saveSession('test-session-123', context);

            const loaded = await storage.loadSession('test-session-123');
            expect(loaded).not.toBeNull();
            expect(loaded?.agent_type).toBe('test_agent');
            expect(loaded?.user).toBe('test_user');
        });

        test('should return null for non-existent session', async () => {
            const loaded = await storage.loadSession('non-existent');
            expect(loaded).toBeNull();
        });

        test('should roundtrip session data', async () => {
            const context = createSampleContext();
            context.addApiSpec('test-api', 'https://test.com');
            context.addInteraction('test', 'request', 'response');

            await storage.saveSession('roundtrip-test', context);
            const loaded = await storage.loadSession('roundtrip-test');

            expect(loaded).not.toBeNull();
            expect(Object.keys(loaded?.api_specs || {}).length).toBe(1);
            expect(loaded?.history.length).toBe(1);
        });

        test('should list sessions', async () => {
            const context1 = createSampleContext();
            const context2 = createSampleContext();

            await storage.saveSession('session-1', context1);
            await storage.saveSession('session-2', context2);

            const sessions = await storage.listSessions();
            expect(sessions.length).toBe(2);
            
            // Verify session metadata structure
            expect(sessions[0]).toEqual(expect.objectContaining({
                id: expect.any(String),
                context_id: expect.any(String),
                agent_type: 'test_agent',
                user: 'test_user',
                workspace: 'test_workspace',
                created_at: expect.any(String),
                last_updated: expect.any(String),
                interaction_count: expect.any(Number)
            }));
        });

        test('should list sessions with limit', async () => {
            const context = createSampleContext();

            await storage.saveSession('session-1', context);
            await storage.saveSession('session-2', context);
            await storage.saveSession('session-3', context);

            const sessions = await storage.listSessions(2);
            expect(sessions.length).toBe(2);
        });

        test('should list sessions sorted by most recent first', async () => {
            const context = createSampleContext();

            await storage.saveSession('session-1', context);
            await new Promise(resolve => setTimeout(resolve, 10));
            await storage.saveSession('session-2', context);
            await new Promise(resolve => setTimeout(resolve, 10));
            await storage.saveSession('session-3', context);

            const sessions = await storage.listSessions();
            expect(sessions[0].id).toBe('session-3');
            expect(sessions[2].id).toBe('session-1');
        });

        test('should return empty list when no sessions exist', async () => {
            const sessions = await storage.listSessions();
            expect(sessions).toEqual([]);
        });

        test('should cleanup old sessions', async () => {
            const context = createSampleContext();

            await storage.saveSession('session-1', context);
            await storage.saveSession('session-2', context);
            await storage.saveSession('session-3', context);

            const deletedCount = await storage.cleanupSessions(2);
            expect(deletedCount).toBe(1);

            const sessions = await storage.listSessions();
            expect(sessions.length).toBe(2);
        });

        test('should cleanup old sessions', async () => {
            const context = createSampleContext();

            // Create multiple sessions
            for (let i = 1; i <= 5; i++) {
                await storage.saveSession(`session-${i}`, context);
                // Small delay to ensure different modification times
                await new Promise(resolve => setTimeout(resolve, 10));
            }

            // Cleanup keeping only 3 most recent
            const deletedCount = await storage.cleanupSessions(3);
            expect(deletedCount).toBe(2);

            const sessions = await storage.listSessions();
            expect(sessions.length).toBe(3);
            
            // Verify we kept the most recent sessions
            const sessionIds = sessions.map(s => s.id).sort();
            expect(sessionIds).toEqual(['session-3', 'session-4', 'session-5']);
        });

        test('should not cleanup if under limit', async () => {
            const context = createSampleContext();

            await storage.saveSession('session-1', context);
            await storage.saveSession('session-2', context);

            const deletedCount = await storage.cleanupSessions(10);
            expect(deletedCount).toBe(0);

            const sessions = await storage.listSessions();
            expect(sessions.length).toBe(2);
        });
    });

    // ========================================
    // Error Handling Tests
    // ========================================

    describe('Error Handling', () => {
        test('should handle invalid cache path gracefully', async () => {
            const invalidStorage = new OCPStorage('/invalid/path/that/does/not/exist');
            const result = await invalidStorage.cacheApi('test', sampleApiSpec);
            // Should return false but not throw
            expect(result).toBe(false);
        });

        test('should handle corrupted cache file', async () => {
            const cacheFile = path.join(storage.cacheDir, 'corrupted.json');
            await fs.writeFile(cacheFile, 'invalid json{{{', 'utf-8');

            const retrieved = await storage.getCachedApi('corrupted');
            expect(retrieved).toBeNull();
        });

        test('should handle invalid session path gracefully', async () => {
            const invalidStorage = new OCPStorage('/invalid/path/that/does/not/exist');
            const context = createSampleContext();
            const result = await invalidStorage.saveSession('test', context);
            // Should return false but not throw
            expect(result).toBe(false);
        });

        test('should handle corrupted session file', async () => {
            const sessionFile = path.join(storage.sessionsDir, 'corrupted.json');
            await fs.writeFile(sessionFile, 'invalid json{{{', 'utf-8');

            const loaded = await storage.loadSession('corrupted');
            expect(loaded).toBeNull();
        });
    });
});
