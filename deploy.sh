#!/bin/bash

# AI Data Agent Deployment Script
# This script sets up and deploys the AI Data Agent application

set -e  # Exit on any error

echo "🚀 Starting AI Data Agent Deployment..."

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the ai-data-agent root directory"
    exit 1
fi

# Check for git
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed"
    exit 1
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
build/
dist/
.next/

# Python virtual environment
venv/
env/
.venv/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Coverage reports
coverage/
.nyc_output

# Database
*.db
*.sqlite

# Temporary files
*.tmp
*.temp

EOF
fi

# Add remote origin if not set
if ! git remote get-url origin &> /dev/null; then
    echo "⚠️  Warning: No git remote 'origin' found"
    echo "Please add your GitHub repository URL:"
    echo "git remote add origin https://github.com/yourusername/ai-data-agent.git"
    echo ""
fi

# Stage all changes
echo "📦 Staging files for commit..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit changes
    COMMIT_MSG="Deploy: $(date +'%Y-%m-%d %H:%M:%S')"
    echo "💾 Committing changes: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
fi

# Push to GitHub if remote exists
if git remote get-url origin &> /dev/null; then
    echo "📡 Pushing to GitHub..."
    
    # Check if main branch exists
    if git show-ref --verify --quiet refs/heads/main; then
        git push origin main
    else
        # Create main branch and push
        git branch -M main
        git push -u origin main
    fi
    
    echo "✅ Code pushed to GitHub successfully!"
else
    echo "⚠️  Skipped push - no remote origin configured"
fi

echo ""
echo "🎉 Deployment process completed!"
echo ""
echo "Next steps:"
echo "1. 📊 Set up MongoDB Atlas: https://www.mongodb.com/atlas"
echo "2. 🔄 Set up Upstash Redis: https://upstash.com/"
echo "3. 🚂 Deploy Backend to Railway: https://railway.app/"
echo "4. ⚡ Deploy Frontend to Vercel: https://vercel.com/"
echo ""
echo "📖 See COMPLETE_DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "⏳ Auto-deployment will start once you connect to Railway and Vercel"
echo "📊 Monitor deployment status:"
echo "   - Railway: https://railway.app/dashboard"
echo "   - Vercel: https://vercel.com/dashboard"
echo ""
echo "🌐 Your app will be live at:"
echo "   - Frontend: https://your-project.vercel.app"
echo "   - Backend: https://your-app.railway.app"
echo "   - API Docs: https://your-app.railway.app/docs"

# Check if required tools are installed
check_dependencies() {
    echo "📋 Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "⚠️  Docker is not installed. Docker deployment will not be available."
    fi
    
    echo "✅ Dependencies check completed."
}

# Setup backend
setup_backend() {
    echo "🔧 Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ Virtual environment created."
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Backend setup completed."
    cd ..
}

# Setup frontend
setup_frontend() {
    echo "🔧 Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    npm install
    
    # Build for production
    npm run build
    
    echo "✅ Frontend setup completed."
    cd ..
}

# Setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Setup root environment file
    if [ ! -f ".env" ]; then
        if [ -f ".env.development.example" ]; then
            cp .env.development.example .env
            echo "✅ Root .env created from development template."
        else
            cp .env.production.example .env
            echo "✅ Root .env created from production template."
        fi
        echo "⚠️  Please update .env with your actual configuration values."
    else
        echo "✅ Root .env already exists."
    fi
    
    # Setup backend environment file
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            echo "✅ Backend .env created from template."
        else
            echo "MONGODB_URL=mongodb://localhost:27017" > backend/.env
            echo "GROQ_API_KEY=your_groq_api_key_here" >> backend/.env
            echo "✅ Basic backend .env created."
        fi
        echo "⚠️  Please update backend/.env with your actual configuration values."
    else
        echo "✅ Backend .env already exists."
    fi
    
    # Setup frontend environment file
    if [ ! -f "frontend/.env.local" ]; then
        if [ -f "frontend/.env.example" ]; then
            cp frontend/.env.example frontend/.env.local
            echo "✅ Frontend .env.local created from template."
        else
            echo "REACT_APP_API_BASE_URL=http://localhost:8000" > frontend/.env.local
            echo "REACT_APP_WS_URL=ws://localhost:8000/ws" >> frontend/.env.local
            echo "REACT_APP_ENV=development" >> frontend/.env.local
            echo "✅ Basic frontend .env.local created."
        fi
    else
        echo "✅ Frontend .env.local already exists."
    fi
    
    echo "✅ Environment setup completed."
}

# Setup database
setup_database() {
    echo "🔧 Setting up database..."
    
    # Check if MongoDB is running
    if ! pgrep -x "mongod" > /dev/null; then
        echo "⚠️  MongoDB is not running. Please start MongoDB service."
        echo "   - On Ubuntu/Debian: sudo systemctl start mongod"
        echo "   - On macOS: brew services start mongodb-community"
        echo "   - On Windows: net start MongoDB"
    else
        echo "✅ MongoDB is running."
    fi
    
    # Check if Redis is running
    if ! pgrep -x "redis-server" > /dev/null; then
        echo "⚠️  Redis is not running. Please start Redis service."
        echo "   - On Ubuntu/Debian: sudo systemctl start redis"
        echo "   - On macOS: brew services start redis"
        echo "   - On Windows: redis-server"
    else
        echo "✅ Redis is running."
    fi
}

# Create sample data
create_sample_data() {
    echo "📊 Creating sample data..."
    
    cd backend
    source venv/bin/activate
    
    # Run sample data creation script if it exists
    if [ -f "create_sample_data.py" ]; then
        python create_sample_data.py
        echo "✅ Sample data created."
    else
        echo "⚠️  Sample data script not found. Skipping..."
    fi
    
    cd ..
}

# Start services
start_services() {
    echo "🚀 Starting services..."
    
    # Start backend
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
    # Start frontend
    echo "Starting frontend server..."
    cd frontend
    nohup npm start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    
    echo "✅ Services started."
    echo "📝 Backend PID: $BACKEND_PID (saved to backend.pid)"
    echo "📝 Frontend PID: $FRONTEND_PID (saved to frontend.pid)"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔗 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
}

# Create logs directory
mkdir -p logs

# Main deployment flow
main() {
    echo "🎯 AI Data Agent Deployment Script"
    echo "=================================="
    
    check_dependencies
    setup_environment
    setup_backend
    setup_frontend
    setup_database
    create_sample_data
    start_services
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "=================================="
    echo "🌐 Application URL: http://localhost:3000"
    echo "🔗 API Documentation: http://localhost:8000/docs"
    echo "📝 Logs directory: ./logs/"
    echo ""
    echo "To stop the services:"
    echo "  kill \$(cat backend.pid) \$(cat frontend.pid)"
    echo ""
    echo "To check logs:"
    echo "  tail -f logs/backend.log"
    echo "  tail -f logs/frontend.log"
}

# Handle script arguments
case "${1:-}" in
    "backend")
        setup_backend
        ;;
    "frontend")
        setup_frontend
        ;;
    "deps")
        check_dependencies
        ;;
    "env")
        setup_environment
        ;;
    "db")
        setup_database
        ;;
    "start")
        start_services
        ;;
    *)
        main
        ;;
esac