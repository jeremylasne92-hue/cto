import React, { useEffect, useState } from 'react';

interface ElectronAPI {
  callBackend: (method: string, params: unknown) => Promise<unknown>;
  checkBackendHealth: () => Promise<{ status: string }>;
  getAppVersion: () => Promise<string>;
  onUpdateAvailable: (callback: () => void) => void;
  onUpdateDownloaded: (callback: () => void) => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

const App: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<string>('checking');
  const [appVersion, setAppVersion] = useState<string>('');

  useEffect(() => {
    checkBackend();
    loadVersion();

    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkBackend = async () => {
    try {
      const health = await window.electronAPI.checkBackendHealth();
      setBackendStatus(health.status);
    } catch (error) {
      console.error('Failed to check backend health:', error);
      setBackendStatus('error');
    }
  };

  const loadVersion = async () => {
    try {
      const version = await window.electronAPI.getAppVersion();
      setAppVersion(version);
    } catch (error) {
      console.error('Failed to load version:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Cognisphere</h1>
        <p className="version">v{appVersion}</p>
      </header>
      <main className="app-main">
        <div className="status-card">
          <h2>System Status</h2>
          <div className="status-item">
            <span>Backend:</span>
            <span className={`status-badge status-${backendStatus}`}>
              {backendStatus}
            </span>
          </div>
        </div>
        <div className="welcome-card">
          <h2>Welcome to Cognisphere</h2>
          <p>Your intelligent learning companion with spaced repetition.</p>
          <p className="subtitle">
            Desktop app is running successfully. Backend integration is ready.
          </p>
        </div>
      </main>
    </div>
  );
};

export default App;
