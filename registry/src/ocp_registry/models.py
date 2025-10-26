"""Data models for the OCP Registry."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, HttpUrl, Field
from pydantic import ConfigDict

# Import OCP types from the installed dependency
from ocp_agent.schema_discovery import OCPTool, OCPAPISpec


class AuthType(str, Enum):
    """Supported authentication types."""
    none = "none"
    api_key = "api_key"
    bearer_token = "bearer_token" 
    oauth2 = "oauth2"
    basic_auth = "basic_auth"


class APICategory(str, Enum):
    """API categories for organization."""
    development = "development"
    productivity = "productivity"
    communication = "communication"
    finance = "finance"
    ecommerce = "ecommerce"
    social = "social"
    media = "media"
    analytics = "analytics"
    infrastructure = "infrastructure"
    other = "other"


class APIStatus(str, Enum):
    """API validation status."""
    active = "active"
    inactive = "inactive"
    deprecated = "deprecated"
    validation_pending = "validation_pending"
    validation_failed = "validation_failed"


class AuthConfig(BaseModel):
    """Authentication configuration details."""
    type: AuthType
    header_name: Optional[str] = None
    query_param: Optional[str] = None
    token_url: Optional[HttpUrl] = None
    scopes: Optional[List[str]] = None
    instructions: Optional[str] = None


class APIRegistration(BaseModel):
    """API registration request model."""
    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    display_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    openapi_url: HttpUrl
    base_url: HttpUrl
    category: APICategory
    auth_config: AuthConfig
    tags: Optional[List[str]] = Field(default=[], max_length=10)
    documentation_url: Optional[HttpUrl] = None
    contact_email: Optional[str] = None
    rate_limit: Optional[str] = None


class APIEntry(APIRegistration):
    """Full API registry entry with metadata."""
    id: int
    created_at: datetime
    updated_at: datetime
    status: APIStatus = APIStatus.validation_pending
    validation_error: Optional[str] = None
    tool_count: Optional[int] = None
    # Store tools as dicts for JSON serialization, but can convert to OCPTool objects
    tools: Optional[List[Dict[str, Any]]] = None  # Pre-discovered OCP tools (stored as JSON)
    last_validated: Optional[datetime] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    usage_count: int = 0
    
    model_config = {"from_attributes": True}
    
    def get_ocp_tools(self) -> List[OCPTool]:
        """Convert stored tool dicts to OCPTool objects."""
        if not self.tools:
            return []
        
        ocp_tools = []
        for tool_dict in self.tools:
            # Convert dict back to OCPTool object
            ocp_tool = OCPTool(
                name=tool_dict['name'],
                description=tool_dict['description'],
                method=tool_dict['method'],
                path=tool_dict['path'],
                parameters=tool_dict.get('parameters', {}),
                response_schema=tool_dict.get('response_schema', {}),
                operation_id=tool_dict.get('operation_id'),
                tags=tool_dict.get('tags')
            )
            ocp_tools.append(ocp_tool)
        return ocp_tools
    
    @staticmethod
    def tools_to_dict(ocp_tools: List[OCPTool]) -> List[Dict[str, Any]]:
        """Convert OCPTool objects to dict format for storage."""
        tools_data = []
        for tool in ocp_tools:
            tool_dict = {
                'name': tool.name,
                'description': tool.description,
                'method': tool.method,
                'path': tool.path,
                'parameters': tool.parameters,
                'response_schema': tool.response_schema,
                'operation_id': tool.operation_id,
                'tags': tool.tags
            }
            tools_data.append(tool_dict)
        return tools_data


class APISearchResult(BaseModel):
    """Search result item."""
    name: str
    display_name: str
    description: str
    category: APICategory
    status: APIStatus
    rating: Optional[float] = None
    tool_count: Optional[int] = None
    tags: List[str] = []


class APISearchResponse(BaseModel):
    """Search response with results and metadata."""
    query: str
    results: List[APISearchResult]
    total: int
    page: int = 1
    per_page: int = 20


class ValidationRequest(BaseModel):
    """Request to validate an API specification."""
    openapi_url: HttpUrl
    base_url: Optional[HttpUrl] = None


class ValidationResult(BaseModel):
    """API validation result."""
    valid: bool
    openapi_valid: bool
    endpoint_accessible: bool
    tool_count: Optional[int] = None
    errors: List[str] = []
    warnings: List[str] = []
    
    
class CategorySummary(BaseModel):
    """Category with API count."""
    category: APICategory
    count: int
    description: str


class RegistryStats(BaseModel):
    """Overall registry statistics."""
    total_apis: int
    active_apis: int
    categories: List[CategorySummary]
    most_popular: List[APISearchResult]