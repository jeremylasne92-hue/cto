/* Global type definitions for Window */
interface Window {
  electronAPI?: {
    checkBackendStatus: () => Promise<string>;
    onToken: (callback: (event: any, token: string) => void) => void;
  };
}
