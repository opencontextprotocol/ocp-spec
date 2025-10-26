"""
Shared test fixtures and configuration for OCP tests.
"""

import pytest
import json
from datetime import datetime, timezone
from ocp_agent import AgentContext


@pytest.fixture
def sample_context():
    """Create a sample AgentContext for testing."""
    context = AgentContext(
        agent_type="test_agent",
        user="test_user",
        workspace="test_workspace",
        current_file="test_file.py"
    )
    context.update_goal("test_goal", "Testing OCP functionality")
    context.add_interaction("test_action", "test_endpoint", "test_result")
    return context


@pytest.fixture
def minimal_context():
    """Create a minimal AgentContext for testing."""
    return AgentContext(agent_type="minimal_agent")


@pytest.fixture
def complex_context():
    """Create a complex AgentContext with lots of data."""
    context = AgentContext(
        agent_type="complex_agent",
        user="complex_user",
        workspace="complex_workspace",
        current_file="complex_file.py"
    )
    
    # Add multiple interactions
    for i in range(5):
        context.add_interaction(
            f"action_{i}",
            f"endpoint_{i}",
            f"result_{i}",
            metadata={"step": i}
        )
    
    # Add recent changes
    for i in range(3):
        context.add_recent_change(f"change_{i}")
    
    # Add API specs
    context.add_api_spec("github", "https://api.github.com")
    context.add_api_spec("stripe", "https://api.stripe.com")
    
    # Set error context
    context.set_error_context("Test error message", "error_file.py")
    
    # Set goal
    context.update_goal("complex_testing", "Testing complex context functionality")
    
    return context


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response object."""
    class MockResponse:
        def __init__(self, status_code=200, headers=None, text=""):
            self.status_code = status_code
            self.headers = headers or {}
            self.text = text
        
        def json(self):
            if self.text:
                return json.loads(self.text)
            return {}
    
    return MockResponse


@pytest.fixture
def github_token():
    """Get GitHub token from environment for integration tests."""
    import os
    return os.getenv("GITHUB_TOKEN")


@pytest.fixture
def sample_api_response():
    """Sample API response data for testing."""
    return {
        "message": "Hello from API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"key": "value"}
    }