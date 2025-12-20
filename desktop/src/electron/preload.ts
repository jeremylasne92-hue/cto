"""
Preload script for Electron - exposes API to renderer process
"""
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  // Knowledge Graph Operations
  queryKnowledgeGraph: (queryParams: any) => 
    ipcRenderer.invoke('knowledge-graph-query', queryParams),
  
  findRelatedConcepts: (conceptId: number, limit?: number) => 
    ipcRenderer.invoke('knowledge-graph-related', conceptId, limit),
  
  createConcept: (conceptData: any) => 
    ipcRenderer.invoke('create-concept', conceptData),
  
  updateConcept: (conceptId: number, updateData: any) => 
    ipcRenderer.invoke('update-concept', conceptId, updateData),
  
  deleteConcept: (conceptId: number, force?: boolean) => 
    ipcRenderer.invoke('delete-concept', conceptId, force),
  
  getConcept: (conceptId: number) => 
    ipcRenderer.invoke('get-concept', conceptId),
  
  createRelation: (sourceConceptId: number, relationData: any) => 
    ipcRenderer.invoke('create-relation', sourceConceptId, relationData),
  
  searchConcepts: (query: string, limit?: number) => 
    ipcRenderer.invoke('search-concepts', query, limit),
  
  runIntegrityCheck: (conceptIds?: number[]) => 
    ipcRenderer.invoke('integrity-check', conceptIds),
  
  updateMastery: (userId: string, conceptId: number, masteryData: any) => 
    ipcRenderer.invoke('update-mastery', userId, conceptId, masteryData),
  
  getGraphStats: () => 
    ipcRenderer.invoke('get-graph-stats'),
  
  // System Operations
  healthCheck: () => 
    ipcRenderer.invoke('api-health-check'),
  
  callBackend: (method: string, endpoint: string, data?: any, params?: any) => 
    ipcRenderer.invoke('call-backend', method, endpoint, data, params),
  
  getHardwareInfo: () => 
    ipcRenderer.invoke('get-hardware-info')
});

// Type definitions for renderer
declare global {
  interface Window {
    electronAPI: {
      queryKnowledgeGraph: (queryParams: any) => Promise<any>;
      findRelatedConcepts: (conceptId: number, limit?: number) => Promise<any>;
      createConcept: (conceptData: any) => Promise<any>;
      updateConcept: (conceptId: number, updateData: any) => Promise<any>;
      deleteConcept: (conceptId: number, force?: boolean) => Promise<any>;
      getConcept: (conceptId: number) => Promise<any>;
      createRelation: (sourceConceptId: number, relationData: any) => Promise<any>;
      searchConcepts: (query: string, limit?: number) => Promise<any>;
      runIntegrityCheck: (conceptIds?: number[]) => Promise<any>;
      updateMastery: (userId: string, conceptId: number, masteryData: any) => Promise<any>;
      getGraphStats: () => Promise<any>;
      healthCheck: () => Promise<any>;
      callBackend: (method: string, endpoint: string, data?: any, params?: any) => Promise<any>;
      getHardwareInfo: () => Promise<any>;
    };
  }
}