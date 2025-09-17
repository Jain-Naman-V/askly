from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from ..services.ai_service import AIService
from ..services.database import DatabaseService
from ..services.search_service import SearchService

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request bodies
class ChatRequest(BaseModel):
    message: str
    context_records: Optional[List[str]] = None

class ProcessQueryRequest(BaseModel):
    query: str

class GenerateInsightsRequest(BaseModel):
    record_ids: Optional[List[str]] = None
    search_query: Optional[str] = None
    limit: int = 100

class AnalyzeDataRequest(BaseModel):
    analysis_type: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 1000

class GenerateEmbeddingsRequest(BaseModel):
    texts: List[str]

# Dependency injection placeholders
def get_ai_service() -> AIService:
    pass

def get_db_service() -> DatabaseService:
    pass

def get_search_service() -> SearchService:
    pass

@router.post("/chat")
async def ai_chat(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service),
    db_service: DatabaseService = Depends(get_db_service)
):
    """AI chat endpoint for conversational interaction"""
    try:
        # Check if user is asking for data analysis
        query_lower = request.message.lower()
        analysis_keywords = ['analyze', 'trends', 'patterns', 'insights', 'summary', 'overview']
        
        context_data = []
        
        # If asking for analysis, fetch actual data from MongoDB
        if any(keyword in query_lower for keyword in analysis_keywords):
            # Get recent data from the database
            search_results = await db_service.search_records(
                query="",
                filters={},
                limit=100,
                offset=0
            )
            
            # Convert to context data
            context_data = [record.dict() for record in search_results["data"]]
            
            # Also get analytics summary
            analytics = await db_service.get_analytics()
            
            # Add analytics context
            analytics_context = {
                "total_records": analytics.get("total_records", 0),
                "categories": analytics.get("categories", {}),
                "recent_activity": f"Database contains {analytics.get('total_records', 0)} records across {len(analytics.get('categories', {}))} categories"
            }
            context_data.append(analytics_context)
            
        # Add any provided context records
        if request.context_records:
            for record_id in request.context_records:
                record = await db_service.get_record(record_id)
                if record:
                    context_data.append(record.dict())
        
        # Generate AI response with actual data context
        response_chunks = []
        async for chunk in ai_service.stream_chat(request.message, context_data):
            response_chunks.append(chunk)
        
        full_response = "".join(response_chunks)
        
        return {
            "response": full_response,
            "timestamp": datetime.utcnow().isoformat(),
            "context_count": len(context_data),
            "processing_time": 100,  # TODO: Add actual timing
            "confidence": 0.85  # TODO: Add actual confidence scoring
        }
        
    except Exception as e:
        logger.error(f"AI chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-query")
async def process_natural_language_query(
    request: ProcessQueryRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Process natural language query into structured search parameters"""
    try:
        processed_query = await ai_service.process_search_query(request.query)
        return processed_query
        
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-insights")
async def generate_insights(
    request: GenerateInsightsRequest,
    ai_service: AIService = Depends(get_ai_service),
    db_service: DatabaseService = Depends(get_db_service),
    search_service: SearchService = Depends(get_search_service)
):
    """Generate AI insights from data"""
    try:
        # Get data for analysis
        data = []
        
        if request.record_ids:
            # Get specific records
            for record_id in request.record_ids:
                record = await db_service.get_record(record_id)
                if record:
                    data.append(record.dict())
        elif request.search_query:
            # Get data from search results
            search_results = await search_service.hybrid_search(
                query=request.search_query,
                limit=request.limit
            )
            data = [result.dict() for result in search_results.results]
        else:
            # Get sample data
            sample_data = await db_service.get_sample_data(request.limit)
            data = sample_data
        
        if not data:
            return {"error": "No data found for analysis"}
        
        # Generate insights
        insights = await ai_service.generate_insights(data)
        
        return insights
        
    except Exception as e:
        logger.error(f"Insights generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_data(
    request: AnalyzeDataRequest,
    ai_service: AIService = Depends(get_ai_service),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Perform AI-powered data analysis"""
    try:
        # Get data for analysis
        search_results = await db_service.search_records(
            query="",
            filters=request.filters,
            limit=request.limit
        )
        
        data = [record.dict() for record in search_results["data"]]
        
        if not data:
            return {"error": "No data found matching filters"}
        
        # Perform analysis
        analysis_result = await ai_service.analyze_data(data, request.analysis_type)
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Data analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-embeddings")
async def generate_embeddings(
    request: GenerateEmbeddingsRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate embeddings for text data"""
    try:
        embeddings = ai_service.generate_embeddings(request.texts)
        
        return {
            "embeddings": embeddings.tolist() if embeddings.size > 0 else [],
            "count": len(request.texts),
            "dimension": embeddings.shape[1] if embeddings.size > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Embedding generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions/queries")
async def get_query_suggestions(
    context: Optional[str] = None,
    ai_service: AIService = Depends(get_ai_service),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get AI-generated query suggestions"""
    try:
        # Get data schema for context
        analytics = await db_service.get_analytics()
        
        data_schema = {
            "categories": analytics.get("categories", []),
            "total_records": analytics.get("total_records", 0),
            "context": context
        }
        
        suggestions = await ai_service.suggest_queries(data_schema)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Query suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def ai_health_check(
    ai_service: AIService = Depends(get_ai_service)
):
    """Check AI service health"""
    try:
        is_healthy = await ai_service.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ai_agent"
        }
        
    except Exception as e:
        logger.error(f"AI health check error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ai_agent"
        }