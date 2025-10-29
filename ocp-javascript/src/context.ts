/**
 * AgentContext - Core context management for OCP agents.
 * 
 * Handles creating, updating, and maintaining agent context throughout
 * multi-step workflows.
 */

import { randomBytes } from 'crypto';
import { createOCPHeaders, parseContext } from './headers.js';

/**
 * OCP Context Object - matches the official OCP specification schema
 */
export interface OCPContextDict {
  context_id: string;
  agent_type: string;
  user: string | null;
  workspace: string | null;
  current_file: string | null;
  session: Record<string, any>;
  history: Array<Record<string, any>>;
  current_goal: string | null;
  context_summary: string | null;
  error_context: string | null;
  recent_changes: string[];
  api_specs: Record<string, string>;
  created_at: string;
  last_updated: string;
}

/**
 * Core agent context that flows through OCP-enabled API calls.
 * 
 * This represents the agent's understanding of the current conversation,
 * workspace state, and goals.
 */
export class AgentContext {
  // Core identification
  context_id: string;
  agent_type: string;

  // Agent state
  user: string | null;
  workspace: string | null;
  current_file: string | null;

  // Conversation tracking
  session: Record<string, any>;
  history: Array<Record<string, any>>;

  // Goals and intent
  current_goal: string | null;
  context_summary: string | null;

  // Technical context
  error_context: string | null;
  recent_changes: string[];

  // API specifications
  api_specs: Record<string, string>;

  // Timestamps
  created_at: Date;
  last_updated: Date;

  constructor(params: {
    context_id?: string;
    agent_type?: string;
    user?: string | null;
    workspace?: string | null;
    current_file?: string | null;
    session?: Record<string, any>;
    history?: Array<Record<string, any>>;
    current_goal?: string | null;
    context_summary?: string | null;
    error_context?: string | null;
    recent_changes?: string[];
    api_specs?: Record<string, string>;
    created_at?: Date;
    last_updated?: Date;
  } = {}) {
    this.context_id = params.context_id || `ocp-${randomBytes(4).toString('hex')}`;
    this.agent_type = params.agent_type !== undefined ? params.agent_type : 'generic_agent';
    this.user = params.user ?? null;
    this.workspace = params.workspace ?? null;
    this.current_file = params.current_file ?? null;
    this.history = params.history || [];
    this.current_goal = params.current_goal ?? null;
    this.context_summary = params.context_summary ?? null;
    this.error_context = params.error_context ?? null;
    this.recent_changes = params.recent_changes || [];
    this.api_specs = params.api_specs || {};
    this.created_at = params.created_at || new Date();
    this.last_updated = params.last_updated || new Date();

    // Initialize session
    this.session = params.session || {
      start_time: this.created_at.toISOString(),
      interaction_count: 0,
      agent_type: this.agent_type,
    };
  }

  /**
   * Update the agent's current goal and context summary
   */
  updateGoal(goal: string, summary?: string): void {
    this.current_goal = goal;
    if (summary) {
      this.context_summary = summary;
    }
    this.last_updated = new Date();
    this.session.interaction_count = (this.session.interaction_count || 0) + 1;
  }

  /**
   * Add an interaction to the conversation history
   */
  addInteraction(
    action: string,
    apiEndpoint?: string | null,
    result?: string | null,
    metadata?: Record<string, any>
  ): void {
    const interaction = {
      timestamp: new Date().toISOString(),
      action,
      api_endpoint: apiEndpoint ?? null,
      result: result ?? null,
      metadata: metadata || {},
    };
    this.history.push(interaction);
    this.last_updated = new Date();
  }

  /**
   * Set error context for debugging scenarios
   */
  setErrorContext(error: string, filePath?: string): void {
    this.error_context = error;
    if (filePath) {
      this.current_file = filePath;
    }
    this.last_updated = new Date();
  }

  /**
   * Add a recent change to track modifications
   */
  addRecentChange(change: string): void {
    this.recent_changes.push(change);
    // Keep only last 10 changes
    if (this.recent_changes.length > 10) {
      this.recent_changes = this.recent_changes.slice(-10);
    }
    this.last_updated = new Date();
  }

  /**
   * Add an API specification for enhanced responses
   */
  addApiSpec(apiName: string, openapiUrl: string): void {
    this.api_specs[apiName] = openapiUrl;
    this.last_updated = new Date();
  }

  /**
   * Convert context to dictionary for serialization
   */
  toDict(): OCPContextDict {
    return {
      context_id: this.context_id,
      agent_type: this.agent_type,
      user: this.user,
      workspace: this.workspace,
      current_file: this.current_file,
      session: this.session,
      history: this.history,
      current_goal: this.current_goal,
      context_summary: this.context_summary,
      error_context: this.error_context,
      recent_changes: this.recent_changes,
      api_specs: this.api_specs,
      created_at: this.created_at.toISOString(),
      last_updated: this.last_updated.toISOString(),
    };
  }

  /**
   * Create AgentContext from dictionary
   */
  static fromDict(data: Record<string, any>): AgentContext {
    // Convert ISO strings back to Date objects
    const created_at = data.created_at
      ? new Date(data.created_at.replace('Z', '+00:00'))
      : undefined;
    const last_updated = data.last_updated
      ? new Date(data.last_updated.replace('Z', '+00:00'))
      : undefined;

    return new AgentContext({
      ...data,
      created_at,
      last_updated,
    });
  }

  /**
   * Get a summary of the conversation for API context
   */
  getConversationSummary(): string {
    const summaryParts: string[] = [];

    if (this.current_goal) {
      summaryParts.push(`Goal: ${this.current_goal}`);
    }

    if (this.error_context) {
      summaryParts.push(`Error: ${this.error_context}`);
    }

    if (this.current_file) {
      summaryParts.push(`Working on: ${this.current_file}`);
    }

    if (this.recent_changes.length > 0) {
      summaryParts.push(`Recent changes: ${this.recent_changes.slice(-3).join(', ')}`);
    }

    if (this.history.length > 0) {
      const recentActions = this.history.slice(-3).map(h => h.action);
      summaryParts.push(`Recent actions: ${recentActions.join(', ')}`);
    }

    return summaryParts.length > 0 ? summaryParts.join(' | ') : 'New conversation';
  }

  /**
   * Create a copy of this context for forked workflows
   */
  clone(): AgentContext {
    const data = this.toDict();
    data.context_id = `ocp-${randomBytes(4).toString('hex')}`; // New ID for clone
    return AgentContext.fromDict(data);
  }

  /**
   * Convenience method to convert context to OCP headers
   */
  toHeaders(compress: boolean = true): Record<string, string> {
    return createOCPHeaders(this, undefined, compress);
  }

  /**
   * Convenience method to update context from HTTP response headers
   */
  updateFromHeaders(headers: Record<string, string> | Headers | any): boolean {
    // Try parseContext which handles multiple header types
    const newContext = parseContext(headers);
    
    if (newContext) {
      // Update current context with relevant fields from response
      // Keep our identity but update session and goal info
      if (newContext.current_goal && newContext.current_goal !== this.current_goal) {
        this.current_goal = newContext.current_goal;
      }
      if (newContext.context_summary) {
        this.context_summary = newContext.context_summary;
      }
      if (newContext.history && newContext.history.length > 0) {
        // Merge histories, avoiding duplicates
        const existingIds = new Set(
          this.history.map(h => h.interaction_id).filter(id => id !== undefined)
        );
        for (const interaction of newContext.history) {
          if (!existingIds.has(interaction.interaction_id)) {
            this.history.push(interaction);
          }
        }
      }
      // Update timestamp
      this.last_updated = new Date();
      return true;
    }
    return false;
  }
}
