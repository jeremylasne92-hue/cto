"""
Electron IPC Handlers for Knowledge Graph operations
Handles communication between main process and renderer
"""
import { ipcMain } from 'electron';
import axios from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000';

export function setupKnowledgeGraphIpcHandlers() {
  // Knowledge Graph Query
  ipcMain.handle('knowledge-graph-query', async (event, queryParams) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/query`, queryParams);
      return response.data;
    } catch (error) {
      console.error('Knowledge graph query failed:', error);
      throw error;
    }
  });

  // Find Related Concepts
  ipcMain.handle('knowledge-graph-related', async (event, conceptId, limit = 10) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/related`, {
        concept_id: conceptId,
        limit
      });
      return response.data;
    } catch (error) {
      console.error('Find related concepts failed:', error);
      throw error;
    }
  });

  // Create Concept
  ipcMain.handle('create-concept', async (event, conceptData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/concepts`, conceptData);
      return response.data;
    } catch (error) {
      console.error('Create concept failed:', error);
      throw error;
    }
  });

  // Update Concept
  ipcMain.handle('update-concept', async (event, conceptId, updateData) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/concepts/${conceptId}`, updateData);
      return response.data;
    } catch (error) {
      console.error('Update concept failed:', error);
      throw error;
    }
  });

  // Delete Concept
  ipcMain.handle('delete-concept', async (event, conceptId, force = false) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/concepts/${conceptId}`, {
        params: { force: force.toString() }
      });
      return response.data;
    } catch (error) {
      console.error('Delete concept failed:', error);
      throw error;
    }
  });

  // Get Concept Details
  ipcMain.handle('get-concept', async (event, conceptId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/concepts/${conceptId}`);
      return response.data;
    } catch (error) {
      console.error('Get concept failed:', error);
      throw error;
    }
  });

  // Create Relation
  ipcMain.handle('create-relation', async (event, sourceConceptId, relationData) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/concepts/${sourceConceptId}/relations`,
        relationData
      );
      return response.data;
    } catch (error) {
      console.error('Create relation failed:', error);
      throw error;
    }
  });

  // Search Concepts
  ipcMain.handle('search-concepts', async (event, query, limit = 10) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/search`, {
        query,
        limit
      });
      return response.data;
    } catch (error) {
      console.error('Search concepts failed:', error);
      throw error;
    }
  });

  // Integrity Check
  ipcMain.handle('integrity-check', async (event, conceptIds = null) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/integrity-check`, {
        concept_ids: conceptIds
      });
      return response.data;
    } catch (error) {
      console.error('Integrity check failed:', error);
      throw error;
    }
  });

  // Update Mastery
  ipcMain.handle('update-mastery', async (event, userId, conceptId, masteryData) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/mastery/${userId}/${conceptId}`,
        masteryData
      );
      return response.data;
    } catch (error) {
      console.error('Update mastery failed:', error);
      throw error;
    }
  });

  // Get Graph Stats
  ipcMain.handle('get-graph-stats', async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/stats`);
      return response.data;
    } catch (error) {
      console.error('Get graph stats failed:', error);
      throw error;
    }
  });

  // Health Check
  ipcMain.handle('api-health-check', async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('API health check failed:', error);
      throw error;
    }
  });
}

export function setupBackendApiHandlers() {
  // Generic backend API call handler
  ipcMain.handle('call-backend', async (event, method, endpoint, data = null, params = null) => {
    try {
      const config = {
        method: method.toLowerCase(),
        url: `${API_BASE_URL}${endpoint}`,
        params: params || {}
      };

      if (data && ['post', 'put', 'patch'].includes(config.method)) {
        config.data = data;
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      console.error(`Backend API call failed: ${method} ${endpoint}`, error);
      throw error;
    }
  });
}

export function setupHardwareInfoHandler() {
  // Get hardware capabilities for WebGL vs Canvas fallback
  ipcMain.handle('get-hardware-info', async () => {
    try {
      // This would ideally use system APIs to detect GPU capabilities
      // For now, we'll use a simple heuristic based on platform
      const platform = process.platform;
      const isMac = platform === 'darwin';
      const isWindows = platform === 'win32';
      const isLinux = platform === 'linux';

      return {
        platform,
        supportsWebGL: true, // Most modern systems support WebGL
        gpuInfo: 'Unknown', // Would implement actual GPU detection
        recommendedRenderer: 'webgl' // Could be 'canvas' based on actual detection
      };
    } catch (error) {
      console.error('Get hardware info failed:', error);
      return {
        platform: 'unknown',
        supportsWebGL: false,
        gpuInfo: 'Unknown',
        recommendedRenderer: 'canvas'
      };
    }
  });
}