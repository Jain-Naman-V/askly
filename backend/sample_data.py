#!/usr/bin/env python3
"""
Sample data insertion script for AI Data Agent
"""

import asyncio
import json
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import random
import uuid

# Sample data for testing
SAMPLE_RECORDS = [
    {
        "id": str(uuid.uuid4()),
        "title": "Q4 Sales Report",
        "description": "Quarterly sales analysis showing 15% growth in revenue",
        "content": {
            "revenue": 1250000,
            "growth_rate": 0.15,
            "top_products": ["Product A", "Product B", "Product C"],
            "region": "North America"
        },
        "category": "Sales",
        "tags": ["sales", "revenue", "quarterly", "growth"],
        "created_at": datetime.now() - timedelta(days=1),
        "metadata": {
            "author": "Sales Team",
            "department": "Sales",
            "priority": "high"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Customer Satisfaction Survey Results",
        "description": "Latest customer feedback showing improved satisfaction scores",
        "content": {
            "satisfaction_score": 4.2,
            "response_rate": 0.78,
            "top_feedback": ["Great service", "Fast delivery", "Quality products"],
            "areas_for_improvement": ["Pricing", "Website navigation"]
        },
        "category": "Customer Service",
        "tags": ["customer", "satisfaction", "survey", "feedback"],
        "created_at": datetime.now() - timedelta(hours=6),
        "metadata": {
            "author": "Customer Success Team",
            "department": "Customer Service",
            "priority": "medium"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Product Launch Analytics",
        "description": "Performance metrics for the new product line launched last month",
        "content": {
            "units_sold": 2500,
            "conversion_rate": 0.12,
            "customer_acquisition_cost": 45.50,
            "market_response": "Positive"
        },
        "category": "Product",
        "tags": ["product", "launch", "analytics", "performance"],
        "created_at": datetime.now() - timedelta(hours=12),
        "metadata": {
            "author": "Product Team",
            "department": "Product Management",
            "priority": "high"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Technology Infrastructure Update",
        "description": "Server migration and performance improvements completed",
        "content": {
            "servers_migrated": 25,
            "downtime_minutes": 30,
            "performance_improvement": "40%",
            "cost_savings": 15000
        },
        "category": "Technology",
        "tags": ["infrastructure", "migration", "performance", "servers"],
        "created_at": datetime.now() - timedelta(hours=18),
        "metadata": {
            "author": "IT Team",
            "department": "Technology",
            "priority": "medium"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Employee Training Program Results",
        "description": "Completion rates and feedback from the latest training initiative",
        "content": {
            "participants": 150,
            "completion_rate": 0.92,
            "average_score": 87.5,
            "feedback_rating": 4.6
        },
        "category": "Human Resources",
        "tags": ["training", "employees", "education", "development"],
        "created_at": datetime.now() - timedelta(hours=24),
        "metadata": {
            "author": "HR Team",
            "department": "Human Resources",
            "priority": "low"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Financial Performance Summary",
        "description": "Monthly financial overview with key metrics and projections",
        "content": {
            "total_revenue": 875000,
            "expenses": 620000,
            "net_profit": 255000,
            "profit_margin": 0.29,
            "cash_flow": "Positive"
        },
        "category": "Finance",
        "tags": ["finance", "revenue", "profit", "monthly"],
        "created_at": datetime.now() - timedelta(minutes=30),
        "metadata": {
            "author": "Finance Team",
            "department": "Finance",
            "priority": "high"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Market Research Insights",
        "description": "Latest market trends and competitor analysis for strategic planning",
        "content": {
            "market_size": "2.5B",
            "growth_potential": "High",
            "top_competitors": ["Competitor A", "Competitor B"],
            "market_share": 0.08
        },
        "category": "Marketing",
        "tags": ["market", "research", "competitors", "strategy"],
        "created_at": datetime.now() - timedelta(minutes=45),
        "metadata": {
            "author": "Marketing Team",
            "department": "Marketing",
            "priority": "medium"
        }
    }
]

async def insert_sample_data():
    """Insert sample data into MongoDB"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ai_data_agent
    collection = db.structured_data
    
    try:
        # Drop problematic indexes first
        try:
            await collection.drop_index("unique_id_index")
            print("Dropped unique_id_index")
        except:
            pass  # Index might not exist
            
        # Clear existing data (optional)
        await collection.delete_many({})
        print("Cleared existing data")
        
        # Insert sample records
        result = await collection.insert_many(SAMPLE_RECORDS)
        print(f"Inserted {len(result.inserted_ids)} sample records")
        
        # Create text index for search
        await collection.create_index([
            ("title", "text"),
            ("description", "text"),
            ("tags", "text")
        ])
        print("Created text search index")
        
        # Create other useful indexes
        await collection.create_index("category")
        await collection.create_index("created_at")
        await collection.create_index("tags")
        print("Created additional indexes")
        
        print("Sample data insertion completed successfully!")
        
        # Display summary
        total_count = await collection.count_documents({})
        categories = await collection.distinct("category")
        print(f"\\nDatabase Summary:")
        print(f"Total records: {total_count}")
        print(f"Categories: {', '.join(categories)}")
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(insert_sample_data())