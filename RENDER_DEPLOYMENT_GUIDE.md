# Render.com Deployment Guide

## Overview
Render is ideal for this project because:
- ✅ **No package size limits** (unlike Vercel's 250MB)
- ✅ **Better Python support** with full environment management
- ✅ **Free tier with reasonable limits** (spinning instances, not serverless)
- ✅ **Handles large dependencies** (langchain, langgraph, qdrant-client)

## Architecture

```
┌─────────────────────────────────────────┐
│         Render Dashboard                │
├─────────────────────────────────────────┤
│  Frontend (Static Site)                 │
│  → React/Vite | Deployed to CDN         │
├─────────────────────────────────────────┤
│  Backend (Web Service)                  │
│  → FastAPI + uvicorn on Python 3.12     │
│  → Handles /api/* routes                │
└─────────────────────────────────────────┘
```

## Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Authorize Render to access your GitHub account

## Step 2: Connect Your Repository

1. In Render Dashboard → Click **New +**
2. Select **Web Service**
3. Connect your GitHub fork: `Darshanreddy19/deal-flow-tracker-main`
4. Configure:
   - **Name**: `dealflow-api`
   - **Runtime**: `Python 3.12`
   - **Build Command**: `pip install -r be/requirements.txt`
   - **Start Command**: `cd be && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free or Paid (free has 50 CPU-hours/month)

## Step 3: Add Environment Variables (Backend)

In Render → Web Service → Environment:

```
# If using Qdrant Cloud:
QDRANT_API_KEY=your_api_key_here
QDRANT_URL=https://your-instance.qdrant.io

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## Step 4: Deploy Backend

1. Click **Create Web Service**
2. Render will automatically deploy from GitHub
3. Wait for build to complete (~5-10 minutes)
4. Note your backend URL: `https://dealflow-api.onrender.com`

## Step 5: Deploy Frontend

1. In Render → Click **New +** → **Static Site**
2. Connect same GitHub repo
3. Configure:
   - **Name**: `dealflow-frontend`
   - **Build Command**: `cd fe && npm install && npm run build`
   - **Publish Directory**: `fe/dist`

## Step 6: Add Frontend Environment Variables

In Render → Static Site → Environment:

```
VITE_API_URL=https://dealflow-api.onrender.com
VITE_DEBUG=false
```

## Step 7: Deploy Frontend

1. Click **Create Static Site**
2. Render builds and deploys automatically
3. Your app is live at: `https://dealflow-frontend.onrender.com`

## Verify Deployment

```bash
# Test backend health
curl https://dealflow-api.onrender.com/docs

# Test from frontend
curl https://dealflow-frontend.onrender.com

# Check API calls in DevTools Console
# Open your frontend URL and look for API responses
```

---

## Troubleshooting

### Issue: Build fails with "ModuleNotFoundError"
**Cause**: Missing dependencies in `be/requirements.txt`

**Solution**:
```bash
# On your local machine
cd be
pip list | grep -E "fastapi|langchain|langgraph|qdrant"

# Add missing packages to requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push
```

Render will auto-redeploy when you push.

### Issue: API calls fail with CORS errors
**Solution**: CORS is already configured in `be/main.py` to allow all origins. Verify:

```python
# In be/main.py - should have this:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "503 Service Unavailable" on free tier
**Cause**: Free tier instances spin down after 15 minutes of inactivity

**Solution**: 
- **Upgrade to Paid** ($7/month for reliable uptime)
- Or **use Render Cron Jobs** to ping your API every 10 minutes

### Issue: Database/Qdrant connection fails
**Current Setup**: Assumes local Qdrant

**Production Setup**:
1. Use **Qdrant Cloud** (cloud.qdrant.io)
2. Get API key and URL
3. Update `be/config.py` or `be/qdrant_service.py` to use cloud credentials
4. Add credentials to Render environment variables

### Issue: Large Python packages timeout
**Solution**: Render has no size limits, so this shouldn't happen. If it does:
- Check if `requirements.txt` has unnecessary packages
- Remove unused dependencies
- Rebuild

---

## File Structure for Render

Your repo should have this structure (already set up):

```
deal-flow-tracker-main/
├── be/                          # Backend
│   ├── main.py                  # FastAPI app
│   ├── requirements.txt          # Python dependencies
│   ├── config.py
│   ├── qdrant_service.py
│   └── ...
├── fe/                          # Frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   └── ...
├── render.yaml                  # ✅ Already created
└── README.md
```

---

## Advanced: Custom Domain

To use your own domain (e.g., `dealflow.yourdomain.com`):

1. In Render → Static Site → Settings
2. Click **Add Custom Domain**
3. Enter your domain
4. Update DNS records (Render will show steps)
5. Same for backend API domain

---

## Pricing

**Free Tier**:
- 50 CPU-hours/month (one web service)
- 100 GB bandwidth/month
- Instances spin down after 15 min inactivity
- Auto-rebuild on `git push`

**Pro Plan** ($7/month):
- Unlimited CPU hours
- Reliable uptime (no spin-down)
- Priority support

---

## Local Testing Before Deployment

Test locally to ensure it works as deployed:

```bash
# Terminal 1 - Backend
cd be
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd fe
npm install
VITE_API_URL=http://localhost:8000 npm run dev

# Test
# Visit http://localhost:5173
# Open DevTools → Network tab
# Trigger API calls
```

---

## Next Steps

1. **Create Render account** → [render.com](https://render.com)
2. **Deploy Backend** → Follow Step 2-4 above
3. **Deploy Frontend** → Follow Step 5-7 above
4. **Monitor logs** → Render Dashboard shows build/runtime logs
5. **Set up monitoring** → Enable Render's health checks

---

## Support

If you encounter issues:

1. **Check Render logs**: Dashboard → Service → Logs
2. **Check frontend console**: Browser DevTools → Console
3. **Test API directly**: 
   ```bash
   curl https://dealflow-api.onrender.com/docs
   ```
4. **GitHub Issues**: Post details about the error

---

## Alternative: Docker (Advanced)

If you want to use Docker with Render:

Create `Dockerfile` in project root:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install backend
COPY be/requirements.txt ./be/
RUN pip install --no-cache-dir -r be/requirements.txt

# Install frontend
COPY fe/package*.json ./fe/
RUN cd fe && npm ci --only=production && npm run build

# Copy app code
COPY be/ ./be/
COPY fe/ ./fe/

EXPOSE 8000

CMD ["uvicorn", "be.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then in Render:
- **Runtime**: Docker
- **Build Command**: (leave blank)
- **Start Command**: (leave blank)

Render will auto-detect the Dockerfile.
