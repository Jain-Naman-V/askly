#!/usr/bin/env python3
"""
Test MongoDB Atlas connection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI') or os.getenv('MONGODB_URL')
        if not mongodb_uri:
            print("❌ No MongoDB URI found in environment variables")
            return False
            
        print(f"🔗 Testing connection to: {mongodb_uri[:50]}...")
        
        # Create client
        client = AsyncIOMotorClient(mongodb_uri)
        
        # Test connection with ping
        await client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client.ai_data_agent
        print(f"📊 Database: {db.name}")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"📁 Collections: {collections}")
        
        # Test basic operations
        test_collection = db.test_connection
        
        # Insert a test document
        test_doc = {"test": "connection", "timestamp": "2024-01-01"}
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read the test document
        found_doc = await test_collection.find_one({"test": "connection"})
        print(f"✅ Test document found: {found_doc}")
        
        # Clean up test document
        await test_collection.delete_one({"test": "connection"})
        print("🧹 Test document cleaned up")
        
        # Close connection
        client.close()
        print("✅ Connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_mongodb_connection())
    if result:
        print("\n🎉 MongoDB Atlas is working correctly!")
    else:
        print("\n💥 MongoDB Atlas connection failed. Please check:")
        print("1. Your connection string is correct")
        print("2. Your IP address is whitelisted in MongoDB Atlas")
        print("3. Your username and password are correct")
        print("4. Your cluster is running")