"""
React hook for Knowledge Graph operations
Provides state management and API communication for graph data
"""
import { useState, useEffect, useCallback } from 'react';

export interface GraphNode {
  id: number;
  name: string;
  description: string;
  content: string;
  parent_id?: number;
  created_at: string;
  updated_at: string;
  mastery: number;
  review_count: number;
  last_assessed?: string;
  color: 'green' | 'yellow' | 'orange' | 'gray';
  prerequisites?: number[];
  dependencies?: number[];
}

export interface GraphLink {
  source: number;
  target: number;
  type: string;
  strength: number;
  created_at: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
  stats: {
    total_concepts: number;
    total_relations: number;
    mastery_distribution: Record<string, number>;
  };
}

export interface ConceptData {
  id: number;
  name: string;
  description: string;
  content: string;
  parent_id?: number;
}

export interface RelationData {
  target_concept_id: number;
  relation_type: string;
  strength: number;
}

export interface SearchResult {
  concept_id: number;
  name: string;
  description: string;
  content?: string;
  match_type: string;
  score: number;
}

export interface IntegrityCheckResult {
  status: 'healthy' | 'issues_found';
  total_issues: number;
  issues: {
    orphans: any[];
    cycles: any[];
    broken_references: any[];
    duplicate_ids: any[];
    strength_anomalies: any[];
  };
  checked_at: string;
}

export interface HardwareInfo {
  platform: string;
  supportsWebGL: boolean;
  gpuInfo: string;
  recommendedRenderer: 'webgl' | 'canvas';
}

interface UseKnowledgeGraphReturn {
  // State
  graphData: GraphData | null;
  selectedNode: GraphNode | null;
  isLoading: boolean;
  error: string | null;
  stats: any;
  hardwareInfo: HardwareInfo | null;
  
  // Actions
  loadGraph: (params?: any) => Promise<void>;
  searchConcepts: (query: string) => Promise<SearchResult[]>;
  createConcept: (conceptData: ConceptData) => Promise<GraphNode>;
  updateConcept: (id: number, data: Partial<ConceptData>) => Promise<GraphNode>;
  deleteConcept: (id: number, force?: boolean) => Promise<boolean>;
  createRelation: (sourceId: number, relationData: RelationData) => Promise<any>;
  findRelated: (conceptId: number, limit?: number) => Promise<SearchResult[]>;
  runIntegrityCheck: () => Promise<IntegrityCheckResult>;
  updateMastery: (userId: string, conceptId: number, masteryData: any) => Promise<any>;
  setSelectedNode: (node: GraphNode | null) => void;
  clearError: () => void;
}

export function useKnowledgeGraph(userId: string = 'default'): UseKnowledgeGraphReturn {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [hardwareInfo, setHardwareInfo] = useState<HardwareInfo | null>(null);

  const loadGraph = useCallback(async (params: any = {}) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await window.electronAPI.queryKnowledgeGraph({
        depth: params.depth || 2,
        search_term: params.searchTerm || '',
        concept_ids: params.conceptIds || null,
        user_id: userId,
        use_webgl: params.useWebgl || false
      });
      
      if (result.success) {
        setGraphData(result.data);
      } else {
        throw new Error(result.error || 'Failed to load graph data');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('Failed to load graph:', err);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const searchConcepts = useCallback(async (query: string): Promise<SearchResult[]> => {
    try {
      const result = await window.electronAPI.searchConcepts(query, 20);
      
      if (result.success) {
        return result.data.results;
      } else {
        throw new Error(result.error || 'Search failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Search failed';
      setError(errorMessage);
      return [];
    }
  }, []);

  const createConcept = useCallback(async (conceptData: ConceptData): Promise<GraphNode> => {
    try {
      const result = await window.electronAPI.createConcept(conceptData);
      
      if (result.success) {
        // Reload graph to include new concept
        await loadGraph();
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to create concept');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create concept';
      setError(errorMessage);
      throw err;
    }
  }, [loadGraph]);

  const updateConcept = useCallback(async (id: number, data: Partial<ConceptData>): Promise<GraphNode> => {
    try {
      const result = await window.electronAPI.updateConcept(id, data);
      
      if (result.success) {
        // Update local graph data
        setGraphData(prev => {
          if (!prev) return prev;
          
          const updatedNodes = prev.nodes.map(node =>
            node.id === id ? { ...node, ...result.data } : node
          );
          
          return { ...prev, nodes: updatedNodes };
        });
        
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to update concept');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update concept';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const deleteConcept = useCallback(async (id: number, force: boolean = false): Promise<boolean> => {
    try {
      const result = await window.electronAPI.deleteConcept(id, force);
      
      if (result.success) {
        // Reload graph to reflect changes
        await loadGraph();
        
        // Clear selection if deleted node was selected
        if (selectedNode?.id === id) {
          setSelectedNode(null);
        }
        
        return true;
      } else {
        throw new Error(result.error || 'Failed to delete concept');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete concept';
      setError(errorMessage);
      throw err;
    }
  }, [loadGraph, selectedNode]);

  const createRelation = useCallback(async (sourceId: number, relationData: RelationData) => {
    try {
      const result = await window.electronAPI.createRelation(sourceId, relationData);
      
      if (result.success) {
        // Reload graph to include new relation
        await loadGraph();
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to create relation');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create relation';
      setError(errorMessage);
      throw err;
    }
  }, [loadGraph]);

  const findRelated = useCallback(async (conceptId: number, limit: number = 10): Promise<SearchResult[]> => {
    try {
      const result = await window.electronAPI.findRelatedConcepts(conceptId, limit);
      
      if (result.success) {
        return result.data.neighbors;
      } else {
        throw new Error(result.error || 'Failed to find related concepts');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to find related concepts';
      setError(errorMessage);
      return [];
    }
  }, []);

  const runIntegrityCheck = useCallback(async (): Promise<IntegrityCheckResult> => {
    try {
      const result = await window.electronAPI.runIntegrityCheck();
      
      if (result.success) {
        return result.data;
      } else {
        throw new Error(result.error || 'Integrity check failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Integrity check failed';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const updateMastery = useCallback(async (userId: string, conceptId: number, masteryData: any) => {
    try {
      const result = await window.electronAPI.updateMastery(userId, conceptId, masteryData);
      
      if (result.success) {
        // Update local graph data to reflect mastery changes
        setGraphData(prev => {
          if (!prev) return prev;
          
          const updatedNodes = prev.nodes.map(node => {
            if (node.id === conceptId) {
              const mastery_percentage = masteryData.mastery_percentage || 0;
              let color: 'green' | 'yellow' | 'orange' | 'gray' = 'gray';
              
              if (mastery_percentage >= 80) color = 'green';
              else if (mastery_percentage >= 50) color = 'yellow';
              else if (mastery_percentage >= 20) color = 'orange';
              
              return { 
                ...node, 
                mastery: mastery_percentage,
                color 
              };
            }
            return node;
          });
          
          return { ...prev, nodes: updatedNodes };
        });
        
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to update mastery');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update mastery';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const result = await window.electronAPI.getGraphStats();
      
      if (result.success) {
        setStats(result.data);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  }, []);

  const loadHardwareInfo = useCallback(async () => {
    try {
      const result = await window.electronAPI.getHardwareInfo();
      setHardwareInfo(result);
    } catch (err) {
      console.error('Failed to load hardware info:', err);
      setHardwareInfo({
        platform: 'unknown',
        supportsWebGL: false,
        gpuInfo: 'Unknown',
        recommendedRenderer: 'canvas'
      });
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load initial data
  useEffect(() => {
    loadGraph();
    loadStats();
    loadHardwareInfo();
  }, [loadGraph, loadStats, loadHardwareInfo]);

  return {
    // State
    graphData,
    selectedNode,
    isLoading,
    error,
    stats,
    hardwareInfo,
    
    // Actions
    loadGraph,
    searchConcepts,
    createConcept,
    updateConcept,
    deleteConcept,
    createRelation,
    findRelated,
    runIntegrityCheck,
    updateMastery,
    setSelectedNode,
    clearError
  };
}