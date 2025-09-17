from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class SearchType(str, Enum):
    """Search type enumeration"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    FUZZY = "fuzzy"
    EXACT = "exact"

class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"

class SearchQuery(BaseModel):
    """Search query model"""
    query: str = Field(..., description="Search query text")
    search_type: SearchType = Field(default=SearchType.HYBRID, description="Type of search")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    include_embedding: bool = Field(default=False, description="Include embeddings in response")
    include_score: bool = Field(default=True, description="Include relevance scores")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "find all users in New York",
                "search_type": "hybrid",
                "filters": {"category": "people", "status": "active"},
                "sort_by": "created_at",
                "sort_order": "desc",
                "limit": 20,
                "offset": 0
            }
        }

class SearchFilter(BaseModel):
    """Individual search filter"""
    field: str = Field(..., description="Field name to filter")
    operator: str = Field(..., description="Filter operator: eq, ne, gt, lt, gte, lte, in, nin, contains, regex")
    value: Any = Field(..., description="Filter value")
    case_sensitive: bool = Field(default=False, description="Case sensitive matching")

class AdvancedSearchQuery(BaseModel):
    """Advanced search query with multiple filters"""
    query: str = Field(..., description="Main search query")
    search_type: SearchType = Field(default=SearchType.HYBRID, description="Type of search")
    filters: List[SearchFilter] = Field(default_factory=list, description="Advanced filters")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    categories: Optional[List[str]] = Field(None, description="Category filters")
    tags: Optional[List[str]] = Field(None, description="Tag filters")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum relevance score")

class SearchResult(BaseModel):
    """Individual search result"""
    id: str = Field(..., description="Record ID")
    title: str = Field(..., description="Record title")
    description: Optional[str] = Field(None, description="Record description")
    content: Dict[str, Any] = Field(..., description="Record content")
    tags: List[str] = Field(default_factory=list, description="Record tags")
    category: Optional[str] = Field(None, description="Record category")
    score: float = Field(..., description="Relevance score")
    highlights: Dict[str, List[str]] = Field(default_factory=dict, description="Search highlights")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    
class SearchResponse(BaseModel):
    """Search response model"""
    query: str = Field(..., description="Original search query")
    search_type: SearchType = Field(..., description="Search type used")
    results: List[SearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total number of matching results")
    returned_count: int = Field(..., description="Number of results returned")
    offset: int = Field(..., description="Result offset")
    limit: int = Field(..., description="Result limit")
    processing_time: float = Field(..., description="Query processing time in seconds")
    suggestions: List[str] = Field(default_factory=list, description="Query suggestions")
    facets: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Search facets")
    insights: Optional[Dict[str, Any]] = Field(None, description="AI-generated insights")
    
class SearchSuggestion(BaseModel):
    """Search suggestion model"""
    text: str = Field(..., description="Suggested query text")
    type: str = Field(..., description="Suggestion type")
    confidence: float = Field(..., description="Suggestion confidence score")
    context: Optional[str] = Field(None, description="Suggestion context")

class SearchFacet(BaseModel):
    """Search facet model"""
    field: str = Field(..., description="Facet field name")
    values: Dict[str, int] = Field(..., description="Facet values and counts")
    total_count: int = Field(..., description="Total facet count")

class SavedSearch(BaseModel):
    """Saved search model"""
    id: Optional[str] = Field(None, description="Search ID")
    name: str = Field(..., description="Search name")
    description: Optional[str] = Field(None, description="Search description")
    query: SearchQuery = Field(..., description="Search query")
    created_by: Optional[str] = Field(None, description="User who created the search")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_used: Optional[datetime] = Field(None, description="Last used timestamp")
    use_count: int = Field(default=0, description="Number of times used")
    is_public: bool = Field(default=False, description="Whether search is public")

class SearchAnalytics(BaseModel):
    """Search analytics model"""
    total_searches: int = Field(..., description="Total number of searches")
    unique_queries: int = Field(..., description="Number of unique queries")
    popular_queries: List[Dict[str, Any]] = Field(..., description="Most popular queries")
    popular_filters: List[Dict[str, Any]] = Field(..., description="Most used filters")
    average_results: float = Field(..., description="Average number of results per query")
    zero_result_queries: List[str] = Field(..., description="Queries with no results")
    performance_metrics: Dict[str, float] = Field(..., description="Performance metrics")
    
class RealtimeSearchUpdate(BaseModel):
    """Real-time search update model"""
    type: str = Field(..., description="Update type: new_result, updated_result, deleted_result")
    data: Dict[str, Any] = Field(..., description="Update data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")
    affected_queries: List[str] = Field(default_factory=list, description="Affected search queries")