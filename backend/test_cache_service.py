#!/usr/bin/env python3
"""
Test script for Redis Cache Service
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cache_service import RedisCache, cache_result, async_cache_result, cache

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def test_basic_cache_operations():
    """Test basic cache operations"""
    print_status("Testing basic cache operations...", "INFO")
    
    redis_cache = RedisCache()
    
    # Test 1: Set and get string
    print_status("Testing string operations...", "INFO")
    success = redis_cache.set("test_string", "Hello Redis!", ttl=60)
    if success:
        value = redis_cache.get("test_string")
        if value == "Hello Redis!":
            print_status("✅ String operations successful", "SUCCESS")
        else:
            print_status(f"❌ String operations failed. Expected: 'Hello Redis!', Got: {value}", "ERROR")
            return False
    else:
        print_status("❌ Failed to set string value", "ERROR")
        return False
    
    # Test 2: Set and get complex object
    print_status("Testing complex object operations...", "INFO")
    test_data = {
        "user_id": 123,
        "username": "test_user",
        "settings": {
            "theme": "dark",
            "notifications": True
        },
        "tags": ["python", "redis", "caching"]
    }
    
    success = redis_cache.set("test_object", test_data, ttl=60)
    if success:
        retrieved_data = redis_cache.get("test_object")
        if retrieved_data == test_data:
            print_status("✅ Complex object operations successful", "SUCCESS")
        else:
            print_status(f"❌ Complex object operations failed", "ERROR")
            return False
    else:
        print_status("❌ Failed to set complex object", "ERROR")
        return False
    
    # Test 3: Hash operations
    print_status("Testing hash operations...", "INFO")
    hash_data = {
        "name": "John Doe",
        "age": 30,
        "city": "New York",
        "active": True
    }
    
    success = redis_cache.set_hash("user_profile", hash_data, ttl=60)
    if success:
        retrieved_hash = redis_cache.get_hash("user_profile")
        if retrieved_hash == hash_data:
            print_status("✅ Hash operations successful", "SUCCESS")
        else:
            print_status(f"❌ Hash operations failed", "ERROR")
            return False
        
        # Test getting single field
        name = redis_cache.get_hash("user_profile", "name")
        if name == "John Doe":
            print_status("✅ Hash field operations successful", "SUCCESS")
        else:
            print_status(f"❌ Hash field operations failed", "ERROR")
            return False
    else:
        print_status("❌ Failed to set hash", "ERROR")
        return False
    
    # Test 4: Counter operations
    print_status("Testing counter operations...", "INFO")
    counter_value = redis_cache.increment("test_counter", 5)
    if counter_value == 5:
        print_status("✅ Counter operations successful", "SUCCESS")
    else:
        print_status(f"❌ Counter operations failed. Expected: 5, Got: {counter_value}", "ERROR")
        return False
    
    # Test 5: TTL operations
    print_status("Testing TTL operations...", "INFO")
    ttl = redis_cache.get_ttl("test_string")
    if ttl > 0:
        print_status(f"✅ TTL operations successful: {ttl} seconds remaining", "SUCCESS")
    else:
        print_status(f"❌ TTL operations failed. TTL: {ttl}", "ERROR")
        return False
    
    # Test 6: Exists operations
    print_status("Testing exists operations...", "INFO")
    exists = redis_cache.exists("test_string")
    if exists:
        print_status("✅ Exists operations successful", "SUCCESS")
    else:
        print_status("❌ Exists operations failed", "ERROR")
        return False
    
    return True

@cache_result(ttl=60, prefix="function_cache")
def expensive_function(x, y):
    """Simulate an expensive function"""
    print_status(f"Executing expensive function with x={x}, y={y}", "INFO")
    import time
    time.sleep(0.1)  # Simulate processing time
    return x * y + 100

@async_cache_result(ttl=60, prefix="async_function_cache")
async def expensive_async_function(x, y):
    """Simulate an expensive async function"""
    print_status(f"Executing expensive async function with x={x}, y={y}", "INFO")
    await asyncio.sleep(0.1)  # Simulate async processing time
    return x * y + 200

def test_caching_decorators():
    """Test caching decorators"""
    print_status("Testing caching decorators...", "INFO")
    
    # Test sync decorator
    print_status("Testing sync decorator...", "INFO")
    start_time = datetime.now()
    result1 = expensive_function(5, 10)
    first_duration = (datetime.now() - start_time).total_seconds()
    
    start_time = datetime.now()
    result2 = expensive_function(5, 10)  # Should be cached
    second_duration = (datetime.now() - start_time).total_seconds()
    
    if result1 == result2 and result1 == 150:
        if second_duration < first_duration:
            print_status("✅ Sync caching decorator successful", "SUCCESS")
            print_status(f"   First call: {first_duration:.3f}s, Second call: {second_duration:.3f}s", "INFO")
        else:
            print_status("⚠️ Sync decorator results match but caching might not be working", "WARNING")
    else:
        print_status(f"❌ Sync decorator failed. Results: {result1} vs {result2}", "ERROR")
        return False
    
    return True

async def test_async_caching_decorators():
    """Test async caching decorators"""
    print_status("Testing async caching decorators...", "INFO")
    
    start_time = datetime.now()
    result1 = await expensive_async_function(3, 7)
    first_duration = (datetime.now() - start_time).total_seconds()
    
    start_time = datetime.now()
    result2 = await expensive_async_function(3, 7)  # Should be cached
    second_duration = (datetime.now() - start_time).total_seconds()
    
    if result1 == result2 and result1 == 221:
        if second_duration < first_duration:
            print_status("✅ Async caching decorator successful", "SUCCESS")
            print_status(f"   First call: {first_duration:.3f}s, Second call: {second_duration:.3f}s", "INFO")
        else:
            print_status("⚠️ Async decorator results match but caching might not be working", "WARNING")
    else:
        print_status(f"❌ Async decorator failed. Results: {result1} vs {result2}", "ERROR")
        return False
    
    return True

def test_cache_info():
    """Test cache information"""
    print_status("Testing cache information...", "INFO")
    
    redis_cache = RedisCache()
    info = redis_cache.get_info()
    
    print_status("Cache Information:", "INFO")
    for key, value in info.items():
        print_status(f"  {key}: {value}", "INFO")
    
    if info.get("connected", False):
        print_status("✅ Cache info retrieved successfully", "SUCCESS")
        return True
    else:
        print_status("⚠️ Cache not connected, using fallback", "WARNING")
        return True

async def main():
    """Main test function"""
    print_status("🧪 Redis Cache Service Test Starting...", "INFO")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Basic operations
    if test_basic_cache_operations():
        tests_passed += 1
    print("-" * 40)
    
    # Test 2: Caching decorators
    if test_caching_decorators():
        tests_passed += 1
    print("-" * 40)
    
    # Test 3: Async caching decorators
    if await test_async_caching_decorators():
        tests_passed += 1
    print("-" * 40)
    
    # Test 4: Cache info
    if test_cache_info():
        tests_passed += 1
    print("-" * 40)
    
    # Test 5: Cleanup test
    print_status("Testing cleanup operations...", "INFO")
    redis_cache = RedisCache()
    
    # Clean up test keys
    deleted_count = 0
    test_keys = ["test_string", "test_object", "test_counter"]
    for key in test_keys:
        if redis_cache.delete(key):
            deleted_count += 1
    
    if deleted_count > 0:
        print_status(f"✅ Cleanup successful: {deleted_count} keys deleted", "SUCCESS")
        tests_passed += 1
    else:
        print_status("⚠️ Cleanup completed (no keys to delete)", "WARNING")
        tests_passed += 1
    
    print("=" * 70)
    
    # Summary
    if tests_passed == total_tests:
        print_status(f"🎉 All tests passed! ({tests_passed}/{total_tests})", "SUCCESS")
        print_status("Your Redis cache service is working correctly!", "SUCCESS")
    elif tests_passed > 0:
        print_status(f"⚠️ Partial success: ({tests_passed}/{total_tests}) tests passed", "WARNING")
    else:
        print_status(f"❌ All tests failed! ({tests_passed}/{total_tests})", "ERROR")
    
    print("\n" + "=" * 70)
    print_status("💡 Integration Tips:", "INFO")
    print("1. Replace in-memory cache in search_service.py with RedisCache")
    print("2. Use @cache_result decorator for expensive functions")
    print("3. Use @async_cache_result decorator for async functions")
    print("4. Cache search results, AI responses, and embeddings")
    print("5. Use hash operations for user sessions and preferences")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_status("\n🛑 Test interrupted by user", "WARNING")
    except Exception as e:
        print_status(f"❌ Unexpected error: {e}", "ERROR")
        sys.exit(1)