import { useState, useEffect, useCallback } from 'react';

interface Node {
  id: string;
  name: string;
  description: string;
  mastery: number;
  review_count: number;
  color: string;
  x?: number;
  y?: number;
  z?: number;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  type: string;
  strength: number;
  is_prerequisite?: boolean;
  is_dependency?: boolean;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
  metadata?: any;
  rendering?: {
    use_webgl: boolean;
    mode: string;
  };
}

interface UseKnowledgeGraphOptions {
  userId?: number;
  depth?: number;
  searchTerm?: string;
  autoRefresh?: boolean;
}

export function useKnowledgeGraph(options: UseKnowledgeGraphOptions = {}) {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useWebGL, setUseWebGL] = useState(true);
  
  const fetchGraphData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Check hardware capabilities
      const hwInfo = await window.electronAPI.getHardwareInfo();
      const shouldUseWebGL = hwInfo.hasGPU && useWebGL;
      
      const response = await window.electronAPI.callBackend({
        method: 'POST',
        endpoint: '/api/knowledge-graph/query',
        body: {
          user_id: options.userId,
          depth: options.depth,
          search_term: options.searchTerm,
          use_webgl: shouldUseWebGL,
        },
      });
      
      if (response.success) {
        setGraphData(response.data);
      } else {
        setError(response.error || 'Failed to fetch graph data');
      }
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [options.userId, options.depth, options.searchTerm, useWebGL]);
  
  const getRelatedConcepts = useCallback(async (conceptId: string, maxDepth: number = 2) => {
    try {
      const response = await window.electronAPI.callBackend({
        method: 'POST',
        endpoint: '/api/knowledge-graph/related',
        body: {
          concept_id: conceptId,
          max_depth: maxDepth,
        },
      });
      
      if (response.success) {
        return response.data;
      } else {
        throw new Error(response.error || 'Failed to fetch related concepts');
      }
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, []);
  
  const createConcept = useCallback(async (name: string, description?: string, metadata?: any) => {
    try {
      const response = await window.electronAPI.callBackend({
        method: 'POST',
        endpoint: '/api/concepts',
        body: { name, description, metadata },
      });
      
      if (response.success) {
        await fetchGraphData();
        return response.data;
      } else {
        throw new Error(response.error || 'Failed to create concept');
      }
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, [fetchGraphData]);
  
  const updateConcept = useCallback(async (
    conceptId: string,
    name?: string,
    description?: string,
    metadata?: any
  ) => {
    try {
      const response = await window.electronAPI.callBackend({
        method: 'PUT',
        endpoint: `/api/concepts/${conceptId}`,
        body: { name, description, metadata },
      });
      
      if (response.success) {
        await fetchGraphData();
        return response.data;
      } else {
        throw new Error(response.error || 'Failed to update concept');
      }
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, [fetchGraphData]);
  
  const deleteConcept = useCallback(async (conceptId: string) => {
    try {
      const response = await window.electronAPI.callBackend({
        method: 'DELETE',
        endpoint: `/api/concepts/${conceptId}`,
      });
      
      if (response.success) {
        await fetchGraphData();
        return true;
      } else {
        throw new Error(response.error || 'Failed to delete concept');
      }
    } catch (err: any) {
      setError(err.message);
      return false;
    }
  }, [fetchGraphData]);
  
  const createRelation = useCallback(async (
    sourceId: string,
    targetId: string,
    relationType: string,
    strength: number = 1.0
  ) => {
    try {
      const response = await window.electronAPI.callBackend({
        method: 'POST',
        endpoint: '/api/relations',
        body: {
          source_id: sourceId,
          target_id: targetId,
          relation_type: relationType,
          strength,
        },
      });
      
      if (response.success) {
        await fetchGraphData();
        return response.data;
      } else {
        throw new Error(response.error || 'Failed to create relation');
      }
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, [fetchGraphData]);
  
  const saveLayoutPositions = useCallback(async (positions: Record<string, any>) => {
    try {
      await window.electronAPI.saveGraphLayout(positions);
    } catch (err: any) {
      console.error('Failed to save layout:', err);
    }
  }, []);
  
  const runIntegrityCheck = useCallback(async () => {
    try {
      const response = await window.electronAPI.callBackend({
        method: 'POST',
        endpoint: '/api/knowledge-graph/integrity-check',
      });
      
      if (response.success) {
        return response.data;
      } else {
        throw new Error(response.error || 'Integrity check failed');
      }
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, []);
  
  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);
  
  useEffect(() => {
    if (options.autoRefresh) {
      const interval = setInterval(fetchGraphData, 30000);
      return () => clearInterval(interval);
    }
  }, [options.autoRefresh, fetchGraphData]);
  
  return {
    graphData,
    loading,
    error,
    useWebGL,
    setUseWebGL,
    refetch: fetchGraphData,
    getRelatedConcepts,
    createConcept,
    updateConcept,
    deleteConcept,
    createRelation,
    saveLayoutPositions,
    runIntegrityCheck,
  };
}
