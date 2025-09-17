from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from ..models.search_models import (
    SearchQuery, SearchResponse, AdvancedSearchQuery, 
    SearchType, SortOrder, SavedSearch, SearchAnalytics
)
from ..services.database import DatabaseService
from ..services.search_service import SearchService
from ..services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection placeholders (will be injected in main.py)
def get_db_service() -> DatabaseService:
    pass

def get_search_service() -> SearchService:
    pass

def get_ai_service() -> AIService:
    pass

@router.post("/", response_model=SearchResponse)
async def search_records(
    query: SearchQuery,
    db_service: DatabaseService = Depends(get_db_service),
    search_service: SearchService = Depends(get_search_service)
):
    """Basic search endpoint"""
    try:
        result = await search_service.hybrid_search(
            query=query.query,
            search_type=query.search_type,
            filters=query.filters,
            limit=query.limit,
            offset=query.offset
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/advanced", response_model=SearchResponse)
async def advanced_search(
    query: AdvancedSearchQuery,
    search_service: SearchService = Depends(get_search_service)
):
    """Advanced search with complex filters"""
    try:
        # Convert advanced filters to simple filters
        filters = {}
        
        # Process individual filters
        for search_filter in query.filters:
            if search_filter.operator == "eq":
                filters[search_filter.field] = search_filter.value
            elif search_filter.operator == "ne":
                filters[search_filter.field] = {"$ne": search_filter.value}
            elif search_filter.operator == "gt":
                filters[search_filter.field] = {"$gt": search_filter.value}
            elif search_filter.operator == "lt":
                filters[search_filter.field] = {"$lt": search_filter.value}
            elif search_filter.operator == "gte":
                filters[search_filter.field] = {"$gte": search_filter.value}
            elif search_filter.operator == "lte":
                filters[search_filter.field] = {"$lte": search_filter.value}
            elif search_filter.operator == "in":
                filters[search_filter.field] = {"$in": search_filter.value}
            elif search_filter.operator == "nin":
                filters[search_filter.field] = {"$nin": search_filter.value}
            elif search_filter.operator == "contains":
                options = "i" if not search_filter.case_sensitive else ""
                filters[search_filter.field] = {"$regex": str(search_filter.value), "$options": options}
        
        # Add date range filter
        if query.date_range:
            if "start" in query.date_range:
                filters["created_at"] = {"$gte": query.date_range["start"]}
            if "end" in query.date_range:
                filters.setdefault("created_at", {})["$lte"] = query.date_range["end"]
        
        # Add category filters
        if query.categories:
            filters["category"] = {"$in": query.categories}
        
        # Add tag filters
        if query.tags:
            filters["tags"] = {"$in": query.tags}
        
        result = await search_service.hybrid_search(
            query=query.query,
            search_type=query.search_type,
            filters=filters,
            limit=query.limit,
            offset=query.offset,
            min_score=query.min_score
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Advanced search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., description="Partial query for suggestions"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions"),
    ai_service: AIService = Depends(get_ai_service),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get search suggestions based on partial query"""
    try:
        analytics = await db_service.get_analytics()
        
        suggestions = await ai_service.suggest_queries({
            "partial_query": query,
            "categories": analytics.get("categories", []),
            "limit": limit
        })
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Search suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/facets")
async def get_search_facets(
    query: str = Query("", description="Search query for facets"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get search facets for filtering"""
    try:
        results = await db_service.search_records(query=query, limit=1000)
        
        facets = {
            "categories": {},
            "tags": {},
            "status": {}
        }
        
        for record in results["data"]:
            if record.category:
                facets["categories"][record.category] = \
                    facets["categories"].get(record.category, 0) + 1
            
            for tag in record.tags:
                facets["tags"][tag] = facets["tags"].get(tag, 0) + 1
            
            status = getattr(record, 'status', 'active')
            facets["status"][status] = facets["status"].get(status, 0) + 1
        
        return {"facets": facets}
        
    except Exception as e:
        logger.error(f"Search facets error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))