#!/bin/bash
# Connection Debug Script - Run this to test frontend-backend connectivity

echo "🔍 DealFlow Connection Diagnostic"
echo "=================================="
echo ""

# Test 1: Backend Running
echo "1️⃣ Checking if backend is running on port 8005..."
if netstat -ano | grep -q ":8005"; then
    echo "   ✅ Backend is listening on port 8005"
else
    echo "   ❌ Backend NOT running on port 8005"
    echo "   Start it with: cd be && python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload"
fi

echo ""

# Test 2: Health Endpoint
echo "2️⃣ Testing backend health endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo "   ✅ Health endpoint responding (HTTP 200)"
else
    echo "   ❌ Health endpoint failed (HTTP $response)"
fi

echo ""

# Test 3: API Documentation
echo "3️⃣ Checking API documentation..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/docs 2>/dev/null)
if [ "$response" = "200" ]; then
    echo "   ✅ Swagger docs available at http://localhost:8005/docs"
else
    echo "   ❌ API docs not available"
fi

echo ""

# Test 4: Frontend Running
echo "4️⃣ Checking if frontend is running on port 5173..."
if netstat -ano | grep -q ":5173"; then
    echo "   ✅ Frontend is running on port 5173"
else
    echo "   ❌ Frontend NOT running on port 5173"
    echo "   Start it with: cd fe && npm run dev"
fi

echo ""

# Test 5: CORS Configuration
echo "5️⃣ Checking CORS configuration..."
response=$(curl -s -H "Origin: http://localhost:5173" http://localhost:8005/health)
if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
    echo "   ✅ CORS headers present"
else
    echo "   ⚠️  CORS headers might not be configured"
fi

echo ""
echo "=================================="
echo "Quick Setup:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd be && python -m venv venv"
echo "  source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "  pip install -r requirements.txt"
echo "  python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd fe"
echo "  npm install"
echo "  VITE_API_URL=http://localhost:8005 npm run dev"
echo ""
echo "Then open http://localhost:5173 in your browser"
echo "Check browser DevTools (F12) Console tab for errors"
