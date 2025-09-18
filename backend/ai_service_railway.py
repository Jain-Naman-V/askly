import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import httpx
from groq import Groq, AsyncGroq
import numpy as np

logger = logging.getLogger(__name__)

class AIService:
    """Lightweight AI service with Groq LLM integration (Railway optimized)"""
    
    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        self.api_key = api_key
        self.model = model
        self.client = AsyncGroq(api_key=api_key)
        
        # System prompts for different tasks
        self.system_prompts = {
            "search": """You are an expert data analyst. Help users search and understand structured data.
            Transform natural language queries into precise search parameters.
            Focus on extracting: entities, filters, date ranges, and search intent.""",
            
            "insights": """You are a data insights expert. Analyze search results and provide:
            1. Key patterns and trends
            2. Interesting findings
            3. Potential correlations
            4. Actionable recommendations
            
            Be concise but insightful. Focus on business value.""",
            
            "chat": """You are an AI data analyst assistant specializing in MongoDB data analysis.
            When users ask about trends, patterns, or analysis, use the provided data context to give specific insights.
            
            If data context is provided:
            - Analyze the actual data shown in the context
            - Provide specific insights about categories, dates, patterns
            - Give concrete numbers and statistics
            - Identify real trends in the dataset
            
            Focus on:
            1. Specific data patterns you can see
            2. Category distributions and popular items
            3. Time-based trends if dates are available
            4. Data quality observations
            5. Actionable business insights
            
            Be conversational but data-focused. Always reference the actual data when available."""
        }

    async def health_check(self) -> bool:
        """Check if AI service is available"""
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.model,
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"AI service health check failed: {str(e)}")
            return False

    async def process_search_query(self, query: str) -> Dict[str, Any]:
        """Process natural language search query into structured parameters"""
        try:
            prompt = f"""
            Analyze this search query and extract structured parameters:
            Query: "{query}"
            
            Return ONLY valid JSON with:
            {{
                "intent": "search",
                "entities": ["extracted entities"],
                "filters": {{}},
                "sort": {{}},
                "date_range": {{}},
                "keywords": ["key", "terms"],
                "confidence": 0.95
            }}
            """
            
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompts["search"]},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Raw AI response for query processing: {content}")
            
            if not content:
                raise ValueError("Empty AI response")
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                if '```json' in content:
                    json_start = content.find('{', content.find('```json'))
                    json_end = content.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        result = json.loads(content[json_start:json_end])
                    else:
                        raise ValueError("No valid JSON found in markdown")
                elif '{' in content and '}' in content:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    result = json.loads(content[json_start:json_end])
                else:
                    raise ValueError("No valid JSON found")
            
            result["original_query"] = query
            result["processed_at"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            return {
                "intent": "search",
                "keywords": query.split(),
                "original_query": query,
                "confidence": 0.5,
                "entities": [],
                "filters": {},
                "sort": {},
                "date_range": {},
                "error": str(e)
            }

    async def generate_insights(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered insights from search results"""
        try:
            sample_data = data[:100] if len(data) > 100 else data
            
            data_summary = {
                "total_records": len(data),
                "sample_size": len(sample_data),
                "fields": list(sample_data[0].keys()) if sample_data else [],
                "sample_records": sample_data[:5]
            }
            
            prompt = f"""
            Analyze this dataset and provide insights:
            
            Data Summary:
            {json.dumps(data_summary, indent=2)}
            
            Provide insights in this JSON format:
            {{
                "key_patterns": ["pattern 1", "pattern 2"],
                "trends": ["trend 1", "trend 2"],
                "anomalies": ["anomaly 1", "anomaly 2"],
                "recommendations": ["recommendation 1", "recommendation 2"],
                "data_quality": {{"score": 0.85, "issues": ["issue 1"]}},
                "summary": "Brief overall summary"
            }}
            """
            
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompts["insights"]},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=800,
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            
            if not content:
                raise ValueError("Empty AI response")
            
            try:
                insights = json.loads(content)
            except json.JSONDecodeError:
                if '{' in content and '}' in content:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    insights = json.loads(content[json_start:json_end])
                else:
                    raise ValueError("No valid JSON found")
            
            insights["generated_at"] = datetime.utcnow().isoformat()
            insights["data_size"] = len(data)
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation error: {str(e)}")
            return {
                "summary": f"Analysis completed on {len(data)} records",
                "key_patterns": ["Data contains structured information", "Records have consistent format"],
                "trends": ["Recent data activity", "Regular updates"],
                "recommendations": ["Continue data collection", "Review data quality"],
                "data_quality": {"score": 0.8, "issues": []},
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }

    async def stream_chat(self, message: str, context: Optional[List[Dict]] = None) -> AsyncGenerator[str, None]:
        """Stream AI chat response"""
        try:
            context_text = ""
            if context:
                context_text = f"\nContext data: {json.dumps(context[:5], indent=2)}"
            
            messages = [
                {"role": "system", "content": self.system_prompts["chat"]},
                {"role": "user", "content": f"{message}{context_text}"}
            ]
            
            stream = await self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Chat streaming error: {str(e)}")
            yield f"Error: {str(e)}"

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate simple text-based embeddings (lightweight alternative)"""
        try:
            # Simple TF-IDF-like approach for basic embeddings
            # This is much lighter than SentenceTransformers
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            if not texts:
                return np.array([])
            
            vectorizer = TfidfVectorizer(max_features=384, stop_words='english', ngram_range=(1, 2))
            embeddings = vectorizer.fit_transform(texts).toarray()
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            # Fallback: simple word count vectors
            return np.array([[len(text.split()) for text in texts]]).T

    async def analyze_data(self, data: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
        """Perform comprehensive data analysis"""
        try:
            summary_stats = self._calculate_summary_stats(data)
            
            analysis_prompts = {
                "summary": "Provide a comprehensive summary of the dataset",
                "trends": "Identify trends and patterns in the data",
                "anomalies": "Detect anomalies and outliers",
                "correlations": "Find correlations between different fields",
                "recommendations": "Provide actionable business recommendations"
            }
            
            prompt = f"""
            Perform {analysis_type} analysis on this dataset:
            
            Dataset Statistics:
            {json.dumps(summary_stats, indent=2)}
            
            Sample Data:
            {json.dumps(data[:10], indent=2)}
            
            {analysis_prompts.get(analysis_type, "Analyze the data")}
            
            Return detailed analysis in JSON format with actionable insights.
            """
            
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert data scientist."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=1500,
                temperature=0.1
            )
            
            analysis_result = {
                "analysis_type": analysis_type,
                "result": response.choices[0].message.content,
                "summary_stats": summary_stats,
                "analyzed_at": datetime.utcnow().isoformat(),
                "record_count": len(data)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Data analysis error: {str(e)}")
            return {
                "analysis_type": analysis_type,
                "error": str(e),
                "analyzed_at": datetime.utcnow().isoformat()
            }

    def _calculate_summary_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic summary statistics"""
        if not data:
            return {"error": "No data provided"}
        
        try:
            stats = {
                "record_count": len(data),
                "field_count": len(data[0].keys()) if data else 0,
                "fields": list(data[0].keys()) if data else [],
                "field_types": {},
                "missing_values": {},
                "unique_values": {}
            }
            
            for field in stats["fields"]:
                field_values = [record.get(field) for record in data if record.get(field) is not None]
                
                if field_values:
                    sample_value = field_values[0]
                    if isinstance(sample_value, (int, float)):
                        stats["field_types"][field] = "numeric"
                    elif isinstance(sample_value, str):
                        stats["field_types"][field] = "text"
                    else:
                        stats["field_types"][field] = "other"
                    
                    total_records = len(data)
                    non_null_records = len(field_values)
                    stats["missing_values"][field] = total_records - non_null_records
                    
                    unique_values = list(set(field_values[:100]))
                    stats["unique_values"][field] = len(unique_values)
                else:
                    stats["field_types"][field] = "empty"
                    stats["missing_values"][field] = len(data)
                    stats["unique_values"][field] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Summary stats calculation error: {str(e)}")
            return {"error": str(e)}

    async def suggest_queries(self, data_schema: Dict[str, Any]) -> List[str]:
        """Generate suggested queries based on data schema"""
        try:
            prompt = f"""
            Based on this data schema, suggest 10 useful search queries users might want to ask:
            
            Schema: {json.dumps(data_schema, indent=2)}
            
            Return ONLY a JSON array of query suggestions:
            ["query 1", "query 2", "query 3"]
            """
            
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful query suggestion assistant. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            if not content:
                raise ValueError("Empty AI response")
            
            try:
                suggestions = json.loads(content)
            except json.JSONDecodeError:
                if '[' in content and ']' in content:
                    json_start = content.find('[')
                    json_end = content.rfind(']') + 1
                    suggestions = json.loads(content[json_start:json_end])
                else:
                    raise ValueError("No valid JSON array found")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Query suggestion error: {str(e)}")
            return [
                "Show all active records",
                "Find records created today", 
                "Search by category",
                "Show recent updates",
                "Find records with specific tags"
            ]