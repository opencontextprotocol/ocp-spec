"""
OCPStorage - Local storage for API caching and session persistence.

Provides optional local storage for OCP agents to cache API specifications
and persist session contexts across application restarts.
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from .context import AgentContext
from .schema_discovery import OCPAPISpec


class OCPStorage:
    """
    Local storage manager for OCP API cache and session persistence.
    
    Storage directory structure:
        ~/.ocp/
        ├── cache/
        │   └── apis/
        │       ├── github.json
        │       ├── stripe.json
        │       └── ...
        └── sessions/
            ├── vscode-chat-abc123.json
            ├── cli-session-xyz789.json
            └── ...
    
    Design principles:
    - Per-file storage for surgical reads/writes
    - Fail-safe: storage errors don't break functionality
    - Consumer-agnostic: doesn't manage consumer config
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize storage with base directory.
        
        Args:
            base_path: Base storage directory (defaults to ~/.ocp/)
        """
        if base_path is None:
            base_path = Path.home() / ".ocp"
        
        self.base_path = Path(base_path)
        self.cache_dir = self.base_path / "cache" / "apis"
        self.sessions_dir = self.base_path / "sessions"
        
        self._ensure_dirs()
    
    def _ensure_dirs(self) -> None:
        """Create storage directories if they don't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Non-fatal: log but don't raise
            print(f"Warning: Failed to create storage directories: {e}")
    
    # ==================== API Caching ====================
    
    def cache_api(
        self, 
        name: str, 
        spec: OCPAPISpec, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache an API specification locally.
        
        Args:
            name: API name (used as filename)
            spec: API specification to cache
            metadata: Optional metadata (source, cached_at, etc.)
            
        Returns:
            True if cached successfully, False on error
        """
        try:
            cache_file = self.cache_dir / f"{name}.json"
            
            cache_data = {
                "api_name": name,
                "title": spec.title,
                "version": spec.version,
                "base_url": spec.base_url,
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "source": metadata.get("source", "unknown") if metadata else "unknown",
                "raw_spec": spec.raw_spec,
                "tools": [
                    {
                        "name": tool.name,
                        "method": tool.method,
                        "path": tool.path,
                        "description": tool.description,
                        "parameters": tool.parameters,
                        "response_schema": tool.response_schema,
                        "operation_id": tool.operation_id,
                        "tags": tool.tags
                    }
                    for tool in spec.tools
                ]
            }
            
            if metadata:
                cache_data.update(metadata)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (OSError, IOError, ValueError) as e:
            print(f"Warning: Failed to cache API '{name}': {e}")
            return False
    
    def get_cached_api(
        self, 
        name: str, 
        max_age_days: Optional[int] = None
    ) -> Optional[OCPAPISpec]:
        """
        Retrieve cached API specification.
        
        Args:
            name: API name to retrieve
            max_age_days: Maximum age in days (None = no expiration)
            
        Returns:
            Cached API spec or None if not found/expired
        """
        try:
            cache_file = self.cache_dir / f"{name}.json"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration if max_age_days is set
            if max_age_days is not None:
                cached_at = datetime.fromisoformat(
                    cache_data["cached_at"].replace("Z", "+00:00")
                )
                age = datetime.now(timezone.utc) - cached_at
                
                if age > timedelta(days=max_age_days):
                    return None  # Expired
            
            # Reconstruct OCPAPISpec from cache
            # Import here to avoid circular dependency
            from .schema_discovery import OCPTool
            
            tools = [
                OCPTool(
                    name=t["name"],
                    method=t["method"],
                    path=t["path"],
                    description=t.get("description", ""),
                    parameters=t.get("parameters", {}),
                    response_schema=t.get("response_schema", {}),
                    operation_id=t.get("operation_id"),
                    tags=t.get("tags")
                )
                for t in cache_data.get("tools", [])
            ]
            
            api_spec = OCPAPISpec(
                title=cache_data["title"],
                version=cache_data["version"],
                base_url=cache_data["base_url"],
                description=cache_data.get("description", ""),
                raw_spec=cache_data["raw_spec"],
                tools=tools
            )
            
            return api_spec
            
        except (OSError, IOError, ValueError, KeyError) as e:
            print(f"Warning: Failed to load cached API '{name}': {e}")
            return None
    
    def search_cache(self, query: str) -> List[Dict[str, Any]]:
        """
        Search cached APIs by name or description.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching API metadata
        """
        results = []
        query_lower = query.lower()
        
        try:
            if not self.cache_dir.exists():
                return []
            
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Search in name, title, and tool descriptions
                    if (query_lower in cache_data.get("api_name", "").lower() or
                        query_lower in cache_data.get("title", "").lower() or
                        any(query_lower in tool.get("description", "").lower() 
                            for tool in cache_data.get("tools", []))):
                        
                        results.append({
                            "name": cache_data.get("api_name"),
                            "title": cache_data.get("title"),
                            "version": cache_data.get("version"),
                            "base_url": cache_data.get("base_url"),
                            "cached_at": cache_data.get("cached_at"),
                            "tool_count": len(cache_data.get("tools", []))
                        })
                        
                except (OSError, IOError, ValueError):
                    continue
            
        except OSError:
            pass
        
        return results
    
    def list_cached_apis(self) -> List[str]:
        """
        List all cached API names.
        
        Returns:
            List of API names
        """
        try:
            if not self.cache_dir.exists():
                return []
            
            return [f.stem for f in self.cache_dir.glob("*.json")]
            
        except OSError:
            return []
    
    def clear_cache(self, name: Optional[str] = None) -> bool:
        """
        Clear API cache.
        
        Args:
            name: Specific API to clear (None = clear all)
            
        Returns:
            True if cleared successfully
        """
        try:
            if name:
                # Clear specific API
                cache_file = self.cache_dir / f"{name}.json"
                if cache_file.exists():
                    cache_file.unlink()
            else:
                # Clear all cache files
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
            
            return True
            
        except OSError as e:
            print(f"Warning: Failed to clear cache: {e}")
            return False
    
    # ==================== Session Persistence ====================
    
    def save_session(self, session_id: str, context: AgentContext) -> bool:
        """
        Save session context to disk.
        
        Args:
            session_id: Unique session identifier
            context: Agent context to save
            
        Returns:
            True if saved successfully
        """
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            
            session_data = context.to_dict()
            session_data["session_id"] = session_id
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (OSError, IOError, ValueError) as e:
            print(f"Warning: Failed to save session '{session_id}': {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[AgentContext]:
        """
        Load session context from disk.
        
        Args:
            session_id: Session identifier to load
            
        Returns:
            Loaded context or None if not found
        """
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            
            if not session_file.exists():
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Remove session_id from data (not part of AgentContext)
            session_data.pop("session_id", None)
            
            # Use from_dict to reconstruct context
            context = AgentContext.from_dict(session_data)
            
            return context
            
        except (OSError, IOError, ValueError, KeyError) as e:
            print(f"Warning: Failed to load session '{session_id}': {e}")
            return None
    
    def list_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all sessions with metadata.
        
        Args:
            limit: Maximum number of sessions to return (most recent first)
            
        Returns:
            List of session metadata dicts
        """
        sessions = []
        
        try:
            if not self.sessions_dir.exists():
                return []
            
            # Get all session files
            session_files = list(self.sessions_dir.glob("*.json"))
            
            # Sort by modification time (most recent first)
            session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Apply limit if specified
            if limit:
                session_files = session_files[:limit]
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    sessions.append({
                        "id": session_data.get("session_id", session_file.stem),
                        "context_id": session_data.get("context_id"),
                        "agent_type": session_data.get("agent_type"),
                        "user": session_data.get("user"),
                        "workspace": session_data.get("workspace"),
                        "created_at": session_data.get("created_at"),
                        "last_updated": session_data.get("last_updated"),
                        "interaction_count": session_data.get("session", {}).get("interaction_count", 0)
                    })
                    
                except (OSError, IOError, ValueError):
                    continue
            
        except OSError:
            pass
        
        return sessions
    
    def cleanup_sessions(self, keep_recent: int = 50) -> int:
        """
        Remove old sessions, keeping N most recent.
        
        Args:
            keep_recent: Number of recent sessions to keep
            
        Returns:
            Number of sessions removed
        """
        try:
            if not self.sessions_dir.exists():
                return 0
            
            # Get all session files sorted by modification time
            session_files = list(self.sessions_dir.glob("*.json"))
            session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Remove old sessions beyond keep_recent
            removed = 0
            for session_file in session_files[keep_recent:]:
                try:
                    session_file.unlink()
                    removed += 1
                except OSError:
                    continue
            
            return removed
            
        except OSError as e:
            print(f"Warning: Failed to cleanup sessions: {e}")
            return 0
