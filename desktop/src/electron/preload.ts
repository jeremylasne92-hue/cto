import { contextBridge, ipcRenderer } from 'electron';

interface BackendCallOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  endpoint: string;
  body?: any;
  params?: Record<string, any>;
}

interface BackendResponse {
  success: boolean;
  data?: any;
  error?: string;
  status: number;
}

contextBridge.exposeInMainWorld('electronAPI', {
  callBackend: async (options: BackendCallOptions): Promise<BackendResponse> => {
    return await ipcRenderer.invoke('call-backend', options);
  },
  
  getHardwareInfo: async () => {
    return await ipcRenderer.invoke('get-hardware-info');
  },
  
  saveGraphLayout: async (positions: Record<string, any>) => {
    return await ipcRenderer.invoke('save-graph-layout', positions);
  },
});

export {};
