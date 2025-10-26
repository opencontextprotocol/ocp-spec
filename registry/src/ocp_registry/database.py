"""Database models and configuration for OCP Registry."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum as SQLEnum, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import enum

from .models import APICategory, APIStatus, AuthType

Base = declarative_base()


class APIEntryDB(Base):
    """Database model for API registry entries."""
    __tablename__ = "api_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    openapi_url = Column(String(500), nullable=False)
    base_url = Column(String(500), nullable=False)
    category = Column(SQLEnum(APICategory), nullable=False, index=True)
    
    # Auth configuration stored as JSON
    auth_config = Column(JSON, nullable=False)
    
    # Metadata
    tags = Column(JSON, default=list)
    documentation_url = Column(String(500))
    contact_email = Column(String(255))
    rate_limit = Column(String(100))
    
    # Status and validation
    status = Column(SQLEnum(APIStatus), default=APIStatus.validation_pending, index=True)
    validation_error = Column(Text)
    tool_count = Column(Integer)
    tools = Column(JSON)  # Pre-discovered OCP tools
    last_validated = Column(DateTime)
    
    # Community metrics
    rating = Column(Float)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, database_url: str = "sqlite:///./registry.db"):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Global database manager instance
db_manager = DatabaseManager()


def get_db():
    """Dependency for FastAPI to get database session."""
    return next(db_manager.get_session())