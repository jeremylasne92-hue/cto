import React, { useState } from 'react';
import IngestionForm from './components/IngestionForm';
import JobsList from './components/JobsList';
import SourcesList from './components/SourcesList';
import SearchInterface from './components/SearchInterface';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState<'ingest' | 'sources' | 'search'>('ingest');

  const handleIngestionStarted = (jobId: number) => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1>Universal Content Ingestion Pipeline</h1>
      </header>
      
      <div style={styles.tabs}>
        <button
          style={activeTab === 'ingest' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('ingest')}
        >
          Ingest Content
        </button>
        <button
          style={activeTab === 'sources' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('sources')}
        >
          Sources
        </button>
        <button
          style={activeTab === 'search' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('search')}
        >
          Search
        </button>
      </div>

      <div style={styles.container}>
        {activeTab === 'ingest' && (
          <>
            <IngestionForm onIngestionStarted={handleIngestionStarted} />
            <JobsList refreshTrigger={refreshTrigger} />
          </>
        )}
        
        {activeTab === 'sources' && <SourcesList />}
        
        {activeTab === 'search' && <SearchInterface />}
      </div>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#e9ecef',
  },
  header: {
    backgroundColor: '#343a40',
    color: '#fff',
    padding: '20px',
    textAlign: 'center' as const,
  },
  tabs: {
    display: 'flex',
    backgroundColor: '#fff',
    borderBottom: '1px solid #dee2e6',
    padding: '0 20px',
  },
  tab: {
    padding: '15px 30px',
    border: 'none',
    backgroundColor: 'transparent',
    cursor: 'pointer',
    fontSize: '16px',
    borderBottom: '3px solid transparent',
  },
  activeTab: {
    padding: '15px 30px',
    border: 'none',
    backgroundColor: 'transparent',
    cursor: 'pointer',
    fontSize: '16px',
    borderBottom: '3px solid #007bff',
    color: '#007bff',
    fontWeight: 'bold' as const,
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
  },
};

export default App;
