#!/bin/bash

# Start Prediction Marketplace Servers

echo "Starting Prediction Marketplace..."

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $DJANGO_PID $REACT_PID 2>/dev/null
    exit
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start Django backend
echo "Starting Django backend on port 8000..."
cd /Users/benjones/prediction_marketplace
source venv/bin/activate
python manage.py runserver &
DJANGO_PID=$!

# Wait a moment for Django to start
sleep 3

# Start React frontend
echo "Starting React frontend on port 3000..."
cd frontend
npm start &
REACT_PID=$!

echo ""
echo "🚀 Prediction Marketplace is running!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "⚙️  Admin Panel: http://localhost:8000/admin"
echo ""
echo "Sample users:"
echo "  Admin: admin / admin123"
echo "  User: trader1 / password123"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
