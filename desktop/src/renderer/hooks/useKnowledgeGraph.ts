import { useState, useEffect, useCallback } from 'react';

interface GraphData {
  nodes: any[];
  links: any[];
}

export const useKnowledgeGraph = () => {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGraph = useCallback(async (filterDepth = 1, searchTerm = '') => {
    setLoading(true);
    setError(null);
    try {
      const result = await window.electronAPI.callBackend(
        'knowledge-graph/query',
        'POST',
        { filter_depth: filterDepth, search_term: searchTerm }
      ) as GraphData;
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch graph');
    } finally {
      setLoading(false);
    }
  }, []);

  const runIntegrityCheck = async () => {
      return await window.electronAPI.callBackend('knowledge-graph/integrity-check', 'POST');
  };

  return { data, loading, error, fetchGraph, runIntegrityCheck };
};
