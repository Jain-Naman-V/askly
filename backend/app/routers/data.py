from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging

from ..models.data_models import (
    DataRecord, DataRecordCreate, DataRecordUpdate, DataRecordResponse,
    BulkDataOperation, DataAnalytics, DataExportRequest, DataImportRequest
)
from ..services.database import DatabaseService
from ..services.data_processor import DataProcessor
from ..services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter()

# Pagination response model
class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[DataRecordResponse]
    pagination: Dict[str, Any]
    total_count: int
    returned_count: int

# Dependency injection placeholders
def get_db_service() -> DatabaseService:
    pass

def get_data_processor() -> DataProcessor:
    pass

def get_ai_service() -> AIService:
    pass

@router.post("/", response_model=DataRecordResponse)
async def create_record(
    record: DataRecordCreate,
    created_by: Optional[str] = None,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new data record"""
    try:
        result = await db_service.create_record(record, created_by)
        return DataRecordResponse(**result.dict())
        
    except Exception as e:
        logger.error(f"Record creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedResponse)
async def list_records(
    limit: int = 10,  # Changed default to 10 for pagination
    offset: int = 0,
    page: Optional[int] = None,  # Page-based pagination
    category: Optional[str] = None,
    db_service: DatabaseService = Depends(get_db_service)
):
    """List all records with pagination and optional filtering"""
    try:
        # Handle page-based pagination (convert to offset-based)
        if page is not None and page > 0:
            offset = (page - 1) * limit
        
        # Build filters
        filters = {}
        if category:
            filters["category"] = category
        
        # Get records
        results = await db_service.search_records(
            query="",
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        records = [DataRecordResponse(**record.dict()) for record in results["data"]]
        
        # Calculate pagination info
        total_count = results["total_count"]
        current_page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
        has_next = offset + limit < total_count
        has_prev = offset > 0
        
        pagination_info = {
            "current_page": current_page,
            "total_pages": total_pages,
            "page_size": limit,
            "offset": offset,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": current_page + 1 if has_next else None,
            "prev_page": current_page - 1 if has_prev else None
        }
        
        return PaginatedResponse(
            data=records,
            pagination=pagination_info,
            total_count=total_count,
            returned_count=len(records)
        )
        
    except Exception as e:
        logger.error(f"Record listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{record_id}", response_model=DataRecordResponse)
async def get_record(
    record_id: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get a record by ID"""
    try:
        record = await db_service.get_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return DataRecordResponse(**record.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{record_id}", response_model=DataRecordResponse)
async def update_record(
    record_id: str,
    record_update: DataRecordUpdate,
    updated_by: Optional[str] = None,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Update a record"""
    try:
        result = await db_service.update_record(record_id, record_update, updated_by)
        if not result:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return DataRecordResponse(**result.dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{record_id}")
async def delete_record(
    record_id: str,
    soft_delete: bool = True,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Delete a record"""
    try:
        success = await db_service.delete_record(record_id, soft_delete)
        if not success:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return {"message": "Record deleted successfully", "record_id": record_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk")
async def bulk_operation(
    operation: BulkDataOperation,
    created_by: Optional[str] = None,
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Perform bulk operations on data"""
    try:
        result = await data_processor.process_bulk_data(operation, created_by)
        return result
        
    except Exception as e:
        logger.error(f"Bulk operation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    file_format: str = Form(...),
    mapping: Optional[str] = Form(None),
    created_by: Optional[str] = Form(None),
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Import data from file"""
    try:
        file_content = await file.read()
        
        # Parse mapping if provided
        import json
        mapping_dict = None
        if mapping:
            mapping_dict = json.loads(mapping)
        
        result = await data_processor.import_data(
            file_content=file_content,
            file_format=file_format,
            mapping=mapping_dict,
            created_by=created_by
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Data import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/summary", response_model=DataAnalytics)
async def get_analytics(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get data analytics summary"""
    try:
        analytics = await db_service.get_analytics()
        
        return DataAnalytics(
            total_records=analytics.get("total_records", 0),
            active_records=analytics.get("active_records", 0),
            categories=analytics.get("categories", {}),
            tags_distribution={},
            data_types={},
            created_today=analytics.get("created_today", 0),
            updated_today=analytics.get("updated_today", 0),
            most_active_users=[]
        )
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/categories")
async def get_category_stats(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get category statistics"""
    try:
        # Get category distribution from the database
        pipeline = [
            {"$group": {
                "_id": "$category", 
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        # Execute aggregation
        collection = db_service.collection
        results = await collection.aggregate(pipeline).to_list(None)
        
        # Format results
        categories = {}
        for result in results:
            if result["_id"]:
                categories[result["_id"]] = result["count"]
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Category stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/time-distribution")
async def get_time_distribution(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get time-based distribution of data"""
    try:
        # Get time distribution from the database
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d", 
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": -1}},
            {"$limit": 30}  # Last 30 days
        ]
        
        # Execute aggregation
        collection = db_service.collection
        results = await collection.aggregate(pipeline).to_list(None)
        
        # Format results
        distribution = {}
        for result in results:
            if result["_id"]:
                distribution[result["_id"]] = result["count"]
        
        return {"distribution": distribution}
        
    except Exception as e:
        logger.error(f"Time distribution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_record(
    record_data: Dict[str, Any],
    data_processor: DataProcessor = Depends(get_data_processor)
):
    """Validate record data"""
    try:
        validation_result = await data_processor.validate_record(record_data)
        return validation_result.dict()
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))