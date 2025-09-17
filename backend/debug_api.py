#!/usr/bin/env python3
"""
Debug script to test API responses and data format
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test API endpoints and check data format"""
    base_url = "http://localhost:8000/api/v1"
    
    # Test 1: Get all data
    print("=" * 60)
    print("Testing GET /api/v1/data/")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/data/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle both old and new response formats
            if isinstance(data, list):
                # Old format (direct list)
                records = data
                total_count = len(records)
                pagination_info = "N/A (old format)"
            else:
                # New format (with pagination)
                records = data.get('data', [])
                total_count = data.get('total_count', 0)
                pagination_info = json.dumps(data.get('pagination', {}), indent=2)
            
            print(f"Number of records: {len(records)}")
            print(f"Total count: {total_count}")
            
            if records:
                print("\nFirst record:")
                print(json.dumps(records[0], indent=2, default=str))
                
                # Check specific fields
                first_record = records[0]
                print(f"\nField analysis:")
                print(f"ID: {first_record.get('id')}")
                print(f"Title: {first_record.get('title')}")
                print(f"Created At: {first_record.get('created_at')}")
                print(f"Content Type: {type(first_record.get('content'))}")
                print(f"Tags Type: {type(first_record.get('tags'))}")
                
                if not isinstance(data, list):
                    print(f"\nPagination info:")
                    print(pagination_info)
            else:
                print("No records found")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing GET /data/: {e}")
    
    # Test 2: Create a new record
    print("\n" + "=" * 60)
    print("Testing POST /api/v1/data/")
    print("=" * 60)
    
    test_record = {
        "title": "Debug Test Record",
        "description": "Testing data format and API response",
        "content": {
            "name": "Debug User",
            "email": "debug@test.com",
            "age": 25,
            "city": "Test City",
            "active": True
        },
        "tags": ["debug", "test", "api"],
        "category": "Testing"
    }
    
    try:
        response = requests.post(
            f"{base_url}/data/",
            json=test_record,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            data = response.json()
            print("Created record:")
            print(json.dumps(data, indent=2, default=str))
            
            # Store the ID for cleanup
            record_id = data.get('id')
            
            # Test 3: Get the specific record
            if record_id:
                print(f"\n" + "=" * 60)
                print(f"Testing GET /api/v1/data/{record_id}")
                print("=" * 60)
                
                get_response = requests.get(f"{base_url}/data/{record_id}", timeout=10)
                print(f"Status: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    single_data = get_response.json()
                    print("Retrieved record:")
                    print(json.dumps(single_data, indent=2, default=str))
                else:
                    print(f"Error: {get_response.text}")
            
            # Test 4: Analytics endpoints
            print(f"\n" + "=" * 60)
            print("Testing analytics endpoints")
            print("=" * 60)
            
            # Categories
            cat_response = requests.get(f"{base_url}/data/analytics/categories", timeout=10)
            print(f"Categories Status: {cat_response.status_code}")
            if cat_response.status_code == 200:
                cat_data = cat_response.json()
                print("Categories data:")
                print(json.dumps(cat_data, indent=2))
            
            # Time distribution
            time_response = requests.get(f"{base_url}/data/analytics/time-distribution", timeout=10)
            print(f"Time Distribution Status: {time_response.status_code}")
            if time_response.status_code == 200:
                time_data = time_response.json()
                print("Time distribution data:")
                print(json.dumps(time_data, indent=2))
            
            # Clean up - delete the test record
            if record_id:
                print(f"\n" + "=" * 60)
                print(f"Cleaning up - deleting record {record_id}")
                print("=" * 60)
                
                delete_response = requests.delete(f"{base_url}/data/{record_id}", timeout=10)
                print(f"Delete Status: {delete_response.status_code}")
                if delete_response.status_code == 200:
                    delete_data = delete_response.json()
                    print("Delete response:")
                    print(json.dumps(delete_data, indent=2))
            
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing POST /data/: {e}")

def test_datetime_conversion():
    """Test datetime conversion issues"""
    print("\n" + "=" * 60)
    print("Testing datetime conversion")
    print("=" * 60)
    
    # The timestamp from your MongoDB document
    timestamp_ms = 1758135020588
    
    print(f"Original timestamp (ms): {timestamp_ms}")
    
    # Convert from milliseconds
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    print(f"Converted datetime: {dt}")
    print(f"ISO format: {dt.isoformat()}")
    
    # Current time for comparison
    now = datetime.utcnow()
    print(f"Current UTC time: {now}")
    print(f"Current timestamp (ms): {int(now.timestamp() * 1000)}")

if __name__ == "__main__":
    # Test datetime conversion first
    test_datetime_conversion()
    
    # Test API endpoints
    try:
        test_api_endpoints()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")