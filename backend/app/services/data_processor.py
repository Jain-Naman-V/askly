import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import csv
import io
import pandas as pd
from pathlib import Path

from .database import DatabaseService
from .ai_service import AIService
from ..models.data_models import (
    DataRecord, DataRecordCreate, DataRecordUpdate, 
    DataValidationResult, BulkDataOperation
)
from ..utils.helpers import extract_keywords, clean_text, generate_hash

logger = logging.getLogger(__name__)

class DataProcessor:
    """Advanced data processing service"""
    
    def __init__(self, db_service: DatabaseService, ai_service: AIService):
        self.db_service = db_service
        self.ai_service = ai_service
        
        # Supported file formats
        self.supported_formats = {
            'json': self._process_json,
            'csv': self._process_csv,
            'xlsx': self._process_excel,
            'txt': self._process_text
        }
        
        # Data validation rules
        self.validation_rules = {
            'required_fields': ['title', 'content'],
            'max_title_length': 200,
            'max_description_length': 1000,
            'max_tags': 20,
            'allowed_statuses': ['active', 'inactive', 'deleted', 'processing', 'error']
        }

    async def process_bulk_data(
        self, 
        operation: BulkDataOperation,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process bulk data operations"""
        start_time = datetime.utcnow()
        
        try:
            if operation.operation == "insert":
                return await self._bulk_insert(operation.records, created_by)
            elif operation.operation == "update":
                return await self._bulk_update(operation.records, operation.filters)
            elif operation.operation == "delete":
                return await self._bulk_delete(operation.filters)
            else:
                raise ValueError(f"Unsupported operation: {operation.operation}")
                
        except Exception as e:
            logger.error(f"Bulk operation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def _bulk_insert(self, records: List[Dict[str, Any]], created_by: Optional[str]) -> Dict[str, Any]:
        """Bulk insert records with validation and processing"""
        start_time = datetime.utcnow()
        processed_count = 0
        errors = []
        
        try:
            # Validate and process records
            valid_records = []
            
            for i, record_data in enumerate(records):
                try:
                    # Validate record
                    validation_result = await self.validate_record(record_data)
                    
                    if not validation_result.is_valid:
                        errors.append({
                            "index": i,
                            "errors": validation_result.errors
                        })
                        continue
                    
                    # Create record instance
                    record_create = DataRecordCreate(**record_data)
                    
                    # Process with AI if needed
                    processed_record = await self._process_record_with_ai(record_create)
                    valid_records.append(processed_record)
                    
                except Exception as e:
                    errors.append({
                        "index": i,
                        "errors": [str(e)]
                    })
            
            # Bulk insert valid records
            if valid_records:
                record_ids = await self.db_service.bulk_insert(valid_records, created_by)
                processed_count = len(record_ids)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "processed_count": processed_count,
                "error_count": len(errors),
                "errors": errors,
                "processing_time": processing_time,
                "record_ids": record_ids if valid_records else []
            }
            
        except Exception as e:
            logger.error(f"Bulk insert error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_count": processed_count,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def _bulk_update(self, records: List[Dict[str, Any]], filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk update records"""
        start_time = datetime.utcnow()
        processed_count = 0
        
        try:
            # If filters provided, update based on filters
            if filters:
                # Get matching records
                search_results = await self.db_service.search_records(
                    query="",
                    filters=filters,
                    limit=1000
                )
                
                update_data = records[0] if records else {}
                
                for record in search_results["data"]:
                    try:
                        record_update = DataRecordUpdate(**update_data)
                        await self.db_service.update_record(record.id, record_update)
                        processed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to update record {record.id}: {str(e)}")
            
            else:
                # Update individual records
                for record_data in records:
                    try:
                        record_id = record_data.get('id')
                        if not record_id:
                            continue
                            
                        record_update = DataRecordUpdate(**record_data)
                        result = await self.db_service.update_record(record_id, record_update)
                        
                        if result:
                            processed_count += 1
                            
                    except Exception as e:
                        logger.error(f"Failed to update record: {str(e)}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "processed_count": processed_count,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Bulk update error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_count": processed_count,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def _bulk_delete(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Bulk delete records based on filters"""
        start_time = datetime.utcnow()
        processed_count = 0
        
        try:
            # Get matching records
            search_results = await self.db_service.search_records(
                query="",
                filters=filters,
                limit=1000
            )
            
            # Delete records
            for record in search_results["data"]:
                try:
                    success = await self.db_service.delete_record(record.id, soft_delete=True)
                    if success:
                        processed_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete record {record.id}: {str(e)}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "processed_count": processed_count,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Bulk delete error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_count": processed_count,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def validate_record(self, record_data: Dict[str, Any]) -> DataValidationResult:
        """Validate record data against rules"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Check required fields
            for field in self.validation_rules['required_fields']:
                if field not in record_data or not record_data[field]:
                    errors.append(f"Required field '{field}' is missing or empty")
            
            # Validate title
            title = record_data.get('title', '')
            if len(title) > self.validation_rules['max_title_length']:
                errors.append(f"Title exceeds maximum length of {self.validation_rules['max_title_length']} characters")
            
            # Validate description
            description = record_data.get('description', '')
            if description and len(description) > self.validation_rules['max_description_length']:
                warnings.append(f"Description is very long ({len(description)} characters)")
            
            # Validate tags
            tags = record_data.get('tags', [])
            if len(tags) > self.validation_rules['max_tags']:
                warnings.append(f"Too many tags ({len(tags)}), consider reducing to {self.validation_rules['max_tags']}")
            
            # Validate status
            status = record_data.get('status', 'active')
            if status not in self.validation_rules['allowed_statuses']:
                errors.append(f"Invalid status '{status}'. Allowed: {self.validation_rules['allowed_statuses']}")
            
            # Validate content structure
            content = record_data.get('content', {})
            if not isinstance(content, dict):
                errors.append("Content must be a dictionary/object")
            elif not content:
                warnings.append("Content is empty")
            
            # Generate suggestions
            if not tags:
                suggestions.append("Consider adding tags to improve discoverability")
            
            if not description:
                suggestions.append("Adding a description would provide better context")
            
            return DataValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return DataValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                suggestions=[]
            )

    async def _process_record_with_ai(self, record: DataRecordCreate) -> DataRecordCreate:
        """Process record with AI enhancements"""
        try:
            # Generate enhanced keywords if not provided
            if not record.tags:
                content_text = f"{record.title} {record.description or ''}"
                for key, value in record.content.items():
                    if isinstance(value, str):
                        content_text += f" {value}"
                
                keywords = extract_keywords(content_text, max_keywords=10)
                record.tags = keywords[:5]  # Use top 5 as tags
            
            # Clean and enhance description
            if record.description:
                record.description = clean_text(record.description)
            
            # Generate category if not provided
            if not record.category:
                try:
                    # Use AI to suggest category
                    content_summary = {
                        "title": record.title,
                        "description": record.description,
                        "content_keys": list(record.content.keys())
                    }
                    
                    # This would be an AI call to categorize
                    # For now, use simple heuristics
                    if any(key in ["name", "email", "phone"] for key in record.content.keys()):
                        record.category = "contacts"
                    elif any(key in ["price", "cost", "amount"] for key in record.content.keys()):
                        record.category = "financial"
                    else:
                        record.category = "general"
                        
                except Exception as e:
                    logger.warning(f"AI categorization failed: {str(e)}")
                    record.category = "general"
            
            return record
            
        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            return record

    async def import_data(
        self,
        file_content: bytes,
        file_format: str,
        mapping: Optional[Dict[str, str]] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Import data from various file formats"""
        start_time = datetime.utcnow()
        
        try:
            if file_format not in self.supported_formats:
                raise ValueError(f"Unsupported format: {file_format}")
            
            # Process file content
            processor = self.supported_formats[file_format]
            records = await processor(file_content, mapping)
            
            # Bulk insert processed records
            if records:
                bulk_operation = BulkDataOperation(
                    operation="insert",
                    records=records
                )
                
                result = await self.process_bulk_data(bulk_operation, created_by)
                
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                result["total_processing_time"] = processing_time
                
                return result
            else:
                return {
                    "success": False,
                    "error": "No valid records found in file",
                    "processed_count": 0,
                    "processing_time": (datetime.utcnow() - start_time).total_seconds()
                }
                
        except Exception as e:
            logger.error(f"Data import error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_count": 0,
                "processing_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def _process_json(self, file_content: bytes, mapping: Optional[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process JSON file"""
        try:
            data = json.loads(file_content.decode('utf-8'))
            
            if isinstance(data, dict):
                data = [data]  # Single record
            
            if not isinstance(data, list):
                raise ValueError("JSON must contain a list of records or a single record")
            
            processed_records = []
            for record in data:
                processed_record = self._apply_mapping(record, mapping)
                processed_records.append(processed_record)
            
            return processed_records
            
        except Exception as e:
            logger.error(f"JSON processing error: {str(e)}")
            raise

    async def _process_csv(self, file_content: bytes, mapping: Optional[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process CSV file"""
        try:
            csv_content = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            processed_records = []
            for row in csv_reader:
                # Convert CSV row to proper format
                processed_record = self._csv_row_to_record(row, mapping)
                processed_records.append(processed_record)
            
            return processed_records
            
        except Exception as e:
            logger.error(f"CSV processing error: {str(e)}")
            raise

    async def _process_excel(self, file_content: bytes, mapping: Optional[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process Excel file"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            
            processed_records = []
            for _, row in df.iterrows():
                record = row.to_dict()
                processed_record = self._apply_mapping(record, mapping)
                processed_records.append(processed_record)
            
            return processed_records
            
        except Exception as e:
            logger.error(f"Excel processing error: {str(e)}")
            raise

    async def _process_text(self, file_content: bytes, mapping: Optional[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process plain text file"""
        try:
            text_content = file_content.decode('utf-8')
            lines = text_content.strip().split('\n')
            
            processed_records = []
            for i, line in enumerate(lines):
                if line.strip():
                    record = {
                        "title": f"Text Record {i+1}",
                        "description": line.strip()[:100],
                        "content": {"text": line.strip()}
                    }
                    processed_record = self._apply_mapping(record, mapping)
                    processed_records.append(processed_record)
            
            return processed_records
            
        except Exception as e:
            logger.error(f"Text processing error: {str(e)}")
            raise

    def _apply_mapping(self, record: Dict[str, Any], mapping: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Apply field mapping to record"""
        if not mapping:
            return record
        
        mapped_record = {}
        for source_field, target_field in mapping.items():
            if source_field in record:
                mapped_record[target_field] = record[source_field]
        
        # Ensure required fields are present
        if 'title' not in mapped_record:
            mapped_record['title'] = f"Record {generate_hash(record)[:8]}"
        
        if 'content' not in mapped_record:
            mapped_record['content'] = record
        
        return mapped_record

    def _csv_row_to_record(self, row: Dict[str, str], mapping: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Convert CSV row to record format"""
        # Create base record structure
        record = {
            "title": row.get("title", row.get("name", f"Record {generate_hash(row)[:8]}")),
            "description": row.get("description", ""),
            "content": {},
            "tags": [],
            "category": row.get("category", "imported")
        }
        
        # Move other fields to content
        for key, value in row.items():
            if key not in ["title", "description", "category", "tags"]:
                record["content"][key] = value
        
        # Process tags if present
        if "tags" in row and row["tags"]:
            record["tags"] = [tag.strip() for tag in row["tags"].split(",")]
        
        return self._apply_mapping(record, mapping)