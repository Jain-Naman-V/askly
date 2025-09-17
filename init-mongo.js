// MongoDB initialization script
db = db.getSiblingDB('ai_data_agent');

// Create collections
db.createCollection('structured_data');
db.createCollection('analysis_results');
db.createCollection('search_analytics');

// Create indexes for better performance
db.structured_data.createIndex({ "id": 1 }, { unique: true });
db.structured_data.createIndex({ "title": "text", "description": "text", "content": "text", "tags": "text" });
db.structured_data.createIndex({ "status": 1, "category": 1, "created_at": -1 });
db.structured_data.createIndex({ "tags": 1, "created_at": -1 });
db.structured_data.createIndex({ "created_by": 1, "created_at": -1 });

// Create sample data
db.structured_data.insertMany([
  {
    "id": "sample-1",
    "title": "Sample User Record",
    "description": "A sample user record for demonstration",
    "content": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "age": 30,
      "city": "New York",
      "occupation": "Software Engineer"
    },
    "tags": ["user", "sample", "demo"],
    "category": "users",
    "status": "active",
    "metadata": {
      "source": "demo",
      "version": "1.0"
    },
    "created_at": new Date(),
    "updated_at": new Date(),
    "created_by": "system",
    "updated_by": "system",
    "keywords": ["john", "doe", "software", "engineer"],
    "search_text": "Sample User Record A sample user record for demonstration John Doe john.doe@example.com Software Engineer"
  },
  {
    "id": "sample-2",
    "title": "Product Information",
    "description": "Sample product data",
    "content": {
      "name": "AI Data Agent",
      "price": 99.99,
      "category": "Software",
      "features": ["AI-powered", "Real-time search", "Data visualization"],
      "availability": true
    },
    "tags": ["product", "software", "ai"],
    "category": "products",
    "status": "active",
    "metadata": {
      "source": "catalog",
      "version": "1.0"
    },
    "created_at": new Date(),
    "updated_at": new Date(),
    "created_by": "system",
    "updated_by": "system",
    "keywords": ["ai", "data", "agent", "software"],
    "search_text": "Product Information Sample product data AI Data Agent Software AI-powered Real-time search Data visualization"
  }
]);

print('MongoDB initialization completed successfully!');