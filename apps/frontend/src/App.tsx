import React, { useEffect, useState } from 'react';

function App() {
  const [status, setStatus] = useState('Checking backend connection...');
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Check if running in Electron
    if (window.electronAPI) {
      window.electronAPI.onToken((_event: any, receivedToken: string) => {
          setToken(receivedToken);
          setStatus('Token received from Electron');
      });
      
      // Request status
      window.electronAPI.checkBackendStatus().then((result: string) => {
        setStatus(prev => `${prev}\nBackend Status: ${result}`);
      });
    } else {
      setStatus('Not running in Electron');
    }
  }, []);

  return (
    <div className="container">
      <h1>Cognisphere Desktop</h1>
      <div className="card">
        <p>Status: {status}</p>
        <p>Auth Token: {token ? 'Received' : 'Waiting...'}</p>
      </div>
    </div>
  );
}

export default App;
