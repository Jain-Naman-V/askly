from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .services.database import DatabaseService
from .services.ai_service import AIService
from .services.search_service import SearchService
from .services.data_processor import DataProcessor
from .routers import search, data, ai_agent
from .utils.config import get_settings
from .models.search_models import SearchQuery, SearchResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
db_service: DatabaseService = None
ai_service: AIService = None
search_service: SearchService = None
data_processor: DataProcessor = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_service, ai_service, search_service, data_processor
    settings = get_settings()
    
    logger.info("Starting up AI Data Agent...")
    
    # Initialize services
    db_service = DatabaseService(settings.get_mongodb_url(), settings.mongodb_db_name)
    await db_service.connect()
    
    ai_service = AIService(settings.groq_api_key, settings.groq_model)
    search_service = SearchService(db_service, ai_service)
    data_processor = DataProcessor(db_service, ai_service)
    
    # Create indexes
    await db_service.create_indexes()
    
    # Setup dependency overrides now that services are initialized
    setup_dependencies()
    
    logger.info("AI Data Agent started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Data Agent...")
    await db_service.close()

# Create FastAPI app
app = FastAPI(
    title="AI Data Agent",
    description="Intelligent agent for structured data interaction",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set up dependency overrides after app creation
# This will be populated during lifespan startup
def setup_dependencies():
    """Setup dependency overrides with initialized services"""
    # Override dependencies for search router
    app.dependency_overrides[search.get_db_service] = lambda: db_service
    app.dependency_overrides[search.get_search_service] = lambda: search_service
    app.dependency_overrides[search.get_ai_service] = lambda: ai_service
    
    # Override dependencies for data router
    app.dependency_overrides[data.get_db_service] = lambda: db_service
    app.dependency_overrides[data.get_data_processor] = lambda: data_processor
    app.dependency_overrides[data.get_ai_service] = lambda: ai_service
    
    # Override dependencies for ai_agent router
    app.dependency_overrides[ai_agent.get_ai_service] = lambda: ai_service
    app.dependency_overrides[ai_agent.get_db_service] = lambda: db_service
    app.dependency_overrides[ai_agent.get_search_service] = lambda: search_service

# Dependency injection
def get_db_service() -> DatabaseService:
    if db_service is None:
        raise HTTPException(status_code=503, detail="Database service not initialized")
    return db_service

def get_ai_service() -> AIService:
    if ai_service is None:
        raise HTTPException(status_code=503, detail="AI service not initialized")
    return ai_service

def get_search_service() -> SearchService:
    if search_service is None:
        raise HTTPException(status_code=503, detail="Search service not initialized")
    return search_service

def get_data_processor() -> DataProcessor:
    if data_processor is None:
        raise HTTPException(status_code=503, detail="Data processor not initialized")
    return data_processor

# Include routers
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(data.router, prefix="/api/v1/data", tags=["data"])
app.include_router(ai_agent.router, prefix="/api/v1/ai", tags=["ai"])

@app.get("/")
async def root():
    return {
        "message": "AI Data Agent API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = await db_service.health_check()
        
        # Check AI service
        ai_status = await ai_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "database": "connected" if db_status else "disconnected",
                "ai_service": "available" if ai_status else "unavailable"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "search":
                # Handle real-time search
                query = message_data.get("query", "")
                try:
                    # Stream search results
                    async for result in search_service.stream_search(query):
                        await websocket.send_text(json.dumps({
                            "type": "search_result",
                            "data": result
                        }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
            
            elif message_data.get("type") == "chat":
                # Handle AI chat
                query = message_data.get("message", "")
                try:
                    # Stream AI response
                    async for chunk in ai_service.stream_chat(query):
                        await websocket.send_text(json.dumps({
                            "type": "chat_response",
                            "data": chunk
                        }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

@app.post("/api/v1/smart-search")
async def smart_search(query: SearchQuery) -> SearchResponse:
    """Intelligent search endpoint with AI processing"""
    try:
        # Process query with AI
        processed_query = await ai_service.process_search_query(query.query)
        
        # Perform hybrid search
        results = await search_service.hybrid_search(
            processed_query.get("original_query", query.query),
            search_type=query.search_type,
            filters=query.filters,
            limit=query.limit,
            offset=query.offset
        )
        
        # Generate insights
        insights = await ai_service.generate_insights([r.dict() for r in results.results])
        results.insights = insights
        
        return results
    
    except Exception as e:
        logger.error(f"Smart search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/data/analyze")
async def analyze_data(
    background_tasks: BackgroundTasks,
    analysis_type: str = "summary"
):
    """Trigger data analysis in background"""
    try:
        background_tasks.add_task(
            perform_data_analysis,
            analysis_type
        )
        
        return {
            "message": f"Analysis '{analysis_type}' started",
            "status": "processing"
        }
    
    except Exception as e:
        logger.error(f"Analysis trigger error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def perform_data_analysis(analysis_type: str):
    """Background task for data analysis"""
    try:
        logger.info(f"Starting analysis: {analysis_type}")
        
        # Fetch data sample
        data = await db_service.get_sample_data(1000)
        
        # Perform analysis
        analysis_result = await ai_service.analyze_data(data, analysis_type)
        
        # Store results
        await db_service.store_analysis_result(analysis_type, analysis_result)
        
        # Broadcast to connected clients
        await manager.broadcast(json.dumps({
            "type": "analysis_complete",
            "analysis_type": analysis_type,
            "result": analysis_result
        }))
        
        logger.info(f"Analysis '{analysis_type}' completed")
    
    except Exception as e:
        logger.error(f"Background analysis error: {str(e)}")
        await manager.broadcast(json.dumps({
            "type": "analysis_error",
            "analysis_type": analysis_type,
            "error": str(e)
        }))

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )