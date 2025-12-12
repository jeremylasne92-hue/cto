/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

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
