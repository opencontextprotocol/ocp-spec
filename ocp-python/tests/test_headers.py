"""
Tests for OCP header encoding and decoding functionality.
"""

import pytest
import json
import base64
import gzip
from ocp_agent.headers import (
    OCPHeaders, 
    create_ocp_headers, 
    extract_context_from_response,
    OCP_CONTEXT_ID,
    OCP_SESSION,
    OCP_AGENT_TYPE,
    OCP_AGENT_GOAL,
    OCP_WORKSPACE,
    OCP_VERSION
)
from ocp_agent.context import AgentContext


class TestOCPHeadersEncoding:
    """Test OCP header encoding functionality."""
    
    def test_encode_minimal_context(self, minimal_context):
        """Test encoding minimal context to headers."""
        headers = OCPHeaders.encode_context(minimal_context)
        
        assert OCP_CONTEXT_ID in headers
        assert OCP_SESSION in headers
        assert OCP_AGENT_TYPE in headers
        assert OCP_VERSION in headers
        
        assert headers[OCP_CONTEXT_ID] == minimal_context.context_id
        assert headers[OCP_AGENT_TYPE] == minimal_context.agent_type
        assert headers[OCP_VERSION] == "1.0"
    
    def test_encode_full_context(self, sample_context):
        """Test encoding full context with all fields."""
        headers = OCPHeaders.encode_context(sample_context)
        
        # Check all expected headers are present
        expected_headers = [OCP_CONTEXT_ID, OCP_SESSION, OCP_AGENT_TYPE, OCP_VERSION]
        for header in expected_headers:
            assert header in headers
        
        # Check optional headers
        if sample_context.current_goal:
            assert OCP_AGENT_GOAL in headers
            assert headers[OCP_AGENT_GOAL] == sample_context.current_goal
        
        if sample_context.workspace:
            assert OCP_WORKSPACE in headers
            assert headers[OCP_WORKSPACE] == sample_context.workspace
    
    def test_encode_with_compression(self, complex_context):
        """Test encoding with compression for large contexts."""
        headers = OCPHeaders.encode_context(complex_context, compress=True)
        
        # Session data should be compressed if large enough
        session_data = headers[OCP_SESSION]
        if session_data.startswith("gzip:"):
            # Verify we can decode the compressed data
            encoded_data = session_data[5:]
            compressed = base64.b64decode(encoded_data.encode('ascii'))
            decompressed = gzip.decompress(compressed).decode('utf-8')
            parsed = json.loads(decompressed)
            
            assert parsed["context_id"] == complex_context.context_id
    
    def test_encode_without_compression(self, sample_context):
        """Test encoding without compression."""
        headers = OCPHeaders.encode_context(sample_context, compress=False)
        
        # Session data should be base64 encoded but not compressed
        session_data = headers[OCP_SESSION]
        assert not session_data.startswith("gzip:")
        
        # Should be decodable as base64
        decoded = base64.b64decode(session_data.encode('ascii')).decode('utf-8')
        parsed = json.loads(decoded)
        assert parsed["context_id"] == sample_context.context_id


class TestOCPHeadersDecoding:
    """Test OCP header decoding functionality."""
    
    def test_decode_valid_headers(self, sample_context):
        """Test decoding valid OCP headers."""
        # Encode then decode
        headers = OCPHeaders.encode_context(sample_context)
        decoded_context = OCPHeaders.decode_context(headers)
        
        assert decoded_context is not None
        assert decoded_context.context_id == sample_context.context_id
        assert decoded_context.agent_type == sample_context.agent_type
        assert decoded_context.user == sample_context.user
        assert len(decoded_context.history) == len(sample_context.history)
    
    def test_decode_case_insensitive(self, sample_context):
        """Test that header decoding is case-insensitive."""
        headers = OCPHeaders.encode_context(sample_context)
        
        # Convert to different cases
        mixed_case_headers = {
            "ocp-context-id": headers[OCP_CONTEXT_ID],
            "OCP-SESSION": headers[OCP_SESSION],
            "Ocp-Agent-Type": headers[OCP_AGENT_TYPE]
        }
        
        decoded_context = OCPHeaders.decode_context(mixed_case_headers)
        assert decoded_context is not None
        assert decoded_context.context_id == sample_context.context_id
    
    def test_decode_compressed_headers(self, complex_context):
        """Test decoding compressed headers."""
        headers = OCPHeaders.encode_context(complex_context, compress=True)
        decoded_context = OCPHeaders.decode_context(headers)
        
        assert decoded_context is not None
        assert decoded_context.context_id == complex_context.context_id
        assert len(decoded_context.history) == len(complex_context.history)
    
    def test_decode_missing_headers(self):
        """Test decoding with missing required headers."""
        # Missing context ID
        headers = {OCP_SESSION: "dGVzdA=="}
        assert OCPHeaders.decode_context(headers) is None
        
        # Missing session
        headers = {OCP_CONTEXT_ID: "ocp-12345678"}
        assert OCPHeaders.decode_context(headers) is None
    
    def test_decode_invalid_base64(self):
        """Test decoding with invalid base64 data."""
        headers = {
            OCP_CONTEXT_ID: "ocp-12345678",
            OCP_SESSION: "invalid-base64-data"
        }
        assert OCPHeaders.decode_context(headers) is None
    
    def test_decode_invalid_json(self):
        """Test decoding with invalid JSON data."""
        invalid_json = base64.b64encode(b"invalid json").decode('ascii')
        headers = {
            OCP_CONTEXT_ID: "ocp-12345678",
            OCP_SESSION: invalid_json
        }
        assert OCPHeaders.decode_context(headers) is None


class TestOCPHeadersValidation:
    """Test OCP header validation functionality."""
    
    def test_validate_valid_headers(self, sample_context):
        """Test validating correct headers."""
        headers = OCPHeaders.encode_context(sample_context)
        assert OCPHeaders.validate_headers(headers) is True
    
    def test_validate_missing_headers(self):
        """Test validating headers with missing required fields."""
        # Missing context ID
        headers = {OCP_SESSION: "dGVzdA=="}
        assert OCPHeaders.validate_headers(headers) is False
        
        # Missing session
        headers = {OCP_CONTEXT_ID: "ocp-12345678"}
        assert OCPHeaders.validate_headers(headers) is False
    
    def test_validate_invalid_data(self):
        """Test validating headers with invalid data."""
        headers = {
            OCP_CONTEXT_ID: "ocp-12345678",
            OCP_SESSION: "invalid-data"
        }
        assert OCPHeaders.validate_headers(headers) is False


class TestOCPHeadersUtilities:
    """Test OCP header utility functions."""
    
    def test_get_context_summary(self, sample_context):
        """Test getting context summary from headers."""
        headers = OCPHeaders.encode_context(sample_context)
        summary = OCPHeaders.get_context_summary(headers)
        
        assert isinstance(summary, str)
        assert sample_context.context_id in summary
        assert sample_context.agent_type in summary
    
    def test_merge_headers(self):
        """Test merging OCP headers with existing headers."""
        base_headers = {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json"
        }
        
        ocp_headers = {
            OCP_CONTEXT_ID: "ocp-12345678",
            OCP_AGENT_TYPE: "test_agent"
        }
        
        merged = OCPHeaders.merge_headers(base_headers, ocp_headers)
        
        # Should contain both sets
        assert "Authorization" in merged
        assert "Content-Type" in merged
        assert OCP_CONTEXT_ID in merged
        assert OCP_AGENT_TYPE in merged
        
        # Original headers should not be modified
        assert OCP_CONTEXT_ID not in base_headers
    
    def test_strip_ocp_headers(self, sample_context):
        """Test removing OCP headers from header dict."""
        headers = OCPHeaders.encode_context(sample_context)
        headers["Authorization"] = "Bearer token123"
        headers["Content-Type"] = "application/json"
        
        stripped = OCPHeaders.strip_ocp_headers(headers)
        
        # OCP headers should be removed
        assert OCP_CONTEXT_ID not in stripped
        assert OCP_SESSION not in stripped
        assert OCP_AGENT_TYPE not in stripped
        
        # Non-OCP headers should remain
        assert "Authorization" in stripped
        assert "Content-Type" in stripped


class TestConvenienceFunctions:
    """Test convenience functions for header operations."""
    
    def test_create_ocp_headers(self, sample_context):
        """Test create_ocp_headers convenience function."""
        headers = create_ocp_headers(sample_context)
        
        assert OCP_CONTEXT_ID in headers
        assert headers[OCP_CONTEXT_ID] == sample_context.context_id
    
    def test_create_ocp_headers_with_base(self, sample_context):
        """Test create_ocp_headers with base headers."""
        base_headers = {"Authorization": "Bearer token123"}
        headers = create_ocp_headers(sample_context, base_headers)
        
        # Should contain both
        assert "Authorization" in headers
        assert OCP_CONTEXT_ID in headers
    
    def test_extract_context_from_response(self, sample_context, mock_http_response):
        """Test extracting context from HTTP response."""
        # Create response with OCP headers
        ocp_headers = OCPHeaders.encode_context(sample_context)
        response = mock_http_response(headers=ocp_headers)
        
        extracted_context = extract_context_from_response(response)
        
        assert extracted_context is not None
        assert extracted_context.context_id == sample_context.context_id
    
    def test_extract_context_no_headers(self, mock_http_response):
        """Test extracting context from response without OCP headers."""
        response = mock_http_response(headers={"Content-Type": "application/json"})
        
        extracted_context = extract_context_from_response(response)
        assert extracted_context is None
    
    def test_extract_context_no_headers_attr(self):
        """Test extracting context from object without headers attribute."""
        class ResponseWithoutHeaders:
            pass
        
        response = ResponseWithoutHeaders()
        extracted_context = extract_context_from_response(response)
        assert extracted_context is None


class TestHeaderRoundTrip:
    """Test complete encode/decode roundtrip scenarios."""
    
    def test_minimal_roundtrip(self, minimal_context):
        """Test roundtrip with minimal context."""
        headers = OCPHeaders.encode_context(minimal_context)
        decoded = OCPHeaders.decode_context(headers)
        
        assert decoded.context_id == minimal_context.context_id
        assert decoded.agent_type == minimal_context.agent_type
    
    def test_complex_roundtrip(self, complex_context):
        """Test roundtrip with complex context."""
        headers = OCPHeaders.encode_context(complex_context)
        decoded = OCPHeaders.decode_context(headers)
        
        # Verify all data preserved
        assert decoded.context_id == complex_context.context_id
        assert decoded.agent_type == complex_context.agent_type
        assert decoded.user == complex_context.user
        assert decoded.workspace == complex_context.workspace
        assert decoded.current_file == complex_context.current_file
        assert decoded.current_goal == complex_context.current_goal
        assert decoded.error_context == complex_context.error_context
        assert len(decoded.history) == len(complex_context.history)
        assert len(decoded.recent_changes) == len(complex_context.recent_changes)
        assert decoded.api_specs == complex_context.api_specs
    
    @pytest.mark.parametrize("compress", [True, False])
    def test_roundtrip_with_compression_options(self, sample_context, compress):
        """Test roundtrip with different compression settings."""
        headers = OCPHeaders.encode_context(sample_context, compress=compress)
        decoded = OCPHeaders.decode_context(headers)
        
        assert decoded.context_id == sample_context.context_id
        assert decoded.current_goal == sample_context.current_goal
        assert len(decoded.history) == len(sample_context.history)


class TestNewConvenienceFunctions:
    """Test the new convenience functions in headers module."""
    
    def test_parse_context_with_dict(self, sample_context):
        """Test parse_context with dictionary headers."""
        from ocp_agent.headers import parse_context
        
        headers = sample_context.to_headers()
        parsed = parse_context(headers)
        
        assert parsed is not None
        assert parsed.agent_type == sample_context.agent_type
        assert parsed.user == sample_context.user
    
    def test_parse_context_with_headers_object(self, sample_context):
        """Test parse_context with headers object that has items()."""
        from unittest.mock import Mock
        from ocp_agent.headers import parse_context
        
        headers_dict = sample_context.to_headers()
        
        # Mock headers object with items() method
        headers_obj = Mock()
        headers_obj.items.return_value = headers_dict.items()
        
        parsed = parse_context(headers_obj)
        assert parsed is not None
        assert parsed.agent_type == sample_context.agent_type
    
    def test_parse_context_no_ocp_headers(self):
        """Test parse_context with no OCP headers."""
        from ocp_agent.headers import parse_context
        
        headers = {"content-type": "application/json"}
        parsed = parse_context(headers)
        assert parsed is None
    
    def test_add_context_headers_flask_style(self, sample_context):
        """Test add_context_headers with Flask-style response."""
        from unittest.mock import Mock
        from ocp_agent.headers import add_context_headers
        
        # Mock Flask response with proper headers object
        headers_mock = Mock()
        headers_mock.__setitem__ = Mock()
        
        response = Mock()
        response.headers = headers_mock
        
        add_context_headers(response, sample_context)
        
        # Should have called __setitem__ for each OCP header
        assert response.headers.__setitem__.called
    
    def test_add_context_headers_django_style(self, sample_context):
        """Test add_context_headers with Django-style response."""
        from unittest.mock import Mock
        from ocp_agent.headers import add_context_headers
        
        # Mock Django response
        response = Mock()
        response.__setitem__ = Mock()
        # Remove headers attribute to trigger Django path
        del response.headers
        
        add_context_headers(response, sample_context)
        
        # Should have called __setitem__ for each OCP header
        assert response.__setitem__.called
    
    def test_add_context_headers_fastapi_style(self, sample_context):
        """Test add_context_headers with FastAPI-style response."""
        from unittest.mock import Mock
        from ocp_agent.headers import add_context_headers
        
        # Mock FastAPI response - first condition fails, second condition fails,
        # third condition (append) succeeds, then falls back to dict assignment
        headers_mock = {}
        response = Mock()
        response.headers = headers_mock
        
        add_context_headers(response, sample_context)
        
        # Should have added headers to the dict
        assert len(response.headers) > 0
        assert any(key.startswith('OCP-') for key in response.headers)
    
    def test_add_context_headers_generic_dict(self, sample_context):
        """Test add_context_headers with generic headers dict."""
        from unittest.mock import Mock
        from ocp_agent.headers import add_context_headers
        
        # Mock response with headers dict
        response = Mock()
        response.headers = {}
        
        add_context_headers(response, sample_context)
        
        assert len(response.headers) > 0
        assert any(key.startswith('OCP-') for key in response.headers)
    
    def test_add_context_headers_unsupported_type(self, sample_context):
        """Test add_context_headers with unsupported response type."""
        from unittest.mock import Mock, PropertyMock
        from ocp_agent.headers import add_context_headers
        import pytest
        
        # Mock completely unsupported response that fails all attempts
        response = Mock()
        # Remove all potential ways to set headers
        del response.headers
        del response.__setitem__
        
        # Make setting headers attribute fail
        type(response).headers = PropertyMock(side_effect=AttributeError("Cannot set headers"))
        
        with pytest.raises(TypeError, match="Unsupported response type"):
            add_context_headers(response, sample_context)
    
    def test_add_context_headers_with_compression(self, sample_context):
        """Test add_context_headers with compression option."""
        from unittest.mock import Mock
        from ocp_agent.headers import add_context_headers
        
        response = Mock()
        response.headers = {}
        
        add_context_headers(response, sample_context, compress=False)
        
        assert len(response.headers) > 0
        assert any(key.startswith('OCP-') for key in response.headers)