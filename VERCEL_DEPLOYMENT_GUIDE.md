# Deploy to Vercel - Complete Guide

## Overview
Your app will be deployed to Vercel with:
- **Frontend**: React + Vite → Vercel hosting
- **Backend**: FastAPI → Vercel Serverless Functions (Python)
- **API Routes**: `/api/*` → Routed to serverless functions

## Prerequisites
- Vercel account (vercel.com)
- GitHub repository with this code
- Node.js & npm installed locally
- Python 3.12 installed

## Step-by-Step Deployment

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Create Vercel Project

**Option A: Use Vercel CLI (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from root directory
cd deal-flow-tracker-main
vercel
```

**Option B: Use Vercel Dashboard**
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Vercel will auto-detect the configuration
4. Click "Deploy"

### 3. Set Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

**For Production:**
```
VITE_API_URL=/api
```

**For Preview/Development (optional):**
```
VITE_API_URL=/api
```

### 4. Configure Backend Dependencies

The `requirements.txt` will be installed automatically. Key dependencies:
- fastapi
- uvicorn
- langchain-core
- langgraph
- qdrant-client
- etc.

**Note**: Large packages may hit Vercel's 250MB limit. If you get build errors:
1. Check which packages are largest
2. Consider moving to Railway.app instead (better for Python backends)

### 5. Verify Deployment

Once deployed:
1. Visit your Vercel domain (e.g., `your-app.vercel.app`)
2. Test the frontend loads correctly
3. Open DevTools → Network tab
4. Trigger an API call and verify `/api/*` returns data

### 6. Update Repository Settings

Update [fe/.env.example](fe/.env.example) with production URL:
```env
VITE_API_URL=/api
```

---

## Troubleshooting

### Issue: Build fails with "Package too large"
**Solution**: Move to Railway.app or Render.com (better for Python backends)

### Issue: API calls fail with 404
**Solution**: Check that route handlers are properly exported in `be/main.py`

### Issue: CORS errors
**Solution**: Already configured in `be/api/index.py` - all origins allowed

### Issue: Environment variables not loading
**Solution**: 
1. Verify variables set in Vercel dashboard
2. Frontend must use `VITE_` prefix
3. Redeploy after adding env vars

### Issue: Qdrant/Database connection fails
**Current Setup**: Assumes Qdrant runs locally
**Solution for Production**: 
1. Use Qdrant Cloud (cloud.qdrant.io)
2. Update connection string in `be/config.py`
3. Add credentials to Vercel environment variables

---

## Local Testing Before Deployment

Test that your app works exactly as deployed:

### Terminal 1 - Backend
```bash
cd be
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8005
```

### Terminal 2 - Frontend
```bash
cd fe
npm install
VITE_API_URL=http://localhost:8005 npm run dev
```

### Terminal 3 - Test APIs
```bash
# Test backend health
curl http://localhost:8005/docs

# Test from frontend origin
curl -X POST http://localhost:8005/analyze \
  -H "Content-Type: application/json" \
  -d '{"deal_id": "test", "sector": "tech", "parties": "A,B", "messages": []}'
```

---

## Post-Deployment Checklist

- [ ] Frontend loads at your Vercel domain
- [ ] API calls work from frontend
- [ ] No CORS errors in console
- [ ] Environment variables are correctly set
- [ ] Database connections work (Qdrant, etc.)
- [ ] All AI/LLM features function correctly
- [ ] Performance is acceptable

---

## Alternative: Use Railway.app Instead

If Vercel serverless is too limited for your Python backend, use Railway:

1. Go to [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Select the `be/` directory as the root
4. Set `PYTHON_CMD: uvicorn main:app --host 0.0.0.0 --port 8000`
5. Update frontend `VITE_API_URL` to your Railway URL

**Advantages**:
- Better Python support
- No package size limits
- Full background process support

---

## Questions?

Check these files for more details:
- [be/main.py](be/main.py) - FastAPI app definition
- [fe/src/lib/api.ts](fe/src/lib/api.ts) - Frontend API client
- [INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md) - Integration details
