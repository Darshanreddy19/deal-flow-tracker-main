# Connection Debug - Windows PowerShell

Write-Host "🔍 DealFlow Connection Diagnostic" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend Running
Write-Host "1️⃣ Checking if backend is running on port 8005..." -ForegroundColor Yellow
$backend = netstat -ano | Select-String ":8005"
if ($backend) {
    Write-Host "   ✅ Backend is listening on port 8005" -ForegroundColor Green
} else {
    Write-Host "   ❌ Backend NOT running on port 8005" -ForegroundColor Red
    Write-Host "   Start it with: cd be; python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload" -ForegroundColor Gray
}

Write-Host ""

# Test 2: Health Endpoint
Write-Host "2️⃣ Testing backend health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8005/health" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Health endpoint responding (HTTP 200)" -ForegroundColor Green
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Health endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: API Documentation
Write-Host "3️⃣ Checking API documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8005/docs" -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Swagger docs available at http://localhost:8005/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ API docs not available" -ForegroundColor Red
}

Write-Host ""

# Test 4: Frontend Running
Write-Host "4️⃣ Checking if frontend is running on port 5173..." -ForegroundColor Yellow
$frontend = netstat -ano | Select-String ":5173"
if ($frontend) {
    Write-Host "   ✅ Frontend is running on port 5173" -ForegroundColor Green
} else {
    Write-Host "   ❌ Frontend NOT running on port 5173" -ForegroundColor Red
    Write-Host "   Start it with: cd fe; npm run dev" -ForegroundColor Gray
}

Write-Host ""

# Test 5: Test API Call
Write-Host "5️⃣ Testing API call to /api/analyze..." -ForegroundColor Yellow
try {
    $payload = @{
        deal_id = "TEST-001"
        sector = "Technology"
        parties = "Company A, Company B"
        messages = @(
            @{
                sender = "Test"
                content = "Test message"
                type = "email"
            }
        )
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8005/api/analyze" `
        -Method POST `
        -ContentType "application/json" `
        -Body $payload `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    Write-Host "   ✅ API responded with status $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API call failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Quick Setup:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Green
Write-Host "  cd be" -ForegroundColor Gray
Write-Host "  python -m venv venv" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "  python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Green
Write-Host "  cd fe" -ForegroundColor Gray
Write-Host "  npm install" -ForegroundColor Gray
Write-Host "  npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "Then open http://localhost:5173 in your browser" -ForegroundColor Cyan
Write-Host "Check browser DevTools F12 Console tab for errors" -ForegroundColor Cyan
