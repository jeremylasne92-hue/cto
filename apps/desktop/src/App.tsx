import { useEffect } from 'react';
import { Shell } from './components/layout/Shell';
import Dashboard from './pages/Dashboard';
import { useAppStore } from './store/useAppStore';

function App() {
  const setToken = useAppStore(state => state.setToken);

  useEffect(() => {
    // Listen for Auth Token from Electron
    if (window.electronAPI) {
      window.electronAPI.onToken((_event: any, receivedToken: string) => {
        setToken(receivedToken);
        console.log('🔒 Token Secured');
      });
    }
  }, [setToken]);

  return (
    <Shell>
      <Dashboard />
    </Shell>
  );
}

export default App;
