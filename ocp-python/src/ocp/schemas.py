"""
Schema Validation - JSON schema validation for OCP context objects.

Validates agent contexts against the OCP specification schemas.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from .context import AgentContext


# OCP Context Schema (embedded for now, could be loaded from files)
OCP_CONTEXT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2019-09/schema",
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
            "enum": [
                "generic_agent",
                "ide_copilot", 
                "debug_assistant",
                "devops_agent",
                "customer_support",
                "code_reviewer",
                "api_tester"
            ],
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
                "start_time": {"type": "string", "format": "date-time"},
                "interaction_count": {"type": "integer", "minimum": 0},
                "agent_type": {"type": "string"}
            },
            "additionalProperties": True
        },
        "history": {
            "type": "array",
            "items": {
                "type": "object", 
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time"},
                    "action": {"type": "string"},
                    "api_endpoint": {"type": ["string", "null"]},
                    "result": {"type": ["string", "null"]},
                    "metadata": {"type": "object"}
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
            "items": {"type": "string"},
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
    "additionalProperties": False
}


class ValidationResult:
    """Result of schema validation."""
    
    def __init__(self, valid: bool, errors: Optional[List[str]] = None):
        self.valid = valid
        self.errors = errors or []
    
    def __bool__(self) -> bool:
        return self.valid
    
    def __str__(self) -> str:
        if self.valid:
            return "Valid OCP context"
        return f"Invalid OCP context: {'; '.join(self.errors)}"


def validate_context(context: AgentContext) -> ValidationResult:
    """
    Validate an AgentContext against the OCP schema.
    
    Args:
        context: AgentContext to validate
        
    Returns:
        ValidationResult with validation status and errors
    """
    if not JSONSCHEMA_AVAILABLE:
        # Basic validation without jsonschema
        return _basic_validation(context)
    
    try:
        context_dict = context.to_dict()
        validate(context_dict, OCP_CONTEXT_SCHEMA)
        return ValidationResult(True)
    
    except ValidationError as e:
        return ValidationResult(False, [str(e)])
    except Exception as e:
        return ValidationResult(False, [f"Validation error: {str(e)}"])


def validate_context_dict(context_dict: Dict[str, Any]) -> ValidationResult:
    """
    Validate a context dictionary against the OCP schema.
    
    Args:
        context_dict: Context data as dictionary
        
    Returns:
        ValidationResult with validation status and errors
    """
    if not JSONSCHEMA_AVAILABLE:
        return _basic_dict_validation(context_dict)
    
    try:
        validate(context_dict, OCP_CONTEXT_SCHEMA)
        return ValidationResult(True)
    
    except ValidationError as e:
        return ValidationResult(False, [str(e)])
    except Exception as e:
        return ValidationResult(False, [f"Validation error: {str(e)}"])


def _basic_validation(context: AgentContext) -> ValidationResult:
    """Basic validation without jsonschema library."""
    errors = []
    
    # Check required fields
    if not context.context_id:
        errors.append("context_id is required")
    elif not context.context_id.startswith("ocp-"):
        errors.append("context_id must start with 'ocp-'")
    
    if not context.agent_type:
        errors.append("agent_type is required")
    
    if not isinstance(context.session, dict):
        errors.append("session must be a dictionary")
    
    if not isinstance(context.history, list):
        errors.append("history must be a list")
    
    if not isinstance(context.api_specs, dict):
        errors.append("api_specs must be a dictionary")
    
    # Check history items
    for i, item in enumerate(context.history):
        if not isinstance(item, dict):
            errors.append(f"history[{i}] must be a dictionary")
            continue
        
        if "timestamp" not in item:
            errors.append(f"history[{i}] missing required 'timestamp' field")
        
        if "action" not in item:
            errors.append(f"history[{i}] missing required 'action' field")
    
    return ValidationResult(len(errors) == 0, errors)


def _basic_dict_validation(context_dict: Dict[str, Any]) -> ValidationResult:
    """Basic dictionary validation without jsonschema library."""
    errors = []
    
    # Check required fields
    required_fields = [
        "context_id", "agent_type", "session", "history", 
        "api_specs", "created_at", "last_updated"
    ]
    
    for field in required_fields:
        if field not in context_dict:
            errors.append(f"Missing required field: {field}")
    
    # Check context_id format
    if "context_id" in context_dict:
        context_id = context_dict["context_id"]
        if not isinstance(context_id, str) or not context_id.startswith("ocp-"):
            errors.append("context_id must be a string starting with 'ocp-'")
    
    # Check types
    if "session" in context_dict and not isinstance(context_dict["session"], dict):
        errors.append("session must be an object")
    
    if "history" in context_dict and not isinstance(context_dict["history"], list):
        errors.append("history must be an array")
    
    if "api_specs" in context_dict and not isinstance(context_dict["api_specs"], dict):
        errors.append("api_specs must be an object")
    
    return ValidationResult(len(errors) == 0, errors)


def get_schema() -> Dict[str, Any]:
    """
    Get the OCP context JSON schema.
    
    Returns:
        JSON schema dictionary
    """
    return OCP_CONTEXT_SCHEMA.copy()


def is_valid_agent_type(agent_type: str) -> bool:
    """
    Check if an agent type is valid according to the schema.
    
    Args:
        agent_type: Agent type string to validate
        
    Returns:
        True if agent type is valid
    """
    valid_types = OCP_CONTEXT_SCHEMA["properties"]["agent_type"]["enum"]
    return agent_type in valid_types


def get_valid_agent_types() -> List[str]:
    """
    Get list of valid agent types.
    
    Returns:
        List of valid agent type strings
    """
    return OCP_CONTEXT_SCHEMA["properties"]["agent_type"]["enum"].copy()


def validate_and_fix_context(context: AgentContext) -> tuple[AgentContext, ValidationResult]:
    """
    Validate context and attempt to fix common issues.
    
    Args:
        context: AgentContext to validate and fix
        
    Returns:
        Tuple of (possibly_fixed_context, validation_result)
    """
    # Make a copy to avoid modifying original
    fixed_context = AgentContext.from_dict(context.to_dict())
    
    # Fix common issues
    if not fixed_context.context_id.startswith("ocp-"):
        fixed_context.context_id = f"ocp-{fixed_context.context_id}"
    
    if fixed_context.agent_type not in get_valid_agent_types():
        fixed_context.agent_type = "generic_agent"
    
    # Ensure required collections exist
    if not isinstance(fixed_context.session, dict):
        fixed_context.session = {}
    
    if not isinstance(fixed_context.history, list):
        fixed_context.history = []
    
    if not isinstance(fixed_context.api_specs, dict):
        fixed_context.api_specs = {}
    
    # Validate the fixed context
    result = validate_context(fixed_context)
    
    return fixed_context, result