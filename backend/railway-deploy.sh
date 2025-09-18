#!/bin/bash

# Railway deployment script
echo "Starting Railway deployment preparation..."

# Copy lightweight AI service for deployment
cp ai_service_railway.py app/services/ai_service.py

# Use lightweight requirements
cp requirements-railway.txt requirements.txt

echo "Railway optimization complete!"