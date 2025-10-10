#!/bin/bash

echo "🎵 Setting up Shazam Clone Frontend"
echo "=================================="

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create environment file
echo "⚙️  Creating environment configuration..."
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG=true
EOF

echo "✅ Frontend setup complete!"
echo ""
echo "🚀 To start the frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "🌐 The app will be available at http://localhost:3000"
echo "🔗 Make sure your backend is running on http://localhost:8000"