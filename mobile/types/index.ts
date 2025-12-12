// TypeScript types for flashcard sync system

export interface User {
  id: number;
  email: string;
  device_id: string;
  created_at: string;
  last_login?: string;
  last_sync?: string;
}

export interface Deck {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  last_synced?: string;
  sync_version: number;
  card_count: number;
}

export interface Card {
  id: number;
  deck_id: number;
  question: string;
  answer: string;
  ease_factor: number;
  interval: number;
  repetition: number;
  next_review?: string;
  created_at: string;
  updated_at: string;
  last_synced?: string;
  sync_version: number;
}

export interface ReviewLog {
  id: number;
  card_id: number;
  grade: number; // 0-5 quality rating
  review_time: string;
  previous_srs: {
    ease_factor: number;
    interval: number;
    repetition: number;
  };
  new_srs: {
    ease_factor: number;
    interval: number;
    repetition: number;
  };
  created_at: string;
  synced: boolean;
}

export interface SyncLog {
  id: number;
  object_type: 'deck' | 'card' | 'review';
  object_id: number;
  operation: 'CREATE' | 'UPDATE' | 'DELETE';
  timestamp: string;
  synced: boolean;
  sync_error?: string;
  device_id?: string;
  created_by?: string;
}

export interface SyncSession {
  id: number;
  user_id: number;
  device_id: string;
  session_token: string;
  started_at: string;
  completed_at?: string;
  status: 'in_progress' | 'completed' | 'failed';
  pulled_objects: number;
  pushed_objects: number;
  conflicts: number;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  token?: string;
  expires_at?: string;
  error?: string;
}

export interface SyncResponse {
  success: boolean;
  data?: {
    decks: Deck[];
    cards: Card[];
    reviews: ReviewLog[];
    metadata: {
      last_sync: string;
      changes_count: number;
      sync_session_id: number;
    };
  };
  session?: SyncSession;
  conflicts?: number;
  error?: string;
}

export interface SyncChange {
  object_type: 'deck' | 'card' | 'review';
  operation: 'CREATE' | 'UPDATE' | 'DELETE';
  data: any;
  timestamp?: string;
}

export interface SyncStatus {
  unsynced_changes: number;
  last_sync?: string;
  device_id: string;
  recent_sessions: SyncSession[];
}

export interface ApiError {
  error: string;
  status?: number;
}

export interface AppConfig {
  API_BASE_URL: string;
  SYNC_INTERVAL_MINUTES: number;
  MAX_REVIEW_CARDS: number;
  RETRY_ATTEMPTS: number;
}

export type SyncState = 
  | 'idle'           // No sync in progress
  | 'syncing'        // Currently syncing
  | 'error'          // Sync failed
  | 'offline'        // No network connection
  | 'conflict';      // Sync conflicts detected