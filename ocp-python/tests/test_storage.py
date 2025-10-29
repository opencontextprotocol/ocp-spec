"""
Tests for OCP Storage functionality.

Tests cover API caching and session persistence.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

from ocp_agent import OCPStorage, AgentContext, OCPAPISpec, OCPTool


class TestOCPStorageInitialization:
    """Test storage initialization and directory creation."""
    
    def test_default_initialization(self):
        """Test storage initializes with default path."""
        storage = OCPStorage()
        
        assert storage.base_path == Path.home() / ".ocp"
        assert storage.cache_dir == storage.base_path / "cache" / "apis"
        assert storage.sessions_dir == storage.base_path / "sessions"
    
    def test_custom_path_initialization(self):
        """Test storage initializes with custom path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir) / "custom_ocp"
            storage = OCPStorage(base_path=custom_path)
            
            assert storage.base_path == custom_path
            assert storage.cache_dir == custom_path / "cache" / "apis"
            assert storage.sessions_dir == custom_path / "sessions"
    
    def test_directory_creation(self):
        """Test storage creates directories on init."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = OCPStorage(base_path=Path(tmpdir) / "test_ocp")
            
            assert storage.cache_dir.exists()
            assert storage.sessions_dir.exists()


class TestAPICaching:
    """Test API specification caching."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield OCPStorage(base_path=Path(tmpdir) / "test_ocp")
    
    @pytest.fixture
    def sample_api_spec(self):
        """Sample API spec for testing."""
        return OCPAPISpec(
            title="Test API",
            version="1.0.0",
            base_url="https://api.test.com",
            description="A test API",
            raw_spec={"openapi": "3.0.0"},
            tools=[
                OCPTool(
                    name="get_items",
                    description="Get all items",
                    method="GET",
                    path="/items",
                    parameters={},
                    response_schema={"type": "array"}
                )
            ]
        )
    
    def test_cache_api_success(self, temp_storage, sample_api_spec):
        """Test successfully caching an API."""
        result = temp_storage.cache_api("test_api", sample_api_spec)
        
        assert result is True
        cache_file = temp_storage.cache_dir / "test_api.json"
        assert cache_file.exists()
        
        # Verify file content
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        assert data["api_name"] == "test_api"
        assert data["title"] == "Test API"
        assert data["version"] == "1.0.0"
        assert data["base_url"] == "https://api.test.com"
        assert "cached_at" in data
        assert len(data["tools"]) == 1
    
    def test_cache_api_with_metadata(self, temp_storage, sample_api_spec):
        """Test caching API with metadata."""
        metadata = {"source": "registry", "custom_field": "value"}
        temp_storage.cache_api("test_api", sample_api_spec, metadata=metadata)
        
        cache_file = temp_storage.cache_dir / "test_api.json"
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        assert data["source"] == "registry"
        assert data["custom_field"] == "value"
    
    def test_get_cached_api_success(self, temp_storage, sample_api_spec):
        """Test retrieving cached API."""
        temp_storage.cache_api("test_api", sample_api_spec)
        
        cached = temp_storage.get_cached_api("test_api")
        
        assert cached is not None
        assert cached.title == "Test API"
        assert cached.version == "1.0.0"
        assert cached.base_url == "https://api.test.com"
        assert len(cached.tools) == 1
        assert cached.tools[0].name == "get_items"
    
    def test_get_cached_api_not_found(self, temp_storage):
        """Test retrieving non-existent cached API."""
        cached = temp_storage.get_cached_api("nonexistent")
        
        assert cached is None
    
    def test_get_cached_api_with_expiration(self, temp_storage, sample_api_spec):
        """Test cache expiration logic."""
        # Cache API
        temp_storage.cache_api("test_api", sample_api_spec)
        
        # Manually set cached_at to 10 days ago
        cache_file = temp_storage.cache_dir / "test_api.json"
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        data["cached_at"] = old_date.isoformat()
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        
        # Should return None with max_age_days=7
        cached = temp_storage.get_cached_api("test_api", max_age_days=7)
        assert cached is None
        
        # Should return spec with max_age_days=14
        cached = temp_storage.get_cached_api("test_api", max_age_days=14)
        assert cached is not None
    
    def test_get_cached_api_no_expiration(self, temp_storage, sample_api_spec):
        """Test retrieving cached API without expiration check."""
        temp_storage.cache_api("test_api", sample_api_spec)
        
        # Manually set cached_at to very old date
        cache_file = temp_storage.cache_dir / "test_api.json"
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        old_date = datetime.now(timezone.utc) - timedelta(days=365)
        data["cached_at"] = old_date.isoformat()
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        
        # Should still return spec with no max_age_days
        cached = temp_storage.get_cached_api("test_api")
        assert cached is not None
    
    def test_list_cached_apis(self, temp_storage, sample_api_spec):
        """Test listing cached APIs."""
        # Cache multiple APIs
        temp_storage.cache_api("github", sample_api_spec)
        temp_storage.cache_api("stripe", sample_api_spec)
        temp_storage.cache_api("slack", sample_api_spec)
        
        apis = temp_storage.list_cached_apis()
        
        assert len(apis) == 3
        assert "github" in apis
        assert "stripe" in apis
        assert "slack" in apis
    
    def test_list_cached_apis_empty(self, temp_storage):
        """Test listing cached APIs when cache is empty."""
        apis = temp_storage.list_cached_apis()
        
        assert apis == []
    
    def test_search_cache(self, temp_storage):
        """Test searching cached APIs."""
        # Create different API specs
        github_spec = OCPAPISpec(
            title="GitHub API",
            version="1.0.0",
            base_url="https://api.github.com",
            description="GitHub REST API",
            raw_spec={},
            tools=[
                OCPTool(
                    name="list_repos",
                    description="List repositories",
                    method="GET",
                    path="/repos",
                    parameters={},
                    response_schema={}
                )
            ]
        )
        
        stripe_spec = OCPAPISpec(
            title="Stripe API",
            version="1.0.0",
            base_url="https://api.stripe.com",
            description="Stripe payment API",
            raw_spec={},
            tools=[
                OCPTool(
                    name="create_payment",
                    description="Create payment intent",
                    method="POST",
                    path="/payments",
                    parameters={},
                    response_schema={}
                )
            ]
        )
        
        temp_storage.cache_api("github", github_spec)
        temp_storage.cache_api("stripe", stripe_spec)
        
        # Search by name
        results = temp_storage.search_cache("github")
        assert len(results) == 1
        assert results[0]["name"] == "github"
        
        # Search by description
        results = temp_storage.search_cache("payment")
        assert len(results) == 1
        assert results[0]["name"] == "stripe"
        
        # Search by tool description
        results = temp_storage.search_cache("repositories")
        assert len(results) == 1
        assert results[0]["name"] == "github"
        
        # Case-insensitive search
        results = temp_storage.search_cache("GITHUB")
        assert len(results) == 1
    
    def test_clear_cache_specific(self, temp_storage, sample_api_spec):
        """Test clearing specific API from cache."""
        temp_storage.cache_api("github", sample_api_spec)
        temp_storage.cache_api("stripe", sample_api_spec)
        
        result = temp_storage.clear_cache("github")
        
        assert result is True
        assert not (temp_storage.cache_dir / "github.json").exists()
        assert (temp_storage.cache_dir / "stripe.json").exists()
    
    def test_clear_cache_all(self, temp_storage, sample_api_spec):
        """Test clearing entire cache."""
        temp_storage.cache_api("github", sample_api_spec)
        temp_storage.cache_api("stripe", sample_api_spec)
        temp_storage.cache_api("slack", sample_api_spec)
        
        result = temp_storage.clear_cache()
        
        assert result is True
        assert len(list(temp_storage.cache_dir.glob("*.json"))) == 0


class TestSessionPersistence:
    """Test session context persistence."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield OCPStorage(base_path=Path(tmpdir) / "test_ocp")
    
    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        context = AgentContext(
            agent_type="test_agent",
            user="alice",
            workspace="test_workspace",
            current_goal="test goal"
        )
        context.add_interaction("test_action", "test_endpoint", "success")
        return context
    
    def test_save_session_success(self, temp_storage, sample_context):
        """Test successfully saving a session."""
        result = temp_storage.save_session("test-session-123", sample_context)
        
        assert result is True
        session_file = temp_storage.sessions_dir / "test-session-123.json"
        assert session_file.exists()
        
        # Verify file content
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        assert data["session_id"] == "test-session-123"
        assert data["agent_type"] == "test_agent"
        assert data["user"] == "alice"
        assert data["workspace"] == "test_workspace"
    
    def test_load_session_success(self, temp_storage, sample_context):
        """Test successfully loading a session."""
        temp_storage.save_session("test-session-123", sample_context)
        
        loaded = temp_storage.load_session("test-session-123")
        
        assert loaded is not None
        assert loaded.agent_type == "test_agent"
        assert loaded.user == "alice"
        assert loaded.workspace == "test_workspace"
        assert loaded.current_goal == "test goal"
        assert len(loaded.history) == 1
    
    def test_load_session_not_found(self, temp_storage):
        """Test loading non-existent session."""
        loaded = temp_storage.load_session("nonexistent")
        
        assert loaded is None
    
    def test_session_roundtrip(self, temp_storage, sample_context):
        """Test session save and load roundtrip."""
        # Save session
        temp_storage.save_session("roundtrip-test", sample_context)
        
        # Load session
        loaded = temp_storage.load_session("roundtrip-test")
        
        # Compare
        assert loaded.context_id == sample_context.context_id
        assert loaded.agent_type == sample_context.agent_type
        assert loaded.user == sample_context.user
        assert loaded.workspace == sample_context.workspace
        assert loaded.current_goal == sample_context.current_goal
        assert len(loaded.history) == len(sample_context.history)
    
    def test_list_sessions(self, temp_storage, sample_context):
        """Test listing all sessions."""
        # Save multiple sessions
        temp_storage.save_session("session-1", sample_context)
        temp_storage.save_session("session-2", sample_context)
        temp_storage.save_session("session-3", sample_context)
        
        sessions = temp_storage.list_sessions()
        
        assert len(sessions) == 3
        assert all("id" in s for s in sessions)
        assert all("context_id" in s for s in sessions)
        assert all("agent_type" in s for s in sessions)
    
    def test_list_sessions_with_limit(self, temp_storage, sample_context):
        """Test listing sessions with limit."""
        # Save multiple sessions
        for i in range(10):
            temp_storage.save_session(f"session-{i}", sample_context)
        
        sessions = temp_storage.list_sessions(limit=5)
        
        assert len(sessions) == 5
    
    def test_list_sessions_empty(self, temp_storage):
        """Test listing sessions when none exist."""
        sessions = temp_storage.list_sessions()
        
        assert sessions == []
    
    def test_cleanup_sessions(self, temp_storage, sample_context):
        """Test cleaning up old sessions."""
        # Create 10 sessions
        for i in range(10):
            temp_storage.save_session(f"session-{i}", sample_context)
        
        # Keep only 5 most recent
        removed = temp_storage.cleanup_sessions(keep_recent=5)
        
        assert removed == 5
        remaining = list(temp_storage.sessions_dir.glob("*.json"))
        assert len(remaining) == 5
    
    def test_cleanup_sessions_keep_all(self, temp_storage, sample_context):
        """Test cleanup when keep_recent is larger than existing."""
        # Create 5 sessions
        for i in range(5):
            temp_storage.save_session(f"session-{i}", sample_context)
        
        # Keep 10 (more than exist)
        removed = temp_storage.cleanup_sessions(keep_recent=10)
        
        assert removed == 0
        remaining = list(temp_storage.sessions_dir.glob("*.json"))
        assert len(remaining) == 5


class TestStorageErrorHandling:
    """Test storage error handling and fail-safe behavior."""
    
    def test_cache_api_invalid_path(self, sample_api_spec):
        """Test caching with invalid path doesn't crash."""
        # Create storage with read-only path (will fail on write)
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = OCPStorage(base_path=Path(tmpdir) / "test_ocp")
            
            # Make cache directory read-only
            storage.cache_dir.chmod(0o444)
            
            # Should return False but not raise
            result = storage.cache_api("test_api", sample_api_spec)
            assert result is False
            
            # Restore permissions for cleanup
            storage.cache_dir.chmod(0o755)
    
    def test_get_cached_api_corrupted_file(self, temp_storage):
        """Test retrieving corrupted cache file."""
        # Create corrupted cache file
        cache_file = temp_storage.cache_dir / "corrupted.json"
        with open(cache_file, 'w') as f:
            f.write("not valid json {{{")
        
        # Should return None, not raise
        cached = temp_storage.get_cached_api("corrupted")
        assert cached is None
    
    def test_save_session_invalid_path(self, temp_storage, sample_context):
        """Test saving session with invalid path doesn't crash."""
        # Make sessions directory read-only
        temp_storage.sessions_dir.chmod(0o444)
        
        # Should return False but not raise
        result = temp_storage.save_session("test-session", sample_context)
        assert result is False
        
        # Restore permissions
        temp_storage.sessions_dir.chmod(0o755)
    
    def test_load_session_corrupted_file(self, temp_storage):
        """Test loading corrupted session file."""
        # Create corrupted session file
        session_file = temp_storage.sessions_dir / "corrupted.json"
        with open(session_file, 'w') as f:
            f.write("not valid json {{{")
        
        # Should return None, not raise
        loaded = temp_storage.load_session("corrupted")
        assert loaded is None
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield OCPStorage(base_path=Path(tmpdir) / "test_ocp")
    
    @pytest.fixture
    def sample_api_spec(self):
        """Sample API spec for testing."""
        return OCPAPISpec(
            title="Test API",
            version="1.0.0",
            base_url="https://api.test.com",
            description="Test",
            raw_spec={},
            tools=[]
        )
    
    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        return AgentContext(agent_type="test_agent")
