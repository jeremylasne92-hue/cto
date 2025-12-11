import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  callBackend: (method: string, params: unknown) =>
    ipcRenderer.invoke('backend:call', method, params),
  
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
