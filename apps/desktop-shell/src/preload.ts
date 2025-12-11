import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
    checkBackendStatus: () => ipcRenderer.invoke('check-backend-status'),
    onToken: (callback: (event: any, token: string) => void) => ipcRenderer.on('auth-token', callback)
});
