import React, { useEffect, useState } from 'react';
import { ContentSource } from '../types/types';
import { listSources, deleteSource } from '../services/api';

const SourcesList: React.FC = () => {
  const [sources, setSources] = useState<ContentSource[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const data = await listSources();
      setSources(data.reverse());
      setLoading(false);
    } catch (err) {
      console.error('Error fetching sources:', err);
    }
  };

  const handleDelete = async (sourceId: number) => {
    if (window.confirm('Are you sure you want to delete this source?')) {
      try {
        await deleteSource(sourceId);
        fetchSources();
      } catch (err) {
        console.error('Error deleting source:', err);
      }
    }
  };

  if (loading) {
    return <div>Loading sources...</div>;
  }

  return (
    <div style={styles.container}>
      <h2>Content Sources</h2>
      {sources.length === 0 ? (
        <p>No sources ingested yet</p>
      ) : (
        <div style={styles.sourcesList}>
          {sources.map((source) => (
            <div key={source.id} style={styles.sourceCard}>
              <div style={styles.sourceHeader}>
                <div>
                  <h3 style={styles.title}>{source.title || 'Untitled'}</h3>
                  <p style={styles.author}>{source.author || 'Unknown author'}</p>
                </div>
                <span style={styles.type}>{source.source_type}</span>
              </div>
              
              <div style={styles.meta}>
                <span>ID: {source.id}</span>
                <span>Created: {new Date(source.created_at).toLocaleDateString()}</span>
              </div>
              
              <div style={styles.hash}>Hash: {source.hash.substring(0, 16)}...</div>
              
              <button
                onClick={() => handleDelete(source.id)}
                style={styles.deleteButton}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
  },
  sourcesList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '15px',
  },
  sourceCard: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  sourceHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '10px',
  },
  title: {
    margin: '0 0 5px 0',
    fontSize: '18px',
    fontWeight: 'bold' as const,
  },
  author: {
    margin: 0,
    fontSize: '14px',
    color: '#666',
  },
  type: {
    padding: '4px 12px',
    backgroundColor: '#007bff',
    color: '#fff',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 'bold' as const,
  },
  meta: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
    color: '#999',
    marginBottom: '10px',
  },
  hash: {
    fontSize: '12px',
    color: '#999',
    marginBottom: '10px',
    fontFamily: 'monospace',
  },
  deleteButton: {
    padding: '8px 16px',
    backgroundColor: '#dc3545',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    width: '100%',
  },
};

export default SourcesList;
