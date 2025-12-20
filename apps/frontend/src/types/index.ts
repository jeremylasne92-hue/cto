// Core data types
export interface Card {
  id: string;
  front: string;
  back: string;
  deckId: string;
  dueAt: Date;
  interval: number;
  easeFactor: number;
  repetitions: number;
  lapses: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Deck {
  id: string;
  name: string;
  description?: string;
  cardCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface StudyStats {
  totalCards: number;
  cardsDueToday: number;
  cardsInQueue: number;
  streakDays: number;
  retentionPercentage: number;
  averageInterval: number;
  totalStudyTime: number; // in minutes
  cardsReviewedToday: number;
}

export interface StudySession {
  id: string;
  startTime: Date;
  endTime?: Date;
  cardsReviewed: number;
  correctAnswers: number;
  totalTime: number; // in seconds
  averageResponseTime: number; // in seconds
}

export interface FSRSResponse {
  cardId: string;
  rating: 'again' | 'hard' | 'good' | 'easy';
  responseTime: number; // in seconds
  timestamp: Date;
  isCorrect: boolean;
}

export interface QuizData {
  id: string;
  title: string;
  questions: QuizQuestion[];
  createdAt: Date;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options?: string[];
  correctAnswer: string | string[];
  explanation?: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface MindMapData {
  id: string;
  title: string;
  nodes: MindMapNode[];
  createdAt: Date;
}

export interface MindMapNode {
  id: string;
  content: string;
  x: number;
  y: number;
  children: string[];
  expanded: boolean;
  color?: string;
}

export interface StudyProgress {
  dailyGoal: number;
  cardsReviewed: number;
  timeSpent: number; // in minutes
  retentionRate: number;
  streakDays: number;
}

export interface UIState {
  darkMode: boolean;
  sidebarCollapsed: boolean;
  currentView: 'dashboard' | 'review' | 'quiz' | 'mindmap';
  isOnline: boolean;
  isLoading: boolean;
  error?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface StatsResponse extends ApiResponse<StudyStats> {}
export interface CardsResponse extends ApiResponse<Card[]> {}
export interface DeckResponse extends ApiResponse<Deck> {}
export interface DecksResponse extends ApiResponse<Deck[]> {}
