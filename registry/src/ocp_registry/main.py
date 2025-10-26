"""FastAPI application for OCP Community Registry."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .database import get_db, db_manager
from .models import (
    APIRegistration, APIEntry, APISearchResponse, ValidationRequest,
    ValidationResult, CategorySummary, RegistryStats, APICategory, APIStatus
)
from .service import RegistryService
from .validator import validator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    db_manager.create_tables()
    yield


# Create FastAPI app
app = FastAPI(
    title="OCP Community Registry",
    description="Searchable database of API configurations for the Open Context Protocol",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Registry endpoints
@app.get("/api/v1/registry", response_model=List[APIEntry])
async def list_apis(
    category: Optional[APICategory] = Query(None, description="Filter by category"),
    status: Optional[APIStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """List all registered APIs with optional filtering."""
    service = RegistryService(db)
    return service.list_apis(category=category, status=status)


@app.get("/api/v1/registry/{name}", response_model=APIEntry)
async def get_api(name: str, db: Session = Depends(get_db)):
    """Get specific API configuration by name."""
    service = RegistryService(db)
    api_entry = service.get_api(name)
    if not api_entry:
        raise HTTPException(status_code=404, detail=f"API '{name}' not found")
    
    # Increment usage count
    api_entry.usage_count += 1
    # Note: In a real implementation, we'd update this in the database
    
    return api_entry


@app.post("/api/v1/registry", response_model=APIEntry, status_code=201)
async def register_api(registration: APIRegistration, db: Session = Depends(get_db)):
    """Register a new API in the registry."""
    service = RegistryService(db)
    try:
        return await service.register_api(registration)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")


@app.put("/api/v1/registry/{name}", response_model=APIEntry)
async def update_api(
    name: str, 
    registration: APIRegistration, 
    db: Session = Depends(get_db)
):
    """Update an existing API registration."""
    service = RegistryService(db)
    api_entry = service.update_api(name, registration)
    if not api_entry:
        raise HTTPException(status_code=404, detail=f"API '{name}' not found")
    return api_entry


@app.delete("/api/v1/registry/{name}")
async def delete_api(name: str, db: Session = Depends(get_db)):
    """Remove an API from the registry."""
    service = RegistryService(db)
    if not service.delete_api(name):
        raise HTTPException(status_code=404, detail=f"API '{name}' not found")
    return {"message": f"API '{name}' deleted successfully"}


# Search and discovery endpoints
@app.get("/api/v1/search", response_model=APISearchResponse)
async def search_apis(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """Search APIs by name, description, or tags."""
    service = RegistryService(db)
    return service.search_apis(q, page=page, per_page=per_page)


@app.get("/api/v1/categories", response_model=List[CategorySummary])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories with API counts."""
    service = RegistryService(db)
    return service.get_categories()


@app.get("/api/v1/categories/{category}", response_model=List[APIEntry])
async def get_apis_by_category(category: APICategory, db: Session = Depends(get_db)):
    """Get all APIs in a specific category."""
    service = RegistryService(db)
    return service.list_apis(category=category, status=APIStatus.active)


# Validation endpoints
@app.post("/api/v1/validate", response_model=ValidationResult)
async def validate_api_spec(request: ValidationRequest):
    """Validate an OpenAPI specification and endpoint."""
    return await validator.validate_api(request)


@app.get("/api/v1/registry/{name}/status", response_model=ValidationResult)
async def check_api_status(name: str, db: Session = Depends(get_db)):
    """Check the current validation status of an API."""
    service = RegistryService(db)
    api_entry = service.get_api(name)
    if not api_entry:
        raise HTTPException(status_code=404, detail=f"API '{name}' not found")
    
    # Re-validate the API
    validation_request = ValidationRequest(
        openapi_url=api_entry.openapi_url,
        base_url=api_entry.base_url
    )
    return await validator.validate_api(validation_request)


# Statistics endpoint
@app.get("/api/v1/stats", response_model=RegistryStats)
async def get_registry_stats(db: Session = Depends(get_db)):
    """Get overall registry statistics."""
    service = RegistryService(db)
    return service.get_stats()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ocp-registry"}


# Root redirect
@app.get("/")
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "OCP Community Registry",
        "docs": "/docs",
        "api": "/api/v1"
    }


def main():
    """Entry point for running the registry server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()