import React, { useState } from 'react';
import { search } from '../services/api';
import { SearchResult } from '../types/types';

const SearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await search(query, 10);
      setResults(data);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Semantic Search</h2>
      
      <form onSubmit={handleSearch} style={styles.form}>
        <input
          type="text"
          placeholder="Search your content..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={styles.input}
        />
        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {results.length > 0 && (
        <div style={styles.results}>
          <h3>Results ({results.length})</h3>
          {results.map((result, index) => (
            <div key={index} style={styles.resultCard}>
              <div style={styles.resultHeader}>
                <span style={styles.chunkType}>{result.chunk_type}</span>
                <span style={styles.sourceId}>Source #{result.source_id}</span>
              </div>
              <div style={styles.resultText}>
                {result.text.length > 300
                  ? result.text.substring(0, 300) + '...'
                  : result.text}
              </div>
              {result._distance !== undefined && (
                <div style={styles.distance}>
                  Distance: {result._distance.toFixed(4)}
                </div>
              )}
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
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  form: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
  },
  input: {
    flex: 1,
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
  },
  button: {
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  results: {
    marginTop: '20px',
  },
  resultCard: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '10px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  resultHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '10px',
  },
  chunkType: {
    padding: '4px 8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    fontSize: '12px',
  },
  sourceId: {
    fontSize: '12px',
    color: '#666',
  },
  resultText: {
    fontSize: '14px',
    lineHeight: '1.6',
    color: '#333',
  },
  distance: {
    fontSize: '12px',
    color: '#999',
    marginTop: '10px',
  },
};

export default SearchInterface;
