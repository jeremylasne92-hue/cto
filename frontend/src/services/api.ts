import axios from 'axios';
import { IngestionJob, ContentSource, SearchResult } from '../types/types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const ingestUrl = async (url: string): Promise<{ job_id: number }> => {
  const response = await api.post('/ingest/url', { source: url });
  return response.data;
};

export const ingestFile = async (file: File): Promise<{ job_id: number }> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/ingest/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const ingestText = async (text: string): Promise<{ job_id: number }> => {
  const response = await api.post('/ingest/text', { source: text });
  return response.data;
};

export const getJobStatus = async (jobId: number): Promise<IngestionJob> => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

export const listJobs = async (): Promise<IngestionJob[]> => {
  const response = await api.get('/jobs');
  return response.data;
};

export const cancelJob = async (jobId: number): Promise<void> => {
  await api.delete(`/jobs/${jobId}`);
};

export const listSources = async (): Promise<ContentSource[]> => {
  const response = await api.get('/sources');
  return response.data;
};

export const getSource = async (sourceId: number): Promise<ContentSource> => {
  const response = await api.get(`/sources/${sourceId}`);
  return response.data;
};

export const deleteSource = async (sourceId: number): Promise<void> => {
  await api.delete(`/sources/${sourceId}`);
};

export const search = async (
  query: string,
  limit: number = 10,
  sourceId?: number
): Promise<SearchResult[]> => {
  const response = await api.post('/search', {
    query,
    limit,
    source_id: sourceId,
  });
  return response.data.results;
};
