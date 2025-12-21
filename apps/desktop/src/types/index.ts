// Core Definitions from Backend (Sync with CTO.new)
// ----------------------------------------------------

export interface SrsState {
  difficulty: number;     // 0-10
  stability: number;      // days
  retrievability: number; // 0-1
  due_date: string;       // ISO Date
}

export interface Card {
  id: string;
  deck_id: string;
  front: string;
  back: string;
  card_type: 'quiz' | 'flashcard' | 'mindmap';
  srs_state: SrsState;
  // Legacy fields fallback (optional)
  dueAt?: Date;
}

export interface Deck {
  id: string;
  name: string;
  card_count: number;
  due_today: number;
}

export interface Profile {
  id: string;
  handle: string;
  bio: string;
  interests: string[];
}

export interface Quiz {
  id: string;
  type: 'mcq_single' | 'mcq_multiple' | 'fill_blank' | 'matching' | 'ordering';
  question: string;
  options?: string[];
  correct_answer: string | string[];
  difficulty: number;
}

export interface MindMapNode {
  id: string;
  label: string;
  children: MindMapNode[];
  mastery_level: number;
  color: string;
}

// UI & Legacy Support
// -------------------

export interface StudyStats {
  totalCards: number;
  cardsDueToday: number;
  streakDays: number;
  retentionPercentage: number;
  totalStudyTime: number; // in minutes
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Re-export specific responses
export interface DecksResponse extends ApiResponse<Deck[]> { }
