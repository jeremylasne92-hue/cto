import React, { useState } from 'react';
import { ingestUrl, ingestFile, ingestText } from '../services/api';

interface IngestionFormProps {
  onIngestionStarted: (jobId: number) => void;
}

const IngestionForm: React.FC<IngestionFormProps> = ({ onIngestionStarted }) => {
  const [inputType, setInputType] = useState<'url' | 'file' | 'text'>('url');
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let result;
      if (inputType === 'url') {
        result = await ingestUrl(urlInput);
      } else if (inputType === 'file' && file) {
        result = await ingestFile(file);
      } else if (inputType === 'text') {
        result = await ingestText(textInput);
      }

      if (result) {
        onIngestionStarted(result.job_id);
        setUrlInput('');
        setTextInput('');
        setFile(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Ingest Content</h2>
      
      <div style={styles.typeSelector}>
        <button
          style={inputType === 'url' ? styles.activeButton : styles.button}
          onClick={() => setInputType('url')}
        >
          URL
        </button>
        <button
          style={inputType === 'file' ? styles.activeButton : styles.button}
          onClick={() => setInputType('file')}
        >
          File
        </button>
        <button
          style={inputType === 'text' ? styles.activeButton : styles.button}
          onClick={() => setInputType('text')}
        >
          Text
        </button>
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        {inputType === 'url' && (
          <input
            type="text"
            placeholder="Enter URL (YouTube, web page, etc.)"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            style={styles.input}
            required
          />
        )}

        {inputType === 'file' && (
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            style={styles.input}
            required
          />
        )}

        {inputType === 'text' && (
          <textarea
            placeholder="Paste your text here..."
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            style={styles.textarea}
            required
          />
        )}

        {error && <div style={styles.error}>{error}</div>}

        <button type="submit" disabled={loading} style={styles.submitButton}>
          {loading ? 'Processing...' : 'Ingest'}
        </button>
      </form>
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
  typeSelector: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
  },
  button: {
    padding: '10px 20px',
    border: '1px solid #ccc',
    backgroundColor: '#fff',
    cursor: 'pointer',
    borderRadius: '4px',
  },
  activeButton: {
    padding: '10px 20px',
    border: '1px solid #007bff',
    backgroundColor: '#007bff',
    color: '#fff',
    cursor: 'pointer',
    borderRadius: '4px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '10px',
  },
  input: {
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
  },
  textarea: {
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
    minHeight: '100px',
    resize: 'vertical' as const,
  },
  submitButton: {
    padding: '12px',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  error: {
    color: 'red',
    fontSize: '14px',
  },
};

export default IngestionForm;
