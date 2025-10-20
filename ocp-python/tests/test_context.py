"""
Tests for AgentContext class functionality.
"""

import pytest
import json
from datetime import datetime, timezone
from ocp.context import AgentContext


class TestAgentContextCreation:
    """Test AgentContext creation and initialization."""
    
    def test_minimal_context_creation(self):
        """Test creating context with minimal parameters."""
        context = AgentContext(agent_type="test_agent")
        
        assert context.agent_type == "test_agent"
        assert context.context_id.startswith("ocp-")
        assert len(context.context_id) > 8  # ocp- + at least 8 chars
        assert isinstance(context.session, dict)
        assert isinstance(context.history, list)
        assert isinstance(context.api_specs, dict)
        assert context.created_at is not None
        assert context.last_updated is not None
    
    def test_full_context_creation(self):
        """Test creating context with all parameters."""
        context = AgentContext(
            agent_type="ide_copilot",
            user="alice",
            workspace="my-project",
            current_file="main.py",
            current_goal="debug_issue"
        )
        
        assert context.agent_type == "ide_copilot"
        assert context.user == "alice"
        assert context.workspace == "my-project"
        assert context.current_file == "main.py"
        assert context.current_goal == "debug_issue"
    
    def test_session_initialization(self):
        """Test that session is properly initialized."""
        context = AgentContext(agent_type="test_agent")
        
        assert "start_time" in context.session
        assert "interaction_count" in context.session
        assert "agent_type" in context.session
        assert context.session["agent_type"] == "test_agent"
        assert context.session["interaction_count"] == 0


class TestAgentContextUpdates:
    """Test AgentContext update functionality."""
    
    def test_update_goal(self, minimal_context):
        """Test updating agent goal."""
        original_count = minimal_context.session["interaction_count"]
        
        minimal_context.update_goal("new_goal", "new summary")
        
        assert minimal_context.current_goal == "new_goal"
        assert minimal_context.context_summary == "new summary"
        assert minimal_context.session["interaction_count"] == original_count + 1
    
    def test_add_interaction(self, minimal_context):
        """Test adding interaction to history."""
        minimal_context.add_interaction(
            "test_action",
            "test_endpoint",
            "test_result",
            {"key": "value"}
        )
        
        assert len(minimal_context.history) == 1
        interaction = minimal_context.history[0]
        
        assert interaction["action"] == "test_action"
        assert interaction["api_endpoint"] == "test_endpoint"
        assert interaction["result"] == "test_result"
        assert interaction["metadata"]["key"] == "value"
        assert "timestamp" in interaction
    
    def test_set_error_context(self, minimal_context):
        """Test setting error context."""
        minimal_context.set_error_context("Test error", "error_file.py")
        
        assert minimal_context.error_context == "Test error"
        assert minimal_context.current_file == "error_file.py"
    
    def test_add_recent_change(self, minimal_context):
        """Test adding recent changes."""
        minimal_context.add_recent_change("change 1")
        minimal_context.add_recent_change("change 2")
        
        assert len(minimal_context.recent_changes) == 2
        assert "change 1" in minimal_context.recent_changes
        assert "change 2" in minimal_context.recent_changes
    
    def test_recent_changes_limit(self, minimal_context):
        """Test that recent changes are limited to 10 items."""
        # Add 15 changes
        for i in range(15):
            minimal_context.add_recent_change(f"change {i}")
        
        # Should only keep last 10
        assert len(minimal_context.recent_changes) == 10
        assert minimal_context.recent_changes[0] == "change 5"  # First kept change
        assert minimal_context.recent_changes[-1] == "change 14"  # Last change
    
    def test_add_api_spec(self, minimal_context):
        """Test adding API specification."""
        minimal_context.add_api_spec("github", "https://api.github.com")
        
        assert "github" in minimal_context.api_specs
        assert minimal_context.api_specs["github"] == "https://api.github.com"


class TestAgentContextSerialization:
    """Test AgentContext serialization and deserialization."""
    
    def test_to_dict(self, sample_context):
        """Test converting context to dictionary."""
        data = sample_context.to_dict()
        
        assert isinstance(data, dict)
        assert data["context_id"] == sample_context.context_id
        assert data["agent_type"] == sample_context.agent_type
        assert data["user"] == sample_context.user
        assert isinstance(data["created_at"], str)
        assert isinstance(data["last_updated"], str)
    
    def test_from_dict(self, sample_context):
        """Test creating context from dictionary."""
        data = sample_context.to_dict()
        restored_context = AgentContext.from_dict(data)
        
        assert restored_context.context_id == sample_context.context_id
        assert restored_context.agent_type == sample_context.agent_type
        assert restored_context.user == sample_context.user
        assert restored_context.workspace == sample_context.workspace
        assert len(restored_context.history) == len(sample_context.history)
    
    def test_json_roundtrip(self, sample_context):
        """Test JSON serialization roundtrip."""
        # Convert to JSON and back
        json_data = json.dumps(sample_context.to_dict())
        parsed_data = json.loads(json_data)
        restored_context = AgentContext.from_dict(parsed_data)
        
        assert restored_context.context_id == sample_context.context_id
        assert restored_context.current_goal == sample_context.current_goal
        assert len(restored_context.history) == len(sample_context.history)


class TestAgentContextUtilities:
    """Test utility methods of AgentContext."""
    
    def test_get_conversation_summary(self, complex_context):
        """Test conversation summary generation."""
        summary = complex_context.get_conversation_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Goal:" in summary  # Should include goal
        assert "Error:" in summary  # Should include error context
        assert "Working on:" in summary  # Should include current file
    
    def test_conversation_summary_minimal(self, minimal_context):
        """Test conversation summary with minimal context."""
        summary = minimal_context.get_conversation_summary()
        
        assert summary == "New conversation"
    
    def test_clone_context(self, sample_context):
        """Test cloning context."""
        cloned = sample_context.clone()
        
        # Should have different ID
        assert cloned.context_id != sample_context.context_id
        assert cloned.context_id.startswith("ocp-")
        
        # But same data
        assert cloned.agent_type == sample_context.agent_type
        assert cloned.user == sample_context.user
        assert cloned.workspace == sample_context.workspace
        assert len(cloned.history) == len(sample_context.history)


class TestAgentContextEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_agent_type(self):
        """Test behavior with empty agent type."""
        # Should still work, though not recommended
        context = AgentContext(agent_type="")
        assert context.agent_type == ""
        assert context.context_id.startswith("ocp-")
    
    def test_none_values(self):
        """Test handling of None values."""
        context = AgentContext(
            agent_type="test",
            user=None,
            workspace=None,
            current_file=None
        )
        
        assert context.user is None
        assert context.workspace is None
        assert context.current_file is None
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        context = AgentContext(
            agent_type="test",
            user="用户",  # Chinese characters
            workspace="проект",  # Cyrillic characters
            current_file="файл.py"
        )
        
        # Should serialize/deserialize properly
        data = context.to_dict()
        restored = AgentContext.from_dict(data)
        
        assert restored.user == "用户"
        assert restored.workspace == "проект"
        assert restored.current_file == "файл.py"