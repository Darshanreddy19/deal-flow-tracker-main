# Qdrant Integration Guide

## Overview
Your DealFlow application now supports fetching deal data from Qdrant vector database. The synthetic data from `be/data/synthetic_data.json` can be loaded and queried through both backend APIs and the React frontend.

## Setup Steps

### 1. Load Synthetic Data into Qdrant

From the backend directory (`be/`), run:

```bash
python load_synthetic_deals.py
```

This will:
- Read all deals from `data/synthetic_data.json`
- Generate embeddings for each deal
- Upsert them into Qdrant with searchable metadata
- Print confirmation messages for each deal loaded

### 2. Verify Qdrant Connection

Make sure you have environment variables set:
```
QDRANT_URL=<your-qdrant-url>
QDRANT_API_KEY=<your-api-key>
```

## Backend Endpoints

All endpoints are available at `http://localhost:8080`:

### Get All Deals from Qdrant
```
GET /api/qdrant/deals?limit=10
```

**Response:**
```json
{
  "success": true,
  "source": "qdrant",
  "count": 10,
  "data": [
    {
      "deal_id": "SBER-IND-RU-2026-005",
      "sector": "Metals / Commodities",
      "parties": {
        "client": "Northern Steel LLC (Russian Federation)",
        "supplier": "Tata Steel India (India)",
        "specialist": "Priya Nair (Sber BD India - Mumbai Trade Desk)"
      },
      "status": "Settling / FX Conversion",
      "bottleneck": "INR-RUB settlement timing and eBRC documentation for tax incentives",
      "action_items": [...],
      "communication_history": [...],
      "confidence_score": 0.92
    }
  ]
}
```

### Search Deals
```
GET /api/qdrant/deals/search/{query}?limit=5
```

Examples:
- `/api/qdrant/deals/search/Pharmaceuticals` - Find pharma deals
- `/api/qdrant/deals/search/Blocked` - Find blocked deals
- `/api/qdrant/deals/search/FX` - Find FX-related deals

### Get Specific Deal
```
GET /api/qdrant/deals/{deal_id}
```

## Frontend Usage

### Hook: useQdrantDeals

Use the `useQdrantDeals` hook in your React components:

```typescript
import { useQdrantDeals } from '@/hooks/useQdrantDeals';

function MyComponent() {
  const { fetchAllDeals, searchDeals, fetchDealById, loading, error } = useQdrantDeals();

  // Fetch all deals
  const handleFetchAll = async () => {
    const deals = await fetchAllDeals(10);
    console.log(deals);
  };

  // Search for deals
  const handleSearch = async () => {
    const results = await searchDeals('Pharmaceuticals', 5);
    console.log(results);
  };

  // Get specific deal
  const handleGetDeal = async () => {
    const deal = await fetchDealById('SBER-IND-RU-2026-005');
    console.log(deal);
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      <button onClick={handleFetchAll}>Fetch All</button>
      <button onClick={handleSearch}>Search</button>
      <button onClick={handleGetDeal}>Get Deal</button>
    </div>
  );
}
```

### Dashboard Integration

The `DashboardInfographics` component now automatically:
1. Fetches all deals from Qdrant on mount
2. Shows a loading spinner while fetching
3. Displays real Qdrant data in charts and metrics
4. Falls back to mock data if Qdrant is unavailable

## Data Structure

### QdrantDeal Interface
```typescript
interface QdrantDeal {
  deal_id: string;
  sector: string;
  parties: {
    client: string;
    supplier: string;
    specialist: string;
  };
  status: string;
  bottleneck: string;
  action_items: string[];
  communication_history: Array<{
    timestamp: string;
    sender: string;
    type: string;
    content: string;
  }>;
  confidence_score: number;
}
```

## Backend Architecture

### Files Added/Modified

1. **be/load_synthetic_deals.py** (NEW)
   - Loads synthetic data into Qdrant
   - Handles embedding generation
   - Manages upsert operations

2. **be/backend_server.py** (MODIFIED)
   - Added `/api/qdrant/deals` endpoints
   - Auto-initializes Qdrant collections on startup
   - Includes fallback logic if Qdrant unavailable

3. **fe/src/hooks/useQdrantDeals.ts** (NEW)
   - React hook for Qdrant API calls
   - Includes error handling and loading states
   - Type-safe with TypeScript interfaces

4. **fe/src/components/DashboardInfographics.tsx** (MODIFIED)
   - Now fetches from Qdrant
   - Shows loading state
   - Processes Qdrant data into visualizations

## Testing

### Local Testing

1. Start backend:
```bash
cd be
python backend_server.py
```

2. Load synthetic data:
```bash
python load_synthetic_deals.py
```

3. Test endpoints:
```bash
curl http://localhost:8080/api/qdrant/deals?limit=5
curl http://localhost:8080/api/qdrant/deals/search/Pharmaceuticals
```

4. Start frontend:
```bash
cd ../fe
npm run dev
```

5. Navigate to Dashboard tab - should show Qdrant data

## Troubleshooting

### "Qdrant service not available"
- Ensure `QDRANT_URL` and `QDRANT_API_KEY` are set
- Verify Qdrant instance is running
- Check network connectivity

### No deals appear
- Run `load_synthetic_deals.py` to populate Qdrant
- Check Qdrant collection exists: `GET /health`
- Review backend logs for errors

### Dashboard shows mock data
- This is expected fallback behavior
- Check browser console for API errors
- Verify backend is running on port 8080

## Next Steps

- Add more synthetic data files
- Implement real-time sync from backend database
- Add filtering UI for Qdrant searches
- Implement deal pagination
- Add deal creation through Qdrant
