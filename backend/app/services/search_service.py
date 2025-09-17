import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import time

from .database import DatabaseService
from .ai_service import AIService
from ..models.search_models import SearchQuery, SearchResult, SearchResponse, SearchType
from ..utils.helpers import calculate_similarity_score, extract_keywords

logger = logging.getLogger(__name__)

class SearchService:
    """Advanced search service with hybrid capabilities"""
    
    def __init__(self, db_service: DatabaseService, ai_service: AIService):
        self.db_service = db_service
        self.ai_service = ai_service
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
        
    async def hybrid_search(
        self,
        query: str,
        search_type: SearchType = SearchType.HYBRID,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
        min_score: float = 0.0
    ) -> SearchResponse:
        """Perform hybrid search combining multiple search strategies"""
        start_time = time.time()
        
        try:
            # Process query with AI if needed
            processed_query = query
            if search_type in [SearchType.SEMANTIC, SearchType.HYBRID]:
                ai_processed = await self.ai_service.process_search_query(query)
                if ai_processed.get("keywords"):
                    processed_query = " ".join(ai_processed["keywords"])
            
            # Perform different types of searches based on search_type
            if search_type == SearchType.SEMANTIC:
                results = await self._semantic_search(processed_query, filters, limit, offset)
            elif search_type == SearchType.KEYWORD:
                results = await self._keyword_search(processed_query, filters, limit, offset)
            elif search_type == SearchType.FUZZY:
                results = await self._fuzzy_search(processed_query, filters, limit, offset)
            elif search_type == SearchType.EXACT:
                results = await self._exact_search(processed_query, filters, limit, offset)
            else:  # HYBRID
                results = await self._hybrid_search_combined(processed_query, filters, limit, offset)
            
            # Filter by minimum score
            if min_score > 0.0:
                filtered_data = []
                for r in results["data"]:
                    score = getattr(r, 'score', 0.0)
                    if score >= min_score:
                        filtered_data.append(r)
                results["data"] = filtered_data
                results["returned_count"] = len(filtered_data)
            
            # Generate search results
            search_results = []
            for record in results["data"]:
                search_result = SearchResult(
                    id=record.id,
                    title=record.title,
                    description=record.description,
                    content=record.content,
                    tags=record.tags,
                    category=record.category,
                    score=getattr(record, 'score', 0.0),
                    highlights=self._generate_highlights(record, query),
                    metadata=record.metadata,
                    created_at=record.created_at
                )
                search_results.append(search_result)
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(query, results["data"])
            
            # Generate facets
            facets = self._generate_facets(results["data"])
            
            processing_time = time.time() - start_time
            
            return SearchResponse(
                query=query,
                search_type=search_type,
                results=search_results,
                total_count=results["total_count"],
                returned_count=len(search_results),
                offset=offset,
                limit=limit,
                processing_time=processing_time,
                suggestions=suggestions,
                facets=facets
            )
            
        except Exception as e:
            logger.error(f"Hybrid search error: {str(e)}")
            return SearchResponse(
                query=query,
                search_type=search_type,
                results=[],
                total_count=0,
                returned_count=0,
                offset=offset,
                limit=limit,
                processing_time=time.time() - start_time,
                suggestions=[],
                facets={}
            )

    async def _semantic_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int,
        offset: int
    ) -> Dict[str, Any]:
        """Perform semantic search using embeddings"""
        try:
            # Generate query embedding
            query_embedding = self.ai_service.generate_embeddings([query])[0]
            
            # Get all records (this could be optimized with vector search in production)
            all_records = await self.db_service.search_records(
                query="",
                filters=filters,
                limit=1000,  # Get more records for semantic comparison
                offset=0
            )
            
            # Calculate semantic similarity for records with embeddings
            scored_records = []
            for record in all_records["data"]:
                if hasattr(record, 'embedding') and record.embedding:
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        [query_embedding],
                        [record.embedding]
                    )[0][0]
                    # Add score attribute to record
                    setattr(record, 'score', float(similarity))
                    scored_records.append(record)
                else:
                    # Fallback to text similarity
                    text_content = f"{record.title} {record.description or ''}"
                    similarity = calculate_similarity_score(query, text_content)
                    # Add score attribute to record
                    setattr(record, 'score', similarity)
                    scored_records.append(record)
            
            # Sort by score and apply pagination
            scored_records.sort(key=lambda x: getattr(x, 'score', 0.0), reverse=True)
            paginated_records = scored_records[offset:offset + limit]
            
            return {
                "data": paginated_records,
                "total_count": len(scored_records),
                "offset": offset,
                "limit": limit,
                "returned_count": len(paginated_records)
            }
            
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return await self._keyword_search(query, filters, limit, offset)

    async def _keyword_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int,
        offset: int
    ) -> Dict[str, Any]:
        """Perform keyword-based search"""
        return await self.db_service.search_records(
            query=query,
            filters=filters,
            limit=limit,
            offset=offset
        )

    async def _fuzzy_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int,
        offset: int
    ) -> Dict[str, Any]:
        """Perform fuzzy search with typo tolerance"""
        try:
            # Extract keywords and create variations
            keywords = extract_keywords(query)
            expanded_query = " OR ".join(keywords)
            
            # Use MongoDB regex for fuzzy matching
            fuzzy_filters = filters.copy() if filters else {}
            
            # Add fuzzy text search
            if keywords:
                fuzzy_patterns = []
                for keyword in keywords:
                    # Create regex pattern for fuzzy matching
                    pattern = f".*{keyword}.*"
                    fuzzy_patterns.append(pattern)
                
                fuzzy_filters["$or"] = [
                    {"title": {"$regex": "|".join(fuzzy_patterns), "$options": "i"}},
                    {"description": {"$regex": "|".join(fuzzy_patterns), "$options": "i"}},
                    {"search_text": {"$regex": "|".join(fuzzy_patterns), "$options": "i"}}
                ]
            
            return await self.db_service.search_records(
                query="",  # Don't use text search
                filters=fuzzy_filters,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logger.error(f"Fuzzy search error: {str(e)}")
            return await self._keyword_search(query, filters, limit, offset)

    async def _exact_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int,
        offset: int
    ) -> Dict[str, Any]:
        """Perform exact phrase search"""
        try:
            exact_filters = filters.copy() if filters else {}
            
            # Add exact phrase search
            exact_filters["$or"] = [
                {"title": {"$regex": f"\\b{query}\\b", "$options": "i"}},
                {"description": {"$regex": f"\\b{query}\\b", "$options": "i"}},
                {"search_text": {"$regex": f"\\b{query}\\b", "$options": "i"}}
            ]
            
            return await self.db_service.search_records(
                query="",
                filters=exact_filters,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logger.error(f"Exact search error: {str(e)}")
            return await self._keyword_search(query, filters, limit, offset)

    async def _hybrid_search_combined(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int,
        offset: int
    ) -> Dict[str, Any]:
        """Combine multiple search strategies for best results"""
        try:
            # Perform multiple search types
            keyword_results = await self._keyword_search(query, filters, limit * 2, 0)
            semantic_results = await self._semantic_search(query, filters, limit * 2, 0)
            
            # Combine and deduplicate results
            combined_results = {}
            
            # Add keyword results with boost
            for record in keyword_results["data"]:
                score = getattr(record, 'score', 0.5)
                combined_results[record.id] = {
                    "record": record,
                    "score": score * 1.2  # Boost keyword matches
                }
            
            # Add semantic results
            for record in semantic_results["data"]:
                score = getattr(record, 'score', 0.0)
                if record.id in combined_results:
                    # Combine scores
                    combined_results[record.id]["score"] += score
                else:
                    combined_results[record.id] = {
                        "record": record,
                        "score": score
                    }
            
            # Sort by combined score
            sorted_results = sorted(
                combined_results.values(),
                key=lambda x: x["score"],
                reverse=True
            )
            
            # Apply pagination
            paginated_results = sorted_results[offset:offset + limit]
            final_records = []
            
            for result in paginated_results:
                record = result["record"]
                record.score = result["score"]
                final_records.append(record)
            
            return {
                "data": final_records,
                "total_count": len(sorted_results),
                "offset": offset,
                "limit": limit,
                "returned_count": len(final_records)
            }
            
        except Exception as e:
            logger.error(f"Hybrid search error: {str(e)}")
            return await self._keyword_search(query, filters, limit, offset)

    def _generate_highlights(self, record: Any, query: str) -> Dict[str, List[str]]:
        """Generate search highlights for results"""
        highlights = {}
        keywords = extract_keywords(query)
        
        try:
            # Check title
            title_highlights = []
            for keyword in keywords:
                if keyword.lower() in record.title.lower():
                    highlighted = record.title.replace(
                        keyword, f"<mark>{keyword}</mark>"
                    )
                    title_highlights.append(highlighted)
            
            if title_highlights:
                highlights["title"] = title_highlights
            
            # Check description
            if record.description:
                desc_highlights = []
                for keyword in keywords:
                    if keyword.lower() in record.description.lower():
                        highlighted = record.description.replace(
                            keyword, f"<mark>{keyword}</mark>"
                        )
                        desc_highlights.append(highlighted)
                
                if desc_highlights:
                    highlights["description"] = desc_highlights
            
            return highlights
            
        except Exception as e:
            logger.error(f"Highlight generation error: {str(e)}")
            return {}

    async def _generate_suggestions(self, query: str, results: List[Any]) -> List[str]:
        """Generate search suggestions based on query and results"""
        try:
            suggestions = []
            
            # Extract common categories and tags from results
            categories = set()
            tags = set()
            
            for record in results[:10]:  # Use top 10 results
                if record.category:
                    categories.add(record.category)
                tags.update(record.tags[:3])  # Top 3 tags per record
            
            # Generate category-based suggestions
            for category in list(categories)[:3]:
                suggestions.append(f"{query} in {category}")
            
            # Generate tag-based suggestions
            for tag in list(tags)[:3]:
                suggestions.append(f"{query} tagged {tag}")
            
            # Generate AI-powered suggestions if available
            if len(suggestions) < 5:
                try:
                    ai_suggestions = await self.ai_service.suggest_queries({
                        "query": query,
                        "categories": list(categories),
                        "tags": list(tags)
                    })
                    suggestions.extend(ai_suggestions[:5])
                except Exception:
                    pass
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation error: {str(e)}")
            return []

    def _generate_facets(self, results: List[Any]) -> Dict[str, Dict[str, int]]:
        """Generate search facets from results"""
        try:
            facets = {
                "categories": {},
                "tags": {},
                "status": {}
            }
            
            for record in results:
                # Category facets
                if record.category:
                    facets["categories"][record.category] = \
                        facets["categories"].get(record.category, 0) + 1
                
                # Tag facets
                for tag in record.tags:
                    facets["tags"][tag] = facets["tags"].get(tag, 0) + 1
                
                # Status facets
                status = getattr(record, 'status', 'unknown')
                facets["status"][status] = facets["status"].get(status, 0) + 1
            
            return facets
            
        except Exception as e:
            logger.error(f"Facet generation error: {str(e)}")
            return {}

    async def stream_search(self, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream search results for real-time updates"""
        try:
            # Perform initial search
            results = await self.hybrid_search(query, limit=10)
            
            # Yield initial results
            for result in results.results:
                yield {
                    "type": "result",
                    "data": result.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Yield search completion
            yield {
                "type": "complete",
                "total_count": results.total_count,
                "processing_time": results.processing_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stream search error: {str(e)}")
            yield {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }