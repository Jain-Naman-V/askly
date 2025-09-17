from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import uuid

class DataStatus(str, Enum):
    """Data status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    PROCESSING = "processing"
    ERROR = "error"

class DataType(str, Enum):
    """Data type enumeration"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    IMAGE = "image"
    FILE = "file"

class DataRecord(BaseModel):
    """Main data record model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    title: str = Field(..., description="Record title")
    description: Optional[str] = Field(None, description="Record description")
    content: Dict[str, Any] = Field(..., description="Record content data")
    tags: List[str] = Field(default_factory=list, description="Record tags")
    category: Optional[str] = Field(None, description="Record category")
    status: DataStatus = Field(default=DataStatus.ACTIVE, description="Record status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")
    
    # Search and AI fields
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for search")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    search_text: Optional[str] = Field(None, description="Combined searchable text")
    score: Optional[float] = Field(None, description="Search relevance score")
    
    # User tracking
    created_by: Optional[str] = Field(None, description="User who created the record")
    updated_by: Optional[str] = Field(None, description="User who last updated the record")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "title": "Sample Data Record",
                "description": "This is a sample data record",
                "content": {
                    "name": "John Doe",
                    "age": 30,
                    "city": "New York"
                },
                "tags": ["sample", "demo"],
                "category": "people",
                "status": "active"
            }
        }

class DataRecordCreate(BaseModel):
    """Model for creating new data records"""
    title: str = Field(..., description="Record title")
    description: Optional[str] = Field(None, description="Record description")
    content: Dict[str, Any] = Field(..., description="Record content data")
    tags: List[str] = Field(default_factory=list, description="Record tags")
    category: Optional[str] = Field(None, description="Record category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DataRecordUpdate(BaseModel):
    """Model for updating data records"""
    title: Optional[str] = Field(None, description="Record title")
    description: Optional[str] = Field(None, description="Record description")
    content: Optional[Dict[str, Any]] = Field(None, description="Record content data")
    tags: Optional[List[str]] = Field(None, description="Record tags")
    category: Optional[str] = Field(None, description="Record category")
    status: Optional[DataStatus] = Field(None, description="Record status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class DataRecordResponse(BaseModel):
    """Response model for data records"""
    id: str
    title: str
    description: Optional[str]
    content: Dict[str, Any]
    tags: List[str]
    category: Optional[str]
    status: DataStatus
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    score: Optional[float] = Field(None, description="Search relevance score")
    score: Optional[float] = Field(None, description="Search relevance score")

class DataRecordSearchResult(BaseModel):
    """Search result model with score"""
    id: str
    title: str
    description: Optional[str]
    content: Dict[str, Any]
    tags: List[str]
    category: Optional[str]
    status: DataStatus
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    score: float = Field(..., description="Search relevance score")

class BulkDataOperation(BaseModel):
    """Model for bulk operations"""
    operation: str = Field(..., description="Operation type: insert, update, delete")
    records: List[Dict[str, Any]] = Field(..., description="List of records")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters for bulk operations")

class DataSchema(BaseModel):
    """Model for data schema definition"""
    field_name: str = Field(..., description="Field name")
    field_type: DataType = Field(..., description="Field data type")
    required: bool = Field(default=False, description="Whether field is required")
    description: Optional[str] = Field(None, description="Field description")
    default_value: Optional[Any] = Field(None, description="Default value")
    validation_rules: Dict[str, Any] = Field(default_factory=dict, description="Validation rules")

class DataValidationResult(BaseModel):
    """Model for data validation results"""
    is_valid: bool = Field(..., description="Whether data is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

class DataAnalytics(BaseModel):
    """Model for data analytics results"""
    total_records: int = Field(..., description="Total number of records")
    active_records: int = Field(..., description="Number of active records")
    categories: Dict[str, int] = Field(default_factory=dict, description="Records per category")
    tags_distribution: Dict[str, int] = Field(default_factory=dict, description="Tag distribution")
    data_types: Dict[str, int] = Field(default_factory=dict, description="Data type distribution")
    created_today: int = Field(default=0, description="Records created today")
    updated_today: int = Field(default=0, description="Records updated today")
    most_active_users: List[Dict[str, Any]] = Field(default_factory=list, description="Most active users")
    
class DataExportRequest(BaseModel):
    """Model for data export requests"""
    format: str = Field(..., description="Export format: json, csv, xlsx")
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    fields: Optional[List[str]] = Field(None, description="Fields to include")
    include_metadata: bool = Field(default=True, description="Include metadata")
    
class DataImportRequest(BaseModel):
    """Model for data import requests"""
    format: str = Field(..., description="Import format: json, csv, xlsx")
    data: Union[str, List[Dict[str, Any]]] = Field(..., description="Data to import")
    mapping: Optional[Dict[str, str]] = Field(None, description="Field mapping")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing records")