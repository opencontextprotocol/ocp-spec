"""
Tests for OCP validation functionality.
"""

import pytest
from datetime import datetime, timezone
from ocp_agent.validation import (
    validate_context,
    validate_context_dict,
    ValidationResult,
    get_schema,
    validate_and_fix_context,
    OCP_CONTEXT_SCHEMA
)
from ocp_agent.context import AgentContext


class TestValidationResult:
    """Test ValidationResult class functionality."""
    
    def test_valid_result(self):
        """Test valid ValidationResult."""
        result = ValidationResult(True)
        assert result.valid is True
        assert result.errors == []
        assert bool(result) is True
        assert str(result) == "Valid OCP context"
    
    def test_invalid_result(self):
        """Test invalid ValidationResult."""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(False, errors)
        assert result.valid is False
        assert result.errors == errors
        assert bool(result) is False
        assert str(result) == "Invalid OCP context: Error 1; Error 2"
    
    def test_invalid_result_no_errors(self):
        """Test invalid result with no specific errors."""
        result = ValidationResult(False)
        assert result.valid is False
        assert result.errors == []
        assert str(result) == "Invalid OCP context: "


class TestContextValidation:
    """Test AgentContext validation."""
    
    def test_validate_valid_context(self):
        """Test validation of a valid context."""
        context = AgentContext(
            agent_type="ide_copilot",
            user="test_user",
            workspace="test_workspace",
            current_goal="test_goal"
        )
        
        result = validate_context(context)
        assert result.valid is True
        assert result.errors == []
    
    def test_validate_minimal_context(self):
        """Test validation of minimal valid context."""
        context = AgentContext(agent_type="generic_agent")
        
        result = validate_context(context)
        assert result.valid is True
    
    def test_validate_context_with_custom_agent_type(self):
        """Test validation with custom agent type (should be valid)."""
        context = AgentContext(agent_type="custom_agent")
        
        result = validate_context(context)
        # Should be valid since any string is allowed
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_validate_context_missing_agent_type(self):
        """Test validation with missing agent type."""
        context = AgentContext(agent_type="")
        
        result = validate_context(context)
        # Empty string should still be valid if the schema allows it
        # The schema now just requires type: string, not specific values
        assert result.valid is True
    
    def test_validate_context_with_all_fields(self):
        """Test validation with all possible fields filled."""
        context = AgentContext(
            agent_type="ide_copilot",
            user="developer",
            workspace="/home/user/project",
            current_file="main.py",
            current_goal="debug error",
            context_summary="Working on bug fix",
            error_context="NullPointerException at line 42"
        )
        
        # Add some history and changes
        context.add_interaction("tool_call", "https://api.test.com", "success")
        context.add_recent_change("Modified main.py")
        context.add_api_spec("test_api", "https://api.test.com/openapi.json")
        
        result = validate_context(context)
        assert result.valid is True


class TestDictValidation:
    """Test dictionary-based validation."""
    
    def test_validate_valid_dict(self):
        """Test validation of valid context dictionary."""
        context_dict = {
            "context_id": "ocp-12345678",
            "agent_type": "ide_copilot",
            "user": "test_user",
            "workspace": "test_workspace",
            "current_file": None,
            "session": {
                "start_time": "2024-01-01T00:00:00Z",
                "interaction_count": 0,
                "agent_type": "ide_copilot"
            },
            "history": [],
            "current_goal": "test_goal",
            "context_summary": None,
            "error_context": None,
            "recent_changes": [],
            "api_specs": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        result = validate_context_dict(context_dict)
        assert result.valid is True
    
    def test_validate_minimal_dict(self):
        """Test validation of minimal dictionary."""
        context_dict = {
            "context_id": "ocp-abcd1234",
            "agent_type": "generic_agent",
            "user": None,
            "workspace": None,
            "current_file": None,
            "session": {
                "start_time": "2024-01-01T00:00:00Z",
                "interaction_count": 0,
                "agent_type": "generic_agent"
            },
            "history": [],
            "current_goal": None,
            "context_summary": None,
            "error_context": None,
            "recent_changes": [],
            "api_specs": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        result = validate_context_dict(context_dict)
        assert result.valid is True
    
    def test_validate_invalid_context_id(self):
        """Test validation with invalid context ID format."""
        context_dict = {
            "context_id": "invalid-id",
            "agent_type": "generic_agent"
        }
        
        result = validate_context_dict(context_dict)
        assert result.valid is False
        assert any("context_id" in error for error in result.errors)
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        context_dict = {}
        
        result = validate_context_dict(context_dict)
        assert result.valid is False
        assert len(result.errors) > 0


class TestSchemaUtilities:
    """Test schema utility functions."""
    
    def test_get_schema(self):
        """Test getting the OCP context schema."""
        schema = get_schema()
        assert isinstance(schema, dict)
        assert schema["$id"] == "https://opencontextprotocol.org/schemas/ocp-context.json"
        assert schema["title"] == "OCP Context Object"
        assert "properties" in schema
        assert "agent_type" in schema["properties"]
    


class TestValidateAndFix:
    """Test validation and fixing functionality."""
    
    def test_validate_and_fix_valid_context(self):
        """Test validate and fix with valid context."""
        context = AgentContext(
            agent_type="ide_copilot",
            user="test_user"
        )
        
        fixed_context, result = validate_and_fix_context(context)
        assert result.valid is True
        assert fixed_context.agent_type == "ide_copilot"
        assert fixed_context.user == "test_user"
    
    def test_validate_and_fix_custom_agent_type(self):
        """Test validate and fix with custom agent type (should be preserved)."""
        context = AgentContext(agent_type="custom_type")
        
        fixed_context, result = validate_and_fix_context(context)
        assert result.valid is True
        assert fixed_context.agent_type == "custom_type"  # Should be preserved
    
    def test_validate_and_fix_preserves_other_data(self):
        """Test that fixing preserves other context data."""
        context = AgentContext(
            agent_type="my_custom_agent",
            user="test_user",
            workspace="test_workspace",
            current_goal="test_goal"
        )
        
        # Add some data
        context.add_interaction("test", "endpoint", "result")
        context.add_recent_change("change1")
        
        fixed_context, result = validate_and_fix_context(context)
        assert result.valid is True
        assert fixed_context.agent_type == "my_custom_agent"  # Should be preserved
        assert fixed_context.user == "test_user"
        assert fixed_context.workspace == "test_workspace"
        assert fixed_context.current_goal == "test_goal"
        assert len(fixed_context.history) == 1
        assert len(fixed_context.recent_changes) == 1


class TestSchemaConstants:
    """Test schema constants and structure."""
    
    def test_ocp_context_schema_structure(self):
        """Test OCP context schema structure."""
        assert isinstance(OCP_CONTEXT_SCHEMA, dict)
        assert "$schema" in OCP_CONTEXT_SCHEMA
        assert "$id" in OCP_CONTEXT_SCHEMA
        assert "properties" in OCP_CONTEXT_SCHEMA
        
        properties = OCP_CONTEXT_SCHEMA["properties"]
        required_fields = ["context_id", "agent_type"]
        
        for field in required_fields:
            assert field in properties
    
    def test_agent_type_schema_structure(self):
        """Test agent type schema structure (should be free-form string)."""
        agent_type_prop = OCP_CONTEXT_SCHEMA["properties"]["agent_type"]
        assert "type" in agent_type_prop
        assert agent_type_prop["type"] == "string"
        assert "description" in agent_type_prop
        # Should not have enum constraint anymore
        assert "enum" not in agent_type_prop


class TestValidationEdgeCases:
    """Test validation edge cases and error conditions."""
    
    def test_validate_context_none(self):
        """Test validation with None context."""
        # None context should return validation error, not raise exception
        result = validate_context(None)
        assert result.valid is False
        assert len(result.errors) > 0
    
    def test_validate_dict_none(self):
        """Test validation with None dictionary."""
        result = validate_context_dict(None)
        assert result.valid is False
        assert len(result.errors) > 0
    
    def test_validate_dict_invalid_type(self):
        """Test validation with non-dictionary input."""
        result = validate_context_dict("not a dict")
        assert result.valid is False
    
    def test_context_with_unicode_data(self):
        """Test validation with Unicode data."""
        context = AgentContext(
            agent_type="ide_copilot",
            user="用户",  # Chinese
            workspace="проект",  # Cyrillic  
            current_goal="修复错误"  # Chinese
        )
        
        result = validate_context(context)
        assert result.valid is True
    
    def test_context_with_very_long_strings(self):
        """Test validation with very long strings."""
        long_string = "x" * 10000
        context = AgentContext(
            agent_type="ide_copilot",
            user=long_string,
            workspace=long_string,
            current_goal=long_string
        )
        
        result = validate_context(context)
        assert result.valid is True