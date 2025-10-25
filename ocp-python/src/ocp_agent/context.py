"""
AgentContext - Core context management for OCP agents.

Handles creating, updating, and maintaining agent context throughout
multi-step workflows.
"""

import uuid
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass
class AgentContext:
    """
    Core agent context that flows through OCP-enabled API calls.
    
    This represents the agent's understanding of the current conversation,
    workspace state, and goals.
    """
    
    # Core identification
    context_id: str = field(default_factory=lambda: f"ocp-{uuid.uuid4().hex[:8]}")
    agent_type: str = "generic_agent"
    
    # Agent state
    user: Optional[str] = None
    workspace: Optional[str] = None
    current_file: Optional[str] = None
    
    # Conversation tracking
    session: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Goals and intent
    current_goal: Optional[str] = None
    context_summary: Optional[str] = None
    
    # Technical context
    error_context: Optional[str] = None
    recent_changes: List[str] = field(default_factory=list)
    
    # API specifications
    api_specs: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize session with basic metadata if not provided."""
        if not self.session:
            self.session = {
                "start_time": self.created_at.isoformat(),
                "interaction_count": 0,
                "agent_type": self.agent_type,
            }
    
    def update_goal(self, goal: str, summary: Optional[str] = None) -> None:
        """Update the agent's current goal and context summary."""
        self.current_goal = goal
        if summary:
            self.context_summary = summary
        self.last_updated = datetime.now(timezone.utc)
        self.session["interaction_count"] = self.session.get("interaction_count", 0) + 1
    
    def add_interaction(
        self, 
        action: str, 
        api_endpoint: Optional[str] = None,
        result: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an interaction to the conversation history."""
        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "api_endpoint": api_endpoint,
            "result": result,
            "metadata": metadata or {},
        }
        self.history.append(interaction)
        self.last_updated = datetime.now(timezone.utc)
    
    def set_error_context(self, error: str, file_path: Optional[str] = None) -> None:
        """Set error context for debugging scenarios."""
        self.error_context = error
        if file_path:
            self.current_file = file_path
        self.last_updated = datetime.now(timezone.utc)
    
    def add_recent_change(self, change: str) -> None:
        """Add a recent change to track modifications."""
        self.recent_changes.append(change)
        # Keep only last 10 changes
        if len(self.recent_changes) > 10:
            self.recent_changes = self.recent_changes[-10:]
        self.last_updated = datetime.now(timezone.utc)
    
    def add_api_spec(self, api_name: str, openapi_url: str) -> None:
        """Add an API specification for enhanced responses."""
        self.api_specs[api_name] = openapi_url
        self.last_updated = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        """Create AgentContext from dictionary."""
        # Convert ISO strings back to datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if "last_updated" in data and isinstance(data["last_updated"], str):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"].replace("Z", "+00:00"))
        
        return cls(**data)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation for API context."""
        summary_parts = []
        
        if self.current_goal:
            summary_parts.append(f"Goal: {self.current_goal}")
        
        if self.error_context:
            summary_parts.append(f"Error: {self.error_context}")
        
        if self.current_file:
            summary_parts.append(f"Working on: {self.current_file}")
        
        if self.recent_changes:
            summary_parts.append(f"Recent changes: {', '.join(self.recent_changes[-3:])}")
        
        if self.history:
            recent_actions = [h["action"] for h in self.history[-3:]]
            summary_parts.append(f"Recent actions: {', '.join(recent_actions)}")
        
        return " | ".join(summary_parts) if summary_parts else "New conversation"
    
    def clone(self) -> "AgentContext":
        """Create a copy of this context for forked workflows."""
        data = self.to_dict()
        data["context_id"] = f"ocp-{uuid.uuid4().hex[:8]}"  # New ID for clone
        return self.from_dict(data)
    
    def to_headers(self, compress: bool = True) -> Dict[str, str]:
        """
        Convenience method to convert context to OCP headers.
        
        Args:
            compress: Whether to compress session data (default: True)
            
        Returns:
            Dictionary of HTTP headers ready for requests
        """
        # Import here to avoid circular dependency
        from .headers import create_ocp_headers
        return create_ocp_headers(self, compress=compress)
    
    def update_from_headers(self, headers: Dict[str, str]) -> bool:
        """
        Convenience method to update context from HTTP response headers.
        
        Args:
            headers: HTTP headers dictionary
            
        Returns:
            True if context was updated, False if no OCP headers found
        """
        # Import here to avoid circular dependency
        from .headers import OCPHeaders
        
        # Convert headers to dict if needed (handle different response types)
        if hasattr(headers, 'items'):
            headers_dict = dict(headers.items())
        else:
            headers_dict = dict(headers)
        
        new_context = OCPHeaders.decode_context(headers_dict)
        if new_context:
            # Update current context with relevant fields from response
            # Keep our identity but update session and goal info
            if new_context.current_goal and new_context.current_goal != self.current_goal:
                self.current_goal = new_context.current_goal
            if new_context.context_summary:
                self.context_summary = new_context.context_summary
            if new_context.history:
                # Merge histories, avoiding duplicates
                existing_ids = {h.get("interaction_id") for h in self.history}
                for interaction in new_context.history:
                    if interaction.get("interaction_id") not in existing_ids:
                        self.history.append(interaction)
            # Update timestamp
            self.last_updated = datetime.now(timezone.utc)
            return True
        return False