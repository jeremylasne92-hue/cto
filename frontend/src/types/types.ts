export interface IngestionJob {
  id: number;
  status: string;
  progress: number;
  error_message?: string;
  source_id?: number;
  created_at: string;
  updated_at: string;
}

export interface ContentSource {
  id: number;
  source_type: string;
  title: string;
  author: string;
  hash: string;
  created_at: string;
}

export interface SearchResult {
  chunk_id: string;
  source_id: number;
  text: string;
  chunk_type: string;
  chunk_order: number;
  _distance?: number;
}
