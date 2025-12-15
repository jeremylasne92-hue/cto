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

interface HardwareInfo {
  hasGPU: boolean;
  gpuInfo: any;
}

interface ElectronAPI {
  callBackend: (options: BackendCallOptions) => Promise<BackendResponse>;
  getHardwareInfo: () => Promise<HardwareInfo>;
  saveGraphLayout: (positions: Record<string, any>) => Promise<{ success: boolean; error?: string }>;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

export {};
