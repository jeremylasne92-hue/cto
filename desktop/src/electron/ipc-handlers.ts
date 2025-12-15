import { ipcMain } from 'electron';
import axios, { AxiosRequestConfig } from 'axios';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:5000';

interface BackendCallOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  endpoint: string;
  body?: any;
  params?: Record<string, any>;
}

export function setupIpcHandlers() {
  ipcMain.handle('call-backend', async (event, options: BackendCallOptions) => {
    try {
      const { method = 'GET', endpoint, body, params } = options;
      
      const config: AxiosRequestConfig = {
        method,
        url: `${BACKEND_URL}${endpoint}`,
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      if (body) {
        config.data = body;
      }
      
      if (params) {
        config.params = params;
      }
      
      const response = await axios(config);
      return {
        success: true,
        data: response.data,
        status: response.status,
      };
    } catch (error: any) {
      console.error('Backend call failed:', error);
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 500,
        data: error.response?.data,
      };
    }
  });
  
  ipcMain.handle('get-hardware-info', async () => {
    try {
      const { app } = require('electron');
      const gpuInfo = app.getGPUInfo('complete');
      
      return {
        hasGPU: true,
        gpuInfo: await gpuInfo,
      };
    } catch (error) {
      console.error('Failed to get GPU info:', error);
      return {
        hasGPU: false,
        gpuInfo: null,
      };
    }
  });
  
  ipcMain.handle('save-graph-layout', async (event, positions: Record<string, any>) => {
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/knowledge-graph/layout`,
        { positions },
        { headers: { 'Content-Type': 'application/json' } }
      );
      
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      console.error('Failed to save layout:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  });
  
  console.log('IPC handlers registered');
}
