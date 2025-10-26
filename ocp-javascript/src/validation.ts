/**
 * Schema Validation - JSON schema validation for OCP context objects.
 * 
 * Validates agent contexts against the OCP specification schemas.
 */

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { AgentContext } from './context.js';
import { randomBytes } from 'crypto';

// OCP Context Schema (embedded for now, could be loaded from files)
export const OCP_CONTEXT_SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://opencontextprotocol.org/schemas/ocp-context.json",
  "title": "OCP Context Object",
  "description": "Agent context for Open Context Protocol",
  "type": "object",
  "properties": {
    "context_id": {
      "type": "string",
      "pattern": "^ocp-[a-f0-9]{8,}$",
      "description": "Unique identifier for this context"
    },
    "agent_type": {
      "type": "string",
      "description": "Type of agent creating this context"
    },
    "user": {
      "type": ["string", "null"],
      "description": "User identifier"
    },
    "workspace": {
      "type": ["string", "null"],
      "description": "Current workspace or project"
    },
    "current_file": {
      "type": ["string", "null"],
      "description": "Currently active file"
    },
    "session": {
      "type": "object",
      "properties": {
        "start_time": { "type": "string", "format": "date-time" },
        "interaction_count": { "type": "integer", "minimum": 0 },
        "agent_type": { "type": "string" }
      },
      "additionalProperties": true
    },
    "history": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "timestamp": { "type": "string", "format": "date-time" },
          "action": { "type": "string" },
          "api_endpoint": { "type": ["string", "null"] },
          "result": { "type": ["string", "null"] },
          "metadata": { "type": "object" }
        },
        "required": ["timestamp", "action"]
      }
    },
    "current_goal": {
      "type": ["string", "null"],
      "description": "Agent's current objective"
    },
    "context_summary": {
      "type": ["string", "null"],
      "description": "Brief summary of conversation context"
    },
    "error_context": {
      "type": ["string", "null"],
      "description": "Error information for debugging"
    },
    "recent_changes": {
      "type": "array",
      "items": { "type": "string" },
      "maxItems": 20,
      "description": "Recent changes or modifications"
    },
    "api_specs": {
      "type": "object",
      "patternProperties": {
        "^[a-zA-Z0-9_-]+$": {
          "type": "string",
          "format": "uri"
        }
      },
      "description": "API specifications for enhanced responses"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": [
    "context_id",
    "agent_type",
    "session",
    "history",
    "api_specs",
    "created_at",
    "last_updated"
  ],
  "additionalProperties": false
};

// Create and configure Ajv instance
const ajv = new Ajv({
  allErrors: true,
  verbose: true,
  strict: false,
});
addFormats(ajv);

// Compile the schema
const validateSchema = ajv.compile(OCP_CONTEXT_SCHEMA);

/**
 * Result of schema validation
 */
export class ValidationResult {
  constructor(
    public valid: boolean,
    public errors: string[] = []
  ) {}

  valueOf(): boolean {
    return this.valid;
  }

  toString(): string {
    if (this.valid) {
      return 'Valid OCP context';
    }
    return `Invalid OCP context: ${this.errors.join('; ')}`;
  }
}

/**
 * Validate an AgentContext against the OCP schema
 */
export function validateContext(context: AgentContext): ValidationResult {
  try {
    const contextDict = context.toDict();
    return validateContextDict(contextDict);
  } catch (e) {
    return new ValidationResult(false, [`Validation error: ${e}`]);
  }
}

/**
 * Validate a context dictionary against the OCP schema
 */
export function validateContextDict(contextDict: Record<string, any>): ValidationResult {
  try {
    const valid = validateSchema(contextDict);
    
    if (valid) {
      return new ValidationResult(true);
    }
    
    const errors = (validateSchema.errors || []).map(err => {
      return err.message || 'unknown error';
    });
    
    return new ValidationResult(false, errors);
  } catch (e) {
    return new ValidationResult(false, [`Validation error: ${e}`]);
  }
}

/**
 * Get the OCP context JSON schema
 */
export function getSchema(): Record<string, any> {
  return { ...OCP_CONTEXT_SCHEMA };
}

/**
 * Validate and attempt to fix a context object
 */
export function validateAndFixContext(context: AgentContext): [AgentContext, ValidationResult] {
  // Make a copy to avoid modifying original
  const fixed = AgentContext.fromDict(context.toDict());
  
  // Fix common issues
  if (!fixed.context_id.startsWith('ocp-')) {
    fixed.context_id = `ocp-${fixed.context_id}`;
  }
  
  // Ensure required collections exist
  if (typeof fixed.session !== 'object' || fixed.session === null) {
    fixed.session = {};
  }
  
  if (!Array.isArray(fixed.history)) {
    fixed.history = [];
  }
  
  if (typeof fixed.api_specs !== 'object' || fixed.api_specs === null) {
    fixed.api_specs = {};
  }
  
  // Validate the fixed context
  const result = validateContext(fixed);
  
  return [fixed, result];
}
