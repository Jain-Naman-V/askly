import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import TEXT, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
import json
from bson import ObjectId

from ..models.data_models import DataRecord, DataRecordCreate, DataRecordUpdate, BulkDataOperation
from ..utils.helpers import generate_hash, extract_keywords, paginate_results

logger = logging.getLogger(__name__)

class DatabaseService:
    """Advanced MongoDB service with optimized operations"""
    
    def __init__(self, mongodb_url: str, db_name: str):
        self.mongodb_url = mongodb_url
        self.db_name = db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None
        self._connection_pool_size = 10
        self._max_idle_time = 30000  # 30 seconds
        
    async def connect(self):
        """Establish database connection with optimized settings"""
        try:
            self.client = AsyncIOMotorClient(
                self.mongodb_url,
                maxPoolSize=self._connection_pool_size,
                maxIdleTimeMS=self._max_idle_time,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True
            )
            
            self.db = self.client[self.db_name]
            self.collection = self.db.structured_data
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {self.db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

    async def health_check(self) -> bool:
        """Check database health"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    async def create_indexes(self):
        """Create optimized indexes for better performance"""
        try:
            # Text search index
            await self.collection.create_index([
                ("title", TEXT),
                ("description", TEXT),
                ("content", TEXT),
                ("tags", TEXT),
                ("search_text", TEXT)
            ], name="text_search_index")
            
            # Compound indexes for common queries
            await self.collection.create_index([
                ("status", ASCENDING),
                ("category", ASCENDING),
                ("created_at", DESCENDING)
            ], name="status_category_created_index")
            
            await self.collection.create_index([
                ("tags", ASCENDING),
                ("created_at", DESCENDING)
            ], name="tags_created_index")
            
            await self.collection.create_index([
                ("created_by", ASCENDING),
                ("created_at", DESCENDING)
            ], name="user_created_index")
            
            # Vector search index (for Atlas Vector Search)
            # Note: This requires MongoDB Atlas Vector Search
            try:
                await self.collection.create_index([
                    ("embedding", "2dsphere")
                ], name="vector_search_index")
            except Exception as e:
                logger.warning(f"Vector index creation failed (requires Atlas): {str(e)}")
            
            # Unique ID index
            await self.collection.create_index("id", unique=True, name="unique_id_index")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Index creation error: {str(e)}")
            raise

    async def create_record(self, record_data: DataRecordCreate, created_by: Optional[str] = None) -> DataRecord:
        """Create a new data record"""
        try:
            # Create record instance
            record = DataRecord(
                **record_data.dict(),
                created_by=created_by,
                updated_by=created_by
            )
            
            # Generate search text and keywords
            search_text = f"{record.title} {record.description or ''}"
            for key, value in record.content.items():
                if isinstance(value, str):
                    search_text += f" {value}"
            
            record.search_text = search_text
            record.keywords = extract_keywords(search_text)
            
            # Convert to dict for MongoDB
            record_dict = record.dict()
            record_dict["_id"] = record_dict["id"]
            
            # Insert into database
            await self.collection.insert_one(record_dict)
            logger.info(f"Created record: {record.id}")
            
            return record
            
        except DuplicateKeyError:
            logger.error(f"Record with ID already exists")
            raise ValueError("Record with this ID already exists")
        except Exception as e:
            logger.error(f"Record creation error: {str(e)}")
            raise

    async def get_record(self, record_id: str) -> Optional[DataRecord]:
        """Get a record by ID"""
        try:
            record_dict = await self.collection.find_one({"id": record_id})
            if record_dict:
                # Remove MongoDB _id for Pydantic model
                record_dict.pop("_id", None)
                return DataRecord(**record_dict)
            return None
            
        except Exception as e:
            logger.error(f"Record retrieval error: {str(e)}")
            raise

    async def update_record(
        self, 
        record_id: str, 
        update_data: DataRecordUpdate, 
        updated_by: Optional[str] = None
    ) -> Optional[DataRecord]:
        """Update a record"""
        try:
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                update_dict["updated_by"] = updated_by
                
                # Update search text if title, description, or content changed
                if any(key in update_dict for key in ["title", "description", "content"]):
                    record = await self.get_record(record_id)
                    if record:
                        # Merge updates
                        for key, value in update_dict.items():
                            setattr(record, key, value)
                        
                        # Regenerate search text
                        search_text = f"{record.title} {record.description or ''}"
                        for key, value in record.content.items():
                            if isinstance(value, str):
                                search_text += f" {value}"
                        
                        update_dict["search_text"] = search_text
                        update_dict["keywords"] = extract_keywords(search_text)
                
                # Update in database
                result = await self.collection.update_one(
                    {"id": record_id},
                    {"$set": update_dict}
                )
                
                if result.modified_count > 0:
                    return await self.get_record(record_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Record update error: {str(e)}")
            raise

    async def delete_record(self, record_id: str, soft_delete: bool = True) -> bool:
        """Delete a record (soft or hard delete)"""
        try:
            if soft_delete:
                result = await self.collection.update_one(
                    {"id": record_id},
                    {"$set": {"status": "deleted", "updated_at": datetime.utcnow()}}
                )
                return result.modified_count > 0
            else:
                result = await self.collection.delete_one({"id": record_id})
                return result.deleted_count > 0
                
        except Exception as e:
            logger.error(f"Record deletion error: {str(e)}")
            raise

    async def search_records(
        self,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_order: int = -1,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search records with filters and pagination"""
        try:
            # Build search pipeline
            pipeline = []
            
            # Match stage
            match_conditions = {"status": {"$ne": "deleted"}}
            
            # Add text search if query provided
            if query.strip():
                # Use MongoDB text search
                match_conditions["$text"] = {"$search": query}
            
            # Add filters
            if filters:
                for key, value in filters.items():
                    if key == "date_range" and isinstance(value, dict):
                        if "start" in value:
                            match_conditions["created_at"] = {"$gte": value["start"]}
                        if "end" in value:
                            match_conditions.setdefault("created_at", {})["$lte"] = value["end"]
                    elif key == "tags" and isinstance(value, list):
                        match_conditions["tags"] = {"$in": value}
                    elif key == "categories" and isinstance(value, list):
                        match_conditions["category"] = {"$in": value}
                    else:
                        match_conditions[key] = value
            
            pipeline.append({"$match": match_conditions})
            
            # Add text score for sorting
            if query.strip():
                pipeline.append({"$addFields": {"score": {"$meta": "textScore"}}})
                sort_by = "score"
                sort_order = -1
            
            # Sort stage
            pipeline.append({"$sort": {sort_by: sort_order}})
            
            # Count total results
            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await self.collection.aggregate(count_pipeline).to_list(1)
            total_count = count_result[0]["total"] if count_result else 0
            
            # Add pagination
            pipeline.extend([
                {"$skip": offset},
                {"$limit": limit},
                {"$project": {"_id": 0}}  # Remove MongoDB _id
            ])
            
            # Execute search
            results = await self.collection.aggregate(pipeline).to_list(limit)
            
            return {
                "data": [DataRecord(**record) for record in results],
                "total_count": total_count,
                "offset": offset,
                "limit": limit,
                "returned_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise

    async def bulk_insert(self, records: List[DataRecordCreate], created_by: Optional[str] = None) -> List[str]:
        """Bulk insert records"""
        try:
            record_dicts = []
            record_ids = []
            
            for record_data in records:
                record = DataRecord(
                    **record_data.dict(),
                    created_by=created_by,
                    updated_by=created_by
                )
                
                # Generate search text and keywords
                search_text = f"{record.title} {record.description or ''}"
                for key, value in record.content.items():
                    if isinstance(value, str):
                        search_text += f" {value}"
                
                record.search_text = search_text
                record.keywords = extract_keywords(search_text)
                
                record_dict = record.dict()
                record_dict["_id"] = record_dict["id"]
                record_dicts.append(record_dict)
                record_ids.append(record.id)
            
            # Bulk insert
            await self.collection.insert_many(record_dicts, ordered=False)
            logger.info(f"Bulk inserted {len(record_ids)} records")
            
            return record_ids
            
        except Exception as e:
            logger.error(f"Bulk insert error: {str(e)}")
            raise

    async def get_analytics(self) -> Dict[str, Any]:
        """Get database analytics"""
        try:
            pipeline = [
                {"$match": {"status": {"$ne": "deleted"}}},
                {"$group": {
                    "_id": None,
                    "total_records": {"$sum": 1},
                    "active_records": {
                        "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                    },
                    "categories": {"$addToSet": "$category"},
                    "total_tags": {"$push": "$tags"}
                }},
                {"$project": {
                    "_id": 0,
                    "total_records": 1,
                    "active_records": 1,
                    "unique_categories": {"$size": "$categories"},
                    "categories": 1,
                    "total_tags": {"$reduce": {
                        "input": "$total_tags",
                        "initialValue": [],
                        "in": {"$concatArrays": ["$$value", "$$this"]}
                    }}
                }}
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(1)
            analytics = result[0] if result else {}
            
            # Add time-based analytics
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            created_today = await self.collection.count_documents({
                "created_at": {"$gte": today},
                "status": {"$ne": "deleted"}
            })
            
            updated_today = await self.collection.count_documents({
                "updated_at": {"$gte": today},
                "status": {"$ne": "deleted"}
            })
            
            analytics.update({
                "created_today": created_today,
                "updated_today": updated_today,
                "timestamp": datetime.utcnow()
            })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            raise

    async def get_sample_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sample data for analysis"""
        try:
            cursor = self.collection.find(
                {"status": {"$ne": "deleted"}},
                {"_id": 0}
            ).limit(limit)
            
            return await cursor.to_list(limit)
            
        except Exception as e:
            logger.error(f"Sample data retrieval error: {str(e)}")
            raise

    async def store_analysis_result(self, analysis_type: str, result: Dict[str, Any]):
        """Store analysis results"""
        try:
            analysis_doc = {
                "id": f"analysis_{analysis_type}_{int(datetime.utcnow().timestamp())}",
                "type": analysis_type,
                "result": result,
                "created_at": datetime.utcnow()
            }
            
            # Store in separate collection
            analysis_collection = self.db.analysis_results
            await analysis_collection.insert_one(analysis_doc)
            
            logger.info(f"Stored analysis result: {analysis_type}")
            
        except Exception as e:
            logger.error(f"Analysis storage error: {str(e)}")
            raise

    async def stream_changes(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream database changes (requires replica set)"""
        try:
            # Watch for changes in the collection
            async with self.collection.watch() as stream:
                async for change in stream:
                    yield {
                        "operation_type": change["operationType"],
                        "document_id": change.get("documentKey", {}).get("_id"),
                        "timestamp": change["clusterTime"],
                        "changes": change.get("updateDescription", {})
                    }
                    
        except Exception as e:
            logger.error(f"Change stream error: {str(e)}")
            # Fallback: return empty generator
            return
            yield  # Make this a generator