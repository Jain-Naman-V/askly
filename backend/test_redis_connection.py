#!/usr/bin/env python3
"""
Redis Connection Test Script for Upstash/Stash Redis
"""

import asyncio
import aioredis
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

def test_sync_redis(redis_url):
    """Test Redis connection using synchronous redis-py"""
    print_status("Testing synchronous Redis connection...", "INFO")
    
    try:
        # Create Redis client
        client = redis.from_url(redis_url, socket_timeout=10, socket_connect_timeout=10)
        
        # Test ping
        response = client.ping()
        if response:
            print_status("✅ Synchronous Redis PING successful", "SUCCESS")
        else:
            print_status("❌ Synchronous Redis PING failed", "ERROR")
            return False
        
        # Test basic operations
        test_key = "test_connection_key"
        test_value = "Hello from Python!"
        
        # Set a value
        client.set(test_key, test_value, ex=60)  # Expires in 60 seconds
        print_status(f"✅ SET operation successful: {test_key} = {test_value}", "SUCCESS")
        
        # Get the value
        retrieved_value = client.get(test_key)
        if retrieved_value:
            decoded_value = retrieved_value.decode('utf-8')
            print_status(f"✅ GET operation successful: {decoded_value}", "SUCCESS")
        else:
            print_status("❌ GET operation failed", "ERROR")
            return False
        
        # Delete the test key
        deleted = client.delete(test_key)
        if deleted:
            print_status("✅ DELETE operation successful", "SUCCESS")
        else:
            print_status("❌ DELETE operation failed", "ERROR")
        
        # Get Redis info
        try:
            info = client.info()
            print_status(f"✅ Redis Server Version: {info.get('redis_version', 'Unknown')}", "INFO")
            print_status(f"✅ Connected Clients: {info.get('connected_clients', 'Unknown')}", "INFO")
            print_status(f"✅ Used Memory: {info.get('used_memory_human', 'Unknown')}", "INFO")
        except Exception as e:
            print_status(f"⚠️  Could not retrieve Redis info: {e}", "WARNING")
        
        client.close()
        return True
        
    except redis.ConnectionError as e:
        print_status(f"❌ Redis connection error: {e}", "ERROR")
        return False
    except redis.TimeoutError as e:
        print_status(f"❌ Redis timeout error: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ Unexpected error: {e}", "ERROR")
        return False

async def test_async_redis(redis_url):
    """Test Redis connection using asynchronous aioredis"""
    print_status("Testing asynchronous Redis connection...", "INFO")
    
    try:
        # Create async Redis client
        client = aioredis.from_url(
            redis_url,
            socket_timeout=10,
            socket_connect_timeout=10,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test ping
        response = await client.ping()
        if response:
            print_status("✅ Asynchronous Redis PING successful", "SUCCESS")
        else:
            print_status("❌ Asynchronous Redis PING failed", "ERROR")
            await client.close()
            return False
        
        # Test basic operations
        test_key = "async_test_connection_key"
        test_value = "Hello from Async Python!"
        
        # Set a value
        await client.set(test_key, test_value, ex=60)  # Expires in 60 seconds
        print_status(f"✅ Async SET operation successful: {test_key} = {test_value}", "SUCCESS")
        
        # Get the value
        retrieved_value = await client.get(test_key)
        if retrieved_value:
            decoded_value = retrieved_value.decode('utf-8')
            print_status(f"✅ Async GET operation successful: {decoded_value}", "SUCCESS")
        else:
            print_status("❌ Async GET operation failed", "ERROR")
            await client.close()
            return False
        
        # Delete the test key
        deleted = await client.delete(test_key)
        if deleted:
            print_status("✅ Async DELETE operation successful", "SUCCESS")
        else:
            print_status("❌ Async DELETE operation failed", "ERROR")
        
        # Test pipeline operations
        pipe = client.pipeline()
        pipe.set("pipeline_test_1", "value1", ex=60)
        pipe.set("pipeline_test_2", "value2", ex=60)
        pipe.get("pipeline_test_1")
        pipe.get("pipeline_test_2")
        pipe.delete("pipeline_test_1", "pipeline_test_2")
        
        results = await pipe.execute()
        print_status(f"✅ Pipeline operations successful: {len(results)} operations", "SUCCESS")
        
        await client.close()
        return True
        
    except aioredis.ConnectionError as e:
        print_status(f"❌ Async Redis connection error: {e}", "ERROR")
        return False
    except aioredis.TimeoutError as e:
        print_status(f"❌ Async Redis timeout error: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ Async unexpected error: {e}", "ERROR")
        return False

def test_redis_cli_command(redis_url):
    """Test Redis connection using redis-cli command if available"""
    print_status("Testing Redis CLI connection...", "INFO")
    
    try:
        import subprocess
        result = subprocess.run(
            ["redis-cli", "-u", redis_url, "ping"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "PONG" in result.stdout:
            print_status("✅ Redis CLI connection successful", "SUCCESS")
            return True
        else:
            print_status(f"❌ Redis CLI failed: {result.stderr}", "ERROR")
            return False
    except subprocess.TimeoutExpired:
        print_status("❌ Redis CLI timeout", "ERROR")
        return False
    except FileNotFoundError:
        print_status("⚠️  redis-cli not found (this is normal)", "WARNING")
        return False
    except Exception as e:
        print_status(f"❌ Redis CLI error: {e}", "ERROR")
        return False

async def main():
    """Main test function"""
    print_status("🔍 Redis Connection Test Starting...", "INFO")
    print("=" * 60)
    
    # Get Redis URL from environment
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url:
        print_status("❌ REDIS_URL environment variable not found!", "ERROR")
        print_status("Please set REDIS_URL in your .env file", "INFO")
        return
    
    # Parse and display connection info
    parsed = parse_redis_url(redis_url)
    if parsed:
        print_status(f"Redis Host: {parsed['hostname']}", "INFO")
        print_status(f"Redis Port: {parsed['port']}", "INFO")
        print_status(f"Redis Scheme: {parsed['scheme']}", "INFO")
        print_status(f"Username: {'***' if parsed['username'] else 'None'}", "INFO")
        print_status(f"Password: {'***' if parsed['password'] else 'None'}", "INFO")
        print("=" * 60)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Synchronous Redis
    if test_sync_redis(redis_url):
        tests_passed += 1
    print("-" * 40)
    
    # Test 2: Asynchronous Redis
    if await test_async_redis(redis_url):
        tests_passed += 1
    print("-" * 40)
    
    # Test 3: Redis CLI (optional)
    if test_redis_cli_command(redis_url):
        tests_passed += 1
    else:
        total_tests = 2  # Don't count CLI test if redis-cli is not available
    
    print("=" * 60)
    
    # Summary
    if tests_passed == total_tests:
        print_status(f"🎉 All tests passed! ({tests_passed}/{total_tests})", "SUCCESS")
        print_status("Your Redis connection is working correctly!", "SUCCESS")
    elif tests_passed > 0:
        print_status(f"⚠️  Partial success: ({tests_passed}/{total_tests}) tests passed", "WARNING")
        print_status("Some Redis functionality may work but check the errors above", "WARNING")
    else:
        print_status(f"❌ All tests failed! ({tests_passed}/{total_tests})", "ERROR")
        print_status("Please check your Redis configuration and network connectivity", "ERROR")
    
    # Additional troubleshooting tips
    print("\n" + "=" * 60)
    print_status("💡 Troubleshooting Tips:", "INFO")
    print("1. Verify your REDIS_URL in the .env file")
    print("2. Check if your Redis service is running")
    print("3. Ensure firewall/network allows connections")
    print("4. Verify credentials are correct")
    print("5. Check if SSL/TLS is required (rediss:// vs redis://)")
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_status("\n🛑 Test interrupted by user", "WARNING")
    except Exception as e:
        print_status(f"❌ Unexpected error: {e}", "ERROR")
        sys.exit(1)