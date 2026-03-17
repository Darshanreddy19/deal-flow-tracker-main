import { useState, useCallback } from 'react';

const BACKEND_URL = 'http://localhost:8080';

export interface QdrantDeal {
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

export const useQdrantDeals = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAllDeals = useCallback(async (limit = 10): Promise<QdrantDeal[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/qdrant/deals?limit=${limit}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data.data || [];
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch deals';
      setError(message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const searchDeals = useCallback(async (query: string, limit = 5): Promise<QdrantDeal[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/qdrant/deals/search/${encodeURIComponent(query)}?limit=${limit}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data.data || [];
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to search deals';
      setError(message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDealById = useCallback(async (dealId: string): Promise<QdrantDeal | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/qdrant/deals/${dealId}`);
      if (!response.ok) {
        if (response.status === 404) {
          setError(`Deal ${dealId} not found`);
          return null;
        }
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data.data || null;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch deal';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    fetchAllDeals,
    searchDeals,
    fetchDealById,
    loading,
    error,
  };
};

export default useQdrantDeals;
