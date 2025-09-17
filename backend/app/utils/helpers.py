from typing import Any, Dict, List, Optional
import re
import json
from datetime import datetime
import hashlib

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction - remove common words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
        'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Clean and split text
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    keywords = [word for word in words if word not in stop_words]
    
    # Return unique keywords, limited by max_keywords
    return list(dict.fromkeys(keywords))[:max_keywords]

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text

def generate_hash(data: Any) -> str:
    """Generate hash for data"""
    if isinstance(data, dict):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode()).hexdigest()

def format_timestamp(timestamp: datetime = None) -> str:
    """Format timestamp for logging"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

def paginate_results(data: List[Any], offset: int = 0, limit: int = 50) -> Dict[str, Any]:
    """Paginate list of results"""
    total_count = len(data)
    start = offset
    end = offset + limit
    
    paginated_data = data[start:end]
    
    return {
        "data": paginated_data,
        "total_count": total_count,
        "offset": offset,
        "limit": limit,
        "has_more": end < total_count
    }

def safe_json_parse(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def validate_search_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean search filters"""
    valid_filters = {}
    
    for key, value in filters.items():
        # Skip empty values
        if value is None or value == "":
            continue
            
        # Clean field names
        clean_key = re.sub(r'[^\w.]', '', key)
        if not clean_key:
            continue
            
        valid_filters[clean_key] = value
    
    return valid_filters

def calculate_similarity_score(text1: str, text2: str) -> float:
    """Calculate basic text similarity score"""
    if not text1 or not text2:
        return 0.0
    
    # Simple Jaccard similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)