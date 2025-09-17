#!/usr/bin/env python3
"""
Simple Redis Connection Test Script for Upstash/Stash Redis
"""

import redis
import sys
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",     # Blue
        "SUCCESS": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "RESET": "\033[0m"      # Reset
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def parse_redis_url(redis_url):
    """Parse Redis URL and extract connection details"""
    try:
        parsed = urlparse(redis_url)
        return {
            "scheme": parsed.scheme,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "username": parsed.username,
            "password": parsed.password,
            "path": parsed.path
        }
    except Exception as e:
        print_status(f"Failed to parse Redis URL: {e}", "ERROR")
        return None

def test_redis_connection(redis_url):
    """Test Redis connection using synchronous redis-py"""
    print_status("Testing Redis connection...", "INFO")
    
    try:
        # Create Redis client with timeout settings
        client = redis.from_url(
            redis_url, 
            socket_timeout=10, 
            socket_connect_timeout=10,
            retry_on_timeout=True,
            decode_responses=True  # Automatically decode responses
        )
        
        # Test 1: Basic ping
        print_status("Testing basic connectivity...", "INFO")
        response = client.ping()
        if response:
            print_status("✅ Redis PING successful", "SUCCESS")
        else:
            print_status("❌ Redis PING failed", "ERROR")
            return False
        
        # Test 2: Set/Get operations
        print_status("Testing basic operations...", "INFO")
        test_key = "test_connection_key"
        test_value = "Hello from Python Redis Test!"
        
        # Set a value with expiration
        client.set(test_key, test_value, ex=60)  # Expires in 60 seconds
        print_status(f"✅ SET operation successful: {test_key} = {test_value}", "SUCCESS")
        
        # Get the value
        retrieved_value = client.get(test_key)
        if retrieved_value == test_value:
            print_status(f"✅ GET operation successful: {retrieved_value}", "SUCCESS")
        else:
            print_status(f"❌ GET operation failed. Expected: {test_value}, Got: {retrieved_value}", "ERROR")
            return False
        
        # Test 3: Check if key exists
        if client.exists(test_key):
            print_status("✅ EXISTS operation successful", "SUCCESS")
        else:
            print_status("❌ EXISTS operation failed", "ERROR")
        
        # Test 4: Increment operations (for caching/counters)
        counter_key = "test_counter"
        client.set(counter_key, 0)
        incremented = client.incr(counter_key)
        if incremented == 1:
            print_status("✅ INCR operation successful", "SUCCESS")
        else:
            print_status(f"❌ INCR operation failed. Expected: 1, Got: {incremented}", "ERROR")
        
        # Test 5: List operations
        list_key = "test_list"
        client.delete(list_key)  # Clear any existing list
        client.lpush(list_key, "item1", "item2", "item3")
        list_length = client.llen(list_key)
        if list_length == 3:
            print_status("✅ LIST operations successful", "SUCCESS")
        else:
            print_status(f"❌ LIST operations failed. Expected length: 3, Got: {list_length}", "ERROR")
        
        # Test 6: Hash operations
        hash_key = "test_hash"
        client.delete(hash_key)  # Clear any existing hash
        client.hset(hash_key, mapping={"field1": "value1", "field2": "value2"})
        hash_value = client.hget(hash_key, "field1")
        if hash_value == "value1":
            print_status("✅ HASH operations successful", "SUCCESS")
        else:
            print_status(f"❌ HASH operations failed. Expected: value1, Got: {hash_value}", "ERROR")
        
        # Test 7: TTL operations
        ttl_key = "test_ttl"
        client.set(ttl_key, "test", ex=30)  # 30 seconds TTL
        ttl = client.ttl(ttl_key)
        if isinstance(ttl, int) and ttl > 0:
            print_status(f"✅ TTL operations successful: {ttl} seconds remaining", "SUCCESS")
        else:
            print_status(f"❌ TTL operations failed. TTL: {ttl}", "ERROR")
        
        # Clean up test keys
        print_status("Cleaning up test keys...", "INFO")
        deleted = client.delete(test_key, counter_key, list_key, hash_key, ttl_key)
        print_status(f"✅ Cleaned up {deleted} test keys", "SUCCESS")
        
        # Get Redis server information
        try:
            info = client.info()
            if isinstance(info, dict):
                print_status("Redis Server Information:", "INFO")
                print_status(f"  Redis Version: {info.get('redis_version', 'Unknown')}", "INFO")
                print_status(f"  Connected Clients: {info.get('connected_clients', 'Unknown')}", "INFO")
                print_status(f"  Used Memory: {info.get('used_memory_human', 'Unknown')}", "INFO")
                print_status(f"  Total Commands Processed: {info.get('total_commands_processed', 'Unknown')}", "INFO")
                print_status(f"  Keyspace Hits: {info.get('keyspace_hits', 'Unknown')}", "INFO")
                print_status(f"  Keyspace Misses: {info.get('keyspace_misses', 'Unknown')}", "INFO")
            else:
                print_status("✅ Redis INFO command successful (details not available)", "SUCCESS")
        except Exception as e:
            print_status(f"⚠️  Could not retrieve Redis info: {e}", "WARNING")
        
        # Close connection
        client.close()
        return True
        
    except redis.AuthenticationError as e:
        print_status(f"❌ Redis authentication error: {e}", "ERROR")
        return False
    except redis.TimeoutError as e:
        print_status(f"❌ Redis timeout error: {e}", "ERROR")
        return False
    except redis.ConnectionError as e:
        print_status(f"❌ Redis connection error: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ Unexpected error: {e}", "ERROR")
        return False

def main():
    """Main test function"""
    print_status("🔍 Redis Connection Test Starting...", "INFO")
    print("=" * 70)
    
    # Get Redis URL from environment
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url:
        print_status("❌ REDIS_URL environment variable not found!", "ERROR")
        print_status("Please set REDIS_URL in your .env file", "INFO")
        print_status("Example: REDIS_URL=redis://username:password@host:port", "INFO")
        return False
    
    # Parse and display connection info (mask sensitive data)
    parsed = parse_redis_url(redis_url)
    if parsed:
        print_status("Redis Connection Details:", "INFO")
        print_status(f"  Scheme: {parsed['scheme']}", "INFO")
        print_status(f"  Host: {parsed['hostname']}", "INFO")
        print_status(f"  Port: {parsed['port']}", "INFO")
        print_status(f"  Username: {'***' if parsed['username'] else 'None'}", "INFO")
        print_status(f"  Password: {'***' if parsed['password'] else 'None'}", "INFO")
        print("=" * 70)
    
    # Run connection test
    success = test_redis_connection(redis_url)
    
    print("=" * 70)
    
    # Summary and recommendations
    if success:
        print_status("🎉 All Redis tests passed!", "SUCCESS")
        print_status("Your Redis connection is working correctly!", "SUCCESS")
        print_status("You can now use Redis for caching in your application.", "SUCCESS")
    else:
        print_status("❌ Redis connection test failed!", "ERROR")
        print_status("Please check the troubleshooting tips below.", "ERROR")
    
    # Troubleshooting tips
    print("\n" + "=" * 70)
    print_status("💡 Troubleshooting Tips:", "INFO")
    print("1. Verify REDIS_URL in your .env file")
    print("2. Check if Upstash Redis instance is active")
    print("3. Verify username and password are correct")
    print("4. Ensure network connectivity")
    print("5. Check if SSL is required (use rediss:// for SSL)")
    print("6. Verify Upstash IP restrictions (if any)")
    print("7. Check Upstash dashboard for connection logs")
    
    print("\n" + "=" * 70)
    print_status("📚 Upstash Redis Resources:", "INFO")
    print("• Dashboard: https://console.upstash.com/")
    print("• Documentation: https://docs.upstash.com/redis")
    print("• Python SDK: https://docs.upstash.com/redis/sdks/python")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\n🛑 Test interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"❌ Unexpected error: {e}", "ERROR")
        sys.exit(1)