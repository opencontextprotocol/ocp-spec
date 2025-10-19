"""API validation service for OCP Registry."""

import asyncio
import json
from typing import Tuple, List, Dict, Any, Optional
import httpx
from urllib.parse import urljoin

from .models import ValidationResult, ValidationRequest


class APIValidator:
    """Validates API specifications and endpoints."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        
    async def validate_api(self, request: ValidationRequest) -> ValidationResult:
        """Validate an API specification and endpoint."""
        result = ValidationResult(
            valid=False,
            openapi_valid=False,
            endpoint_accessible=False,
            errors=[],
            warnings=[]
        )
        
        # Validate OpenAPI specification
        openapi_result = await self._validate_openapi_spec(request.openapi_url)
        result.openapi_valid = openapi_result[0]
        result.tool_count = openapi_result[1]
        if not result.openapi_valid:
            result.errors.extend(openapi_result[2])
        
        # Validate endpoint accessibility
        if request.base_url:
            endpoint_result = await self._validate_endpoint(request.base_url)
            result.endpoint_accessible = endpoint_result[0]
            if not result.endpoint_accessible:
                result.errors.extend(endpoint_result[1])
        else:
            result.warnings.append("No base URL provided for endpoint validation")
            result.endpoint_accessible = True  # Don't fail validation
            
        # Overall validation passes if OpenAPI is valid
        result.valid = result.openapi_valid
        
        return result
        
    async def _validate_openapi_spec(self, openapi_url: str) -> Tuple[bool, Optional[int], List[str]]:
        """Validate OpenAPI specification."""
        errors = []
        tool_count = None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(str(openapi_url))
                response.raise_for_status()
                
                # Parse JSON
                try:
                    spec = response.json()
                except json.JSONDecodeError as e:
                    errors.append(f"Invalid JSON in OpenAPI spec: {e}")
                    return False, None, errors
                
                # Basic OpenAPI validation
                if not isinstance(spec, dict):
                    errors.append("OpenAPI spec must be a JSON object")
                    return False, None, errors
                    
                # Check required fields
                if "openapi" not in spec and "swagger" not in spec:
                    errors.append("Missing 'openapi' or 'swagger' version field")
                    return False, None, errors
                    
                if "paths" not in spec:
                    errors.append("Missing 'paths' object")
                    return False, None, errors
                    
                if "info" not in spec:
                    errors.append("Missing 'info' object")
                    return False, None, errors
                
                # Count available operations (tools)
                tool_count = self._count_operations(spec.get("paths", {}))
                
                if tool_count == 0:
                    errors.append("No API operations found in specification")
                    return False, tool_count, errors
                
                return True, tool_count, []
                
        except httpx.RequestError as e:
            errors.append(f"Failed to fetch OpenAPI spec: {e}")
            return False, None, errors
        except httpx.HTTPStatusError as e:
            errors.append(f"HTTP error fetching OpenAPI spec: {e.response.status_code}")
            return False, None, errors
        except Exception as e:
            errors.append(f"Unexpected error validating OpenAPI spec: {e}")
            return False, None, errors
            
    async def _validate_endpoint(self, base_url: str) -> Tuple[bool, List[str]]:
        """Validate that the API endpoint is accessible."""
        errors = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try a simple HEAD or GET request to the base URL
                response = await client.get(str(base_url))
                
                # Accept any response that's not a connection error
                # APIs may return 401, 404, etc. but still be accessible
                if response.status_code < 500:
                    return True, []
                else:
                    errors.append(f"API endpoint returned server error: {response.status_code}")
                    return False, errors
                    
        except httpx.ConnectError:
            errors.append("Cannot connect to API endpoint")
            return False, errors
        except httpx.TimeoutException:
            errors.append("Timeout connecting to API endpoint")
            return False, errors
        except Exception as e:
            errors.append(f"Error validating endpoint: {e}")
            return False, errors
    
    def _count_operations(self, paths: Dict[str, Any]) -> int:
        """Count the number of operations in OpenAPI paths."""
        count = 0
        http_methods = {"get", "post", "put", "delete", "patch", "head", "options", "trace"}
        
        for path_item in paths.values():
            if isinstance(path_item, dict):
                for method in path_item.keys():
                    if method.lower() in http_methods:
                        count += 1
                        
        return count


# Global validator instance
validator = APIValidator()