/**
 * OCP Error Hierarchy
 * 
 * Consistent error handling for the Open Context Protocol library.
 * Provides specific exception types for different failure scenarios.
 */

/**
 * Base exception for all OCP-related errors
 */
export class OCPError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'OCPError';
  }
}

/**
 * Registry service is unreachable or returned an error
 */
export class RegistryUnavailable extends OCPError {
  public registryUrl: string;

  constructor(
    registryUrl: string,
    message?: string
  ) {
    const fullMessage = message 
      ? `Registry unavailable at ${registryUrl}: ${message}`
      : `Registry unavailable at ${registryUrl}. Use spec_url for direct discovery.`;
    super(fullMessage);
    this.name = 'RegistryUnavailable';
    this.registryUrl = registryUrl;
  }
}

/**
 * API not found in the registry
 */
export class APINotFound extends OCPError {
  public suggestions: string[];

  constructor(
    public apiName: string,
    suggestions?: string[]
  ) {
    const suggestionList = suggestions || [];
    let message = `API '${apiName}' not found in registry`;
    if (suggestionList.length > 0) {
      message += `. Did you mean: ${suggestionList.slice(0, 3).join(', ')}?`;
    }
    super(message);
    this.name = 'APINotFound';
    this.suggestions = suggestionList;
  }
}

/**
 * OpenAPI schema discovery and parsing errors
 */
export class SchemaDiscoveryError extends OCPError {
  constructor(message: string) {
    super(message);
    this.name = 'SchemaDiscoveryError';
  }
}

/**
 * Context or parameter validation errors
 */
export class ValidationError extends OCPError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}
