"""Registry service layer for OCP Registry."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

# Import OCP schema discovery from the installed dependency
from ocp.schema_discovery import OCPSchemaDiscovery

from .database import APIEntryDB
from .models import (
    APIRegistration, APIEntry, APISearchResponse, APISearchResult,
    CategorySummary, RegistryStats, APICategory, APIStatus, AuthConfig, ValidationRequest
)
from .validator import validator


class RegistryService:
    """Business logic for registry operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_api(self, registration: APIRegistration) -> APIEntry:
        """Register a new API in the registry."""
        # Check if API already exists
        existing = self.db.query(APIEntryDB).filter(APIEntryDB.name == registration.name).first()
        if existing:
            raise ValueError(f"API '{registration.name}' already exists")
        
        # Create database entry
        db_entry = APIEntryDB(
            name=registration.name,
            display_name=registration.display_name,
            description=registration.description,
            openapi_url=str(registration.openapi_url),
            base_url=str(registration.base_url),
            category=registration.category,
            auth_config=registration.auth_config.model_dump(),
            tags=registration.tags or [],
            documentation_url=str(registration.documentation_url) if registration.documentation_url else None,
            contact_email=registration.contact_email,
            rate_limit=registration.rate_limit,
            status=APIStatus.validation_pending
        )
        
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        
        # Trigger async validation and tool discovery
        try:
            validation_request = ValidationRequest(
                openapi_url=registration.openapi_url,
                base_url=registration.base_url
            )
            validation_result = await validator.validate_api(validation_request)
            
            # Update with validation results
            db_entry.status = APIStatus.active if validation_result.valid else APIStatus.validation_failed
            db_entry.validation_error = "; ".join(validation_result.errors) if validation_result.errors else None
            db_entry.tool_count = validation_result.tool_count
            
            # Discover and store tools if validation passed
            if validation_result.valid:
                try:
                    discovery = OCPSchemaDiscovery()
                    api_spec = discovery.discover_api(str(registration.openapi_url), str(registration.base_url))
                    
                    # Use the APIEntry helper method to convert OCPTool objects to dict format
                    from .models import APIEntry
                    tools_data = APIEntry.tools_to_dict(api_spec.tools)
                    
                    db_entry.tools = tools_data
                    db_entry.tool_count = len(tools_data)
                    
                except Exception as discovery_error:
                    db_entry.validation_error = f"Tool discovery failed: {discovery_error}"
            
            self.db.commit()
            self.db.refresh(db_entry)
            
        except Exception as e:
            db_entry.status = APIStatus.validation_failed
            db_entry.validation_error = f"Validation error: {e}"
            self.db.commit()
        
        return self._db_to_model(db_entry)
    
    def get_api(self, name: str) -> Optional[APIEntry]:
        """Get API by name."""
        db_entry = self.db.query(APIEntryDB).filter(APIEntryDB.name == name).first()
        return self._db_to_model(db_entry) if db_entry else None
    
    def list_apis(self, category: Optional[APICategory] = None, status: Optional[APIStatus] = None) -> List[APIEntry]:
        """List APIs with optional filtering."""
        query = self.db.query(APIEntryDB)
        
        if category:
            query = query.filter(APIEntryDB.category == category)
        if status:
            query = query.filter(APIEntryDB.status == status)
            
        return [self._db_to_model(entry) for entry in query.all()]
    
    def search_apis(self, query: str, page: int = 1, per_page: int = 20) -> APISearchResponse:
        """Search APIs by name, description, or tags."""
        offset = (page - 1) * per_page
        
        # Build search query
        search_filter = or_(
            APIEntryDB.name.ilike(f"%{query}%"),
            APIEntryDB.display_name.ilike(f"%{query}%"),
            APIEntryDB.description.ilike(f"%{query}%"),
            func.json_extract(APIEntryDB.tags, '$').op('LIKE')(f'%{query}%')
        )
        
        # Get total count
        total = self.db.query(APIEntryDB).filter(search_filter).count()
        
        # Get paginated results
        results = (
            self.db.query(APIEntryDB)
            .filter(search_filter)
            .offset(offset)
            .limit(per_page)
            .all()
        )
        
        search_results = [
            APISearchResult(
                name=entry.name,
                display_name=entry.display_name,
                description=entry.description,
                category=entry.category,
                status=entry.status,
                rating=entry.rating,
                tool_count=entry.tool_count,
                tags=entry.tags or []
            )
            for entry in results
        ]
        
        return APISearchResponse(
            query=query,
            results=search_results,
            total=total,
            page=page,
            per_page=per_page
        )
    
    def update_api(self, name: str, registration: APIRegistration) -> Optional[APIEntry]:
        """Update an existing API registration."""
        db_entry = self.db.query(APIEntryDB).filter(APIEntryDB.name == name).first()
        if not db_entry:
            return None
        
        # Update fields
        db_entry.display_name = registration.display_name
        db_entry.description = registration.description
        db_entry.openapi_url = str(registration.openapi_url)
        db_entry.base_url = str(registration.base_url)
        db_entry.category = registration.category
        db_entry.auth_config = registration.auth_config.model_dump()
        db_entry.tags = registration.tags or []
        db_entry.documentation_url = str(registration.documentation_url) if registration.documentation_url else None
        db_entry.contact_email = registration.contact_email
        db_entry.rate_limit = registration.rate_limit
        
        # Reset validation status to pending
        db_entry.status = APIStatus.validation_pending
        db_entry.validation_error = None
        
        self.db.commit()
        self.db.refresh(db_entry)
        
        return self._db_to_model(db_entry)
    
    def delete_api(self, name: str) -> bool:
        """Delete an API from the registry."""
        db_entry = self.db.query(APIEntryDB).filter(APIEntryDB.name == name).first()
        if not db_entry:
            return False
        
        self.db.delete(db_entry)
        self.db.commit()
        return True
    
    def get_categories(self) -> List[CategorySummary]:
        """Get all categories with API counts."""
        results = (
            self.db.query(APIEntryDB.category, func.count(APIEntryDB.id))
            .group_by(APIEntryDB.category)
            .all()
        )
        
        category_descriptions = {
            APICategory.development: "Development and programming tools",
            APICategory.productivity: "Productivity and workflow tools",
            APICategory.communication: "Communication and messaging services",
            APICategory.finance: "Financial and payment services",
            APICategory.ecommerce: "E-commerce and shopping platforms",
            APICategory.social: "Social media and networking",
            APICategory.media: "Media and content services",
            APICategory.analytics: "Analytics and data services",
            APICategory.infrastructure: "Infrastructure and cloud services",
            APICategory.other: "Other services"
        }
        
        return [
            CategorySummary(
                category=category,
                count=count,
                description=category_descriptions.get(category, "")
            )
            for category, count in results
        ]
    
    def get_stats(self) -> RegistryStats:
        """Get overall registry statistics."""
        total_apis = self.db.query(APIEntryDB).count()
        active_apis = self.db.query(APIEntryDB).filter(APIEntryDB.status == APIStatus.active).count()
        
        categories = self.get_categories()
        
        # Get most popular APIs (by usage count)
        popular_entries = (
            self.db.query(APIEntryDB)
            .filter(APIEntryDB.status == APIStatus.active)
            .order_by(APIEntryDB.usage_count.desc())
            .limit(5)
            .all()
        )
        
        most_popular = [
            APISearchResult(
                name=entry.name,
                display_name=entry.display_name,
                description=entry.description,
                category=entry.category,
                status=entry.status,
                rating=entry.rating,
                tool_count=entry.tool_count,
                tags=entry.tags or []
            )
            for entry in popular_entries
        ]
        
        return RegistryStats(
            total_apis=total_apis,
            active_apis=active_apis,
            categories=categories,
            most_popular=most_popular
        )
    
    def _db_to_model(self, db_entry: APIEntryDB) -> APIEntry:
        """Convert database entry to Pydantic model."""
        auth_config = AuthConfig(**db_entry.auth_config)
        
        return APIEntry(
            id=db_entry.id,
            name=db_entry.name,
            display_name=db_entry.display_name,
            description=db_entry.description,
            openapi_url=db_entry.openapi_url,
            base_url=db_entry.base_url,
            category=db_entry.category,
            auth_config=auth_config,
            tags=db_entry.tags or [],
            documentation_url=db_entry.documentation_url,
            contact_email=db_entry.contact_email,
            rate_limit=db_entry.rate_limit,
            created_at=db_entry.created_at,
            updated_at=db_entry.updated_at,
            status=db_entry.status,
            validation_error=db_entry.validation_error,
            tool_count=db_entry.tool_count,
            tools=db_entry.tools,
            last_validated=db_entry.last_validated,
            rating=db_entry.rating,
            usage_count=db_entry.usage_count
        )