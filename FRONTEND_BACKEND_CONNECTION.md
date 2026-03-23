# HOW TO FIX: Frontend Not Connected to Backend

## Quick Diagnosis

### Step 1: Check If Both Servers Are Running

**Open a terminal and run:**

```bash
# Check if backend is listening
netstat -ano | findstr ":8005"       # Should show LISTENING

# Check if frontend is listening  
netstat -ano | findstr ":5173"       # Should show LISTENING
```

If either is missing, start them:

**Terminal 1 - Backend:**
```bash
cd be
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows
source venv/bin/activate             # Mac/Linux
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

**Terminal 2 - Frontend:**
```bash
cd fe
npm install
npm run dev
```

### Step 2: Check Browser Console for Errors

1. Open http://localhost:5173 in your browser
2. Press **F12** to open DevTools
3. Click **Console** tab
4. Look for errors like:
   - `Failed to fetch from http://localhost:8005`
   - `CORS error`
   - `Connection refused`

### Step 3: Verify Backend is Responding

In another terminal, test the backend:

```powershell
# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:8005/health"

# Or curl (if installed)
curl http://localhost:8005/health
```

You should see: `{"status":"ok"}` or similar

---

## Common Issues & Fixes

### ❌ "Cannot fetch from localhost:8005"
**Cause:** Backend not running

**Fix:**
```bash
cd be
python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

Check the output - should show:
```
Uvicorn running on http://0.0.0.0:8005
```

### ❌ "CORS error" or "blocked by CORS policy"
**Cause:** CORS not properly configured

**Fix:** Already configured in `be/main.py`. Restart backend:
```bash
# Kill the old process
Get-Process python | Stop-Process -Force

# Start fresh
python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

### ❌ "Connection refused on port 8005"
**Cause:** Backend crashed or not started

**Fix:**
1. Check terminal output for errors
2. Check if Python is installed: `python --version`
3. Check if dependencies installed: `pip list | grep fastapi`
4. Reinstall: `pip install -r requirements.txt`

### ❌ "Frontend won't load at http://localhost:5173"
**Cause:** Frontend dev server not running

**Fix:**
```bash
cd fe
npm install
npm run dev
```

Check terminal output for:
```
✓ built in 2.5s
Local: http://localhost:5173/
```

### ❌ "API call returns 404 Not Found"
**Cause:** Endpoint doesn't exist or wrong URL

**Check available endpoints:**
- Open http://localhost:8005/docs in browser
- Should see Swagger UI with all endpoints listed

**Fix:** Verify the `VITE_API_URL` is correct:
```bash
# In fe/.env, should be:
VITE_API_URL=http://localhost:8005
```

---

## Verify Connection Is Working

### Method 1: DevTools Network Tab

1. Open http://localhost:5173
2. Press F12 → Network tab
3. Click "Analyze" button *in the UI*
4. Look for a request to `http://localhost:8005/api/analyze`
5. Check the response (should be green 200 or similar)

### Method 2: Backend Logs

When you click "Analyze", you should see in the **backend terminal**:

```
INFO:     POST /api/analyze HTTP/1.1" 200 OK
```

### Method 3: API Test

Open a new terminal and test:

```powershell
$payload = @{
    deal_id = "TEST-001"
    sector = "Technology"
    parties = "Company A, Company B"
    messages = @(@{ sender = "Test"; content = "Test"; type = "email" })
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8005/api/analyze" `
    -Method POST `
    -ContentType "application/json" `
    -Body $payload
```

Should return analysis result, not an error.

---

## Step-by-Step Connection Guide

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Start backend | Terminal shows "Uvicorn running on..." |
| 2 | Check `netstat -ano \| findstr ":8005"` | Shows LISTENING |
| 3 | Start frontend | Terminal shows "✓ built in Xs" |
| 4 | Check `netstat -ano \| findstr ":5173"` | Shows LISTENING |
| 5 | Open http://localhost:5173 | See DealFlow UI with no errors |
| 6 | Open DevTools F12 | No red errors in Console tab |
| 7 | Click "Analyze" | See POST request to /api/analyze in Network tab |
| 8 | Wait 5-10 seconds | See response with analysis results |
| 9 | Check backend terminal | See POST request logged |
| 10 | Done! ✅ | Connection working! |

---

## Still Having Issues?

### Check Backend Logs

**Backend terminal should show:**

```
INFO:     started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8005 (Press CTRL+C to quit)
INFO:     POST /api/analyze HTTP/1.1" 200
```

If you see **ERROR** or **EXCEPTION**, the issue is in the backend.

### Check Frontend Logs

**Browser Console (F12) should show:**

```
✅ Analysis Complete!
```

If you see `❌ Analysis failed: ...`, the issue is in the API call.

### Check Network Quality

```bash
# Ping backend
ping localhost

# Or
Invoke-WebRequest -Uri "http://127.0.0.1:8005/health"
```

### Verify Dependencies

```bash
# Backend
cd be
pip list | findstr fastapi
pip list | findstr uvicorn

# Frontend
cd fe
npm list react
npm list vite
```

All should show versions without errors.

---

## Quick Restart Everything

```bash
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Kill all Node processes
Get-Process node | Stop-Process -Force

# Terminal 1 - Backend
cd be
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload

# Terminal 2 - Frontend
cd fe
npm run dev
```

Then open http://localhost:5173 and test again.

---

## Debug Script

Run the diagnostic script to check everything:

```bash
# Windows PowerShell
.\debug_connection.ps1

# Or copy-paste the commands manually
```

This will test:
- ✅ Backend running
- ✅ Health endpoint
- ✅ API docs
- ✅ Frontend running
- ✅ CORS configuration
- ✅ API calls

---

**If everything shows ✅, your connection is working!**

If you see ❌ marks, follow the fix instructions above for that specific issue.
