import React, { useEffect, useState } from 'react';
import { IngestionJob } from '../types/types';
import { listJobs, getJobStatus, cancelJob } from '../services/api';

interface JobsListProps {
  refreshTrigger: number;
}

const JobsList: React.FC<JobsListProps> = ({ refreshTrigger }) => {
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 2000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  const fetchJobs = async () => {
    try {
      const data = await listJobs();
      setJobs(data.reverse());
      setLoading(false);
    } catch (err) {
      console.error('Error fetching jobs:', err);
    }
  };

  const handleCancel = async (jobId: number) => {
    try {
      await cancelJob(jobId);
      fetchJobs();
    } catch (err) {
      console.error('Error cancelling job:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#28a745';
      case 'failed':
        return '#dc3545';
      case 'cancelled':
        return '#6c757d';
      default:
        return '#007bff';
    }
  };

  if (loading) {
    return <div>Loading jobs...</div>;
  }

  return (
    <div style={styles.container}>
      <h2>Ingestion Jobs</h2>
      {jobs.length === 0 ? (
        <p>No jobs yet</p>
      ) : (
        <div style={styles.jobsList}>
          {jobs.map((job) => (
            <div key={job.id} style={styles.jobCard}>
              <div style={styles.jobHeader}>
                <span style={styles.jobId}>Job #{job.id}</span>
                <span
                  style={{
                    ...styles.status,
                    backgroundColor: getStatusColor(job.status),
                  }}
                >
                  {job.status}
                </span>
              </div>
              
              <div style={styles.progressContainer}>
                <div
                  style={{
                    ...styles.progressBar,
                    width: `${job.progress * 100}%`,
                  }}
                />
              </div>
              
              <div style={styles.progressText}>
                {(job.progress * 100).toFixed(0)}% complete
              </div>
              
              {job.error_message && (
                <div style={styles.error}>{job.error_message}</div>
              )}
              
              {job.status !== 'completed' && job.status !== 'failed' && job.status !== 'cancelled' && (
                <button
                  onClick={() => handleCancel(job.id)}
                  style={styles.cancelButton}
                >
                  Cancel
                </button>
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
  },
  jobsList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '15px',
  },
  jobCard: {
    backgroundColor: '#fff',
    padding: '15px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  jobHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
  },
  jobId: {
    fontWeight: 'bold' as const,
    fontSize: '16px',
  },
  status: {
    padding: '4px 12px',
    borderRadius: '12px',
    color: '#fff',
    fontSize: '12px',
    fontWeight: 'bold' as const,
  },
  progressContainer: {
    width: '100%',
    height: '20px',
    backgroundColor: '#e0e0e0',
    borderRadius: '10px',
    overflow: 'hidden',
    marginBottom: '5px',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#007bff',
    transition: 'width 0.3s ease',
  },
  progressText: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '10px',
  },
  error: {
    color: '#dc3545',
    fontSize: '14px',
    marginTop: '10px',
  },
  cancelButton: {
    padding: '8px 16px',
    backgroundColor: '#dc3545',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginTop: '10px',
  },
};

export default JobsList;
