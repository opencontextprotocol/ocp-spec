"""
OCP Headers - HTTP header management for Open Context Protocol.

Handles encoding/decoding agent context into HTTP headers and validation.
"""

import json
import base64
import gzip
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

from .context import AgentContext


# OCP Header names
OCP_CONTEXT_ID = "OCP-Context-ID"
OCP_SESSION = "OCP-Session"
OCP_AGENT_GOAL = "OCP-Agent-Goal"
OCP_AGENT_TYPE = "OCP-Agent-Type"
OCP_USER = "OCP-User"
OCP_WORKSPACE = "OCP-Workspace"
OCP_VERSION = "OCP-Version"

# Current OCP specification version
OCP_SPEC_VERSION = "1.0"


@dataclass
class OCPHeaders:
    """
    Manages OCP HTTP headers for agent context transmission.
    
    Handles encoding agent context into HTTP headers and decoding
    received headers back into context objects.
    """
    
    @staticmethod
    def encode_context(context: AgentContext, compress: bool = True) -> Dict[str, str]:
        """
        Encode AgentContext into OCP HTTP headers.
        
        Args:
            context: The agent context to encode
            compress: Whether to compress the session data (default: True)
            
        Returns:
            Dictionary of HTTP headers ready to add to requests
        """
        headers = {
            OCP_CONTEXT_ID: context.context_id,
            OCP_AGENT_TYPE: context.agent_type,
            OCP_VERSION: OCP_SPEC_VERSION,
        }
        
        # Add optional headers if present
        if context.current_goal:
            headers[OCP_AGENT_GOAL] = context.current_goal
        
        if context.workspace:
            headers[OCP_WORKSPACE] = context.workspace
        
        # Encode session data
        session_data = context.to_dict()
        session_json = json.dumps(session_data, separators=(',', ':'))
        
        if compress and len(session_json) > 1000:
            # Compress large session data
            compressed = gzip.compress(session_json.encode('utf-8'))
            encoded = base64.b64encode(compressed).decode('ascii')
            headers[OCP_SESSION] = f"gzip:{encoded}"
        else:
            # Base64 encode without compression
            encoded = base64.b64encode(session_json.encode('utf-8')).decode('ascii')
            headers[OCP_SESSION] = encoded
            
        return headers
    
    @staticmethod
    def decode_context(headers: Dict[str, str]) -> Optional[AgentContext]:
        """
        Decode OCP headers back into an AgentContext object.
        
        Args:
            headers: HTTP headers dictionary (case-insensitive)
            
        Returns:
            AgentContext object or None if headers are invalid/missing
        """
        # Normalize header names (case-insensitive lookup)
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        context_id = normalized_headers.get(OCP_CONTEXT_ID.lower())
        session_data = normalized_headers.get(OCP_SESSION.lower())
        
        if not context_id or not session_data:
            return None
        
        try:
            # Decode session data
            if session_data.startswith("gzip:"):
                # Decompress gzipped data
                encoded_data = session_data[5:]  # Remove "gzip:" prefix
                compressed = base64.b64decode(encoded_data.encode('ascii'))
                session_json = gzip.decompress(compressed).decode('utf-8')
            else:
                # Base64 decode
                session_json = base64.b64decode(session_data.encode('ascii')).decode('utf-8')
            
            # Parse context data
            context_data = json.loads(session_json)
            return AgentContext.from_dict(context_data)
            
        except (json.JSONDecodeError, base64.binascii.Error, gzip.BadGzipFile, UnicodeDecodeError):
            return None
    
    @staticmethod
    def validate_headers(headers: Dict[str, str]) -> bool:
        """
        Validate that headers contain valid OCP context.
        
        Args:
            headers: HTTP headers dictionary
            
        Returns:
            True if headers are valid OCP headers
        """
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        # Check required headers
        required = [OCP_CONTEXT_ID.lower(), OCP_SESSION.lower()]
        if not all(header in normalized_headers for header in required):
            return False
        
        # Validate context can be decoded
        context = OCPHeaders.decode_context(headers)
        return context is not None
    
    @staticmethod
    def get_context_summary(headers: Dict[str, str]) -> str:
        """
        Get a human-readable summary of the OCP context from headers.
        
        Args:
            headers: HTTP headers dictionary
            
        Returns:
            Summary string for debugging/logging
        """
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        context_id = normalized_headers.get(OCP_CONTEXT_ID.lower(), "unknown")
        agent_type = normalized_headers.get(OCP_AGENT_TYPE.lower(), "unknown")
        goal = normalized_headers.get(OCP_AGENT_GOAL.lower(), "none")
        workspace = normalized_headers.get(OCP_WORKSPACE.lower(), "none")
        
        return f"OCP Context: {context_id} | Agent: {agent_type} | Goal: {goal} | Workspace: {workspace}"
    
    @staticmethod
    def merge_headers(
        base_headers: Dict[str, str], 
        ocp_headers: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Merge OCP headers with existing HTTP headers.
        
        Args:
            base_headers: Existing HTTP headers (e.g., Authorization)
            ocp_headers: OCP headers to add
            
        Returns:
            Combined headers dictionary
        """
        merged = base_headers.copy()
        merged.update(ocp_headers)
        return merged
    
    @staticmethod
    def strip_ocp_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """
        Remove OCP headers from a headers dictionary.
        
        Args:
            headers: HTTP headers dictionary
            
        Returns:
            Headers with OCP headers removed
        """
        ocp_header_names = {
            OCP_CONTEXT_ID.lower(),
            OCP_SESSION.lower(), 
            OCP_AGENT_GOAL.lower(),
            OCP_AGENT_TYPE.lower(),
            OCP_WORKSPACE.lower(),
            OCP_VERSION.lower(),
        }
        
        return {
            k: v for k, v in headers.items() 
            if k.lower() not in ocp_header_names
        }


def create_ocp_headers(
    context: AgentContext, 
    base_headers: Optional[Dict[str, str]] = None,
    compress: bool = True
) -> Dict[str, str]:
    """
    Convenience function to create OCP headers from context.
    
    Args:
        context: Agent context to encode
        base_headers: Existing headers to merge with (optional)
        compress: Whether to compress session data
        
    Returns:
        Complete headers dictionary ready for HTTP requests
    """
    ocp_headers = OCPHeaders.encode_context(context, compress=compress)
    
    if base_headers:
        return OCPHeaders.merge_headers(base_headers, ocp_headers)
    
    return ocp_headers


def extract_context_from_response(response) -> Optional[AgentContext]:
    """
    Extract OCP context from an HTTP response object.
    
    Works with requests.Response, httpx.Response, and similar objects.
    
    Args:
        response: HTTP response object with headers attribute
        
    Returns:
        AgentContext if response contains OCP headers, None otherwise
    """
    if not hasattr(response, 'headers'):
        return None
    
    # Convert headers to dict (handle different response types)
    if hasattr(response.headers, 'items'):
        headers_dict = dict(response.headers.items())
    else:
        headers_dict = dict(response.headers)
    
    return OCPHeaders.decode_context(headers_dict)


# Convenience functions for cleaner API
def parse_context(headers) -> Optional[AgentContext]:
    """
    Convenience function to parse OCP context from HTTP headers.
    
    Works with any headers object that can be converted to a dict.
    
    Args:
        headers: HTTP headers (dict, Headers object, etc.)
        
    Returns:
        AgentContext if OCP headers found, None otherwise
    """
    # Convert headers to dict (handle different header types)
    if hasattr(headers, 'items'):
        headers_dict = dict(headers.items())
    elif hasattr(headers, '__iter__') and not isinstance(headers, str):
        headers_dict = dict(headers)
    else:
        headers_dict = headers
    
    return OCPHeaders.decode_context(headers_dict)


def add_context_headers(response, context: AgentContext, compress: bool = True) -> None:
    """
    Convenience function to add OCP headers to HTTP response objects.
    
    Automatically detects response type and adds headers appropriately.
    Supports Flask, Django, FastAPI, and other common frameworks.
    
    Args:
        response: HTTP response object
        context: Agent context to encode
        compress: Whether to compress session data
    """
    ocp_headers = create_ocp_headers(context, compress=compress)
    
    # Flask Response / Werkzeug Response
    if hasattr(response, 'headers') and hasattr(response.headers, '__setitem__'):
        for key, value in ocp_headers.items():
            response.headers[key] = value
            
    # Django HttpResponse
    elif hasattr(response, '__setitem__'):
        for key, value in ocp_headers.items():
            response[key] = value
            
    # FastAPI Response / Starlette Response  
    elif hasattr(response, 'headers') and hasattr(response.headers, 'append'):
        for key, value in ocp_headers.items():
            response.headers[key] = value
            
    # Generic response with headers dict
    elif hasattr(response, 'headers') and isinstance(response.headers, dict):
        response.headers.update(ocp_headers)
        
    # Fallback - try to set as attributes
    else:
        try:
            if not hasattr(response, 'headers'):
                response.headers = {}
            response.headers.update(ocp_headers)
        except (AttributeError, TypeError):
            raise TypeError(
                f"Unsupported response type: {type(response)}. "
                f"Response must have a 'headers' attribute that supports item assignment."
            )