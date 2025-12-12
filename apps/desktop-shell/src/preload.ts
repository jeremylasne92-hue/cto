import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Dialog handlers
  showSaveDialog: () => ipcRenderer.invoke('show-save-dialog'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // FSRS response handler
  submitFSRSResponse: (responseData: any) => ipcRenderer.invoke('submit-fsrs-response', responseData),
  
  // Platform info
  platform: process.platform,
  
  // Listeners (if needed)
  onBackendMessage: (callback: (data: any) => void) => {
    ipcRenderer.on('backend-message', callback);
  },
  
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: {
      showSaveDialog: () => Promise<Electron.SaveDialogReturnValue>;
      getAppVersion: () => Promise<string>;
      submitFSRSResponse: (responseData: any) => Promise<{ success: boolean }>;
      platform: string;
      onBackendMessage: (callback: (data: any) => void) => void;
      removeAllListeners: (channel: string) => void;
    };
  }
}
