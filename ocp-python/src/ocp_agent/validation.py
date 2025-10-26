"""
Schema Validation - JSON schema validation for OCP context objects.

Validates agent contexts against the OCP specification schemas.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from jsonschema import validate, ValidationError, Draft7Validator

from .context import AgentContext


# OCP Context Schema (embedded for now, could be loaded from files)
OCP_CONTEXT_SCHEMA = {
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
    try:
        validate(context_dict, OCP_CONTEXT_SCHEMA)
        return ValidationResult(True)
    
    except ValidationError as e:
        return ValidationResult(False, [str(e)])
    except Exception as e:
        return ValidationResult(False, [f"Validation error: {str(e)}"])




def get_schema() -> Dict[str, Any]:
    """
    Get the OCP context JSON schema.
    
    Returns:
        JSON schema dictionary
    """
    return OCP_CONTEXT_SCHEMA.copy()


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