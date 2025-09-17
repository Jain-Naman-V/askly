#!/usr/bin/env python3
"""
Test script for pagination API
"""

import requests
import json
from datetime import datetime

def test_pagination_api():
    """Test pagination functionality"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=" * 60)
    print("Testing Pagination API")
    print("=" * 60)
    
    # Test 1: Create multiple test records for pagination
    print("1. Creating test records for pagination...")
    
    test_records = []
    for i in range(25):  # Create 25 records to test pagination
        record = {
            "title": f"Test Record {i+1:02d}",
            "description": f"This is test record number {i+1} for pagination testing",
            "content": {
                "record_number": i+1,
                "test_field": f"value_{i+1}",
                "category_type": "pagination_test"
            },
            "tags": ["test", "pagination", f"record_{i+1}"],
            "category": "Testing"
        }
        
        try:
            response = requests.post(
                f"{base_url}/data/",
                json=record,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                created_record = response.json()
                test_records.append(created_record["id"])
                print(f"   ✅ Created record {i+1}: {created_record['id']}")
            else:
                print(f"   ❌ Failed to create record {i+1}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error creating record {i+1}: {e}")
    
    print(f"\\nCreated {len(test_records)} test records")
    
    # Test 2: Test pagination with different page sizes
    print("\\n2. Testing pagination with different parameters...")
    
    # Test default pagination (page 1, limit 10)
    print("\\n   Testing page 1 with default limit (10):")
    response = requests.get(f"{base_url}/data/?page=1&limit=10", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Records returned: {len(data['data'])}")
        print(f"   ✅ Total count: {data['total_count']}")
        print(f"   ✅ Pagination info: {json.dumps(data['pagination'], indent=2)}")
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
    
    # Test page 2
    print("\\n   Testing page 2:")
    response = requests.get(f"{base_url}/data/?page=2&limit=10", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Records returned: {len(data['data'])}")
        print(f"   ✅ Current page: {data['pagination']['current_page']}")
        print(f"   ✅ Has next: {data['pagination']['has_next']}")
        print(f"   ✅ Has prev: {data['pagination']['has_prev']}")
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
    
    # Test last page
    print("\\n   Testing last page:")
    response = requests.get(f"{base_url}/data/?page=1&limit=10", timeout=10)
    if response.status_code == 200:
        data = response.json()
        total_pages = data['pagination']['total_pages']
        
        # Get last page
        response = requests.get(f"{base_url}/data/?page={total_pages}&limit=10", timeout=10)
        if response.status_code == 200:
            last_page_data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ✅ Last page ({total_pages}) records: {len(last_page_data['data'])}")
            print(f"   ✅ Has next: {last_page_data['pagination']['has_next']}")
            print(f"   ✅ Has prev: {last_page_data['pagination']['has_prev']}")
        else:
            print(f"   ❌ Failed to get last page: {response.status_code}")
    
    # Test different page sizes
    print("\\n   Testing different page sizes:")
    for page_size in [5, 20]:
        response = requests.get(f"{base_url}/data/?page=1&limit={page_size}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Page size {page_size}: {len(data['data'])} records returned")
            print(f"      Total pages: {data['pagination']['total_pages']}")
        else:
            print(f"   ❌ Failed with page size {page_size}: {response.status_code}")
    
    # Test 3: Test offset-based pagination
    print("\\n3. Testing offset-based pagination:")
    response = requests.get(f"{base_url}/data/?offset=10&limit=5", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Records returned: {len(data['data'])}")
        print(f"   ✅ Offset: {data['pagination']['offset']}")
        print(f"   ✅ Current page calculated: {data['pagination']['current_page']}")
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
    
    # Test 4: Test edge cases
    print("\\n4. Testing edge cases:")
    
    # Test page 0 (should default to page 1)
    response = requests.get(f"{base_url}/data/?page=0&limit=10", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Page 0 handled correctly, current_page: {data['pagination']['current_page']}")
    
    # Test very large page number
    response = requests.get(f"{base_url}/data/?page=999&limit=10", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Large page number handled, returned {len(data['data'])} records")
    
    # Test invalid limit
    response = requests.get(f"{base_url}/data/?page=1&limit=0", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Zero limit handled, current_page: {data['pagination']['current_page']}")
    
    # Clean up - delete test records
    print("\\n5. Cleaning up test records...")
    deleted_count = 0
    for record_id in test_records:
        try:
            response = requests.delete(f"{base_url}/data/{record_id}", timeout=10)
            if response.status_code == 200:
                deleted_count += 1
        except Exception as e:
            print(f"   ⚠️ Failed to delete {record_id}: {e}")
    
    print(f"   ✅ Deleted {deleted_count}/{len(test_records)} test records")
    
    print("\\n" + "=" * 60)
    print("Pagination API test completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_pagination_api()
    except KeyboardInterrupt:
        print("\\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")