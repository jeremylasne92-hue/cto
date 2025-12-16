import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  callBackend: (endpoint: string, method: string = 'POST', body: unknown = {}, query: Record<string, string> = {}) =>
    ipcRenderer.invoke('backend:call', endpoint, method, body, query),
  
  checkBackendHealth: () =>
    ipcRenderer.invoke('backend:health'),
  
  getAppVersion: () =>
    ipcRenderer.invoke('app:getVersion'),
  
  onUpdateAvailable: (callback: () => void) => {
    ipcRenderer.on('update-available', callback);
  },
  
  onUpdateDownloaded: (callback: () => void) => {
    ipcRenderer.on('update-downloaded', callback);
  },
});
