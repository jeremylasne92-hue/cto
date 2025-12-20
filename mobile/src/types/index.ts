export interface Card {
  id: string;
  deckId: string;
  front: string;
  back: string;
  conceptId?: string;
  lastReviewed?: Date;
  nextReview: Date;
  interval: number;
  easeFactor: number;
  repetitions: number;
  lapses: number;
}

export interface Deck {
  id: string;
  name: string;
  description?: string;
  totalCards: number;
  dueCards: number;
  reviewedToday: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface ReviewGrade {
  cardId: string;
  grade: 1 | 2 | 3 | 4;
  timestamp: Date;
  duration: number;
}

export interface ReviewSession {
  id: string;
  deckId?: string;
  startTime: Date;
  endTime?: Date;
  cardsReviewed: number;
  grades: ReviewGrade[];
}

export interface Concept {
  id: string;
  name: string;
  mastery: number;
  cardCount: number;
  relatedConcepts: string[];
  position?: { x: number; y: number };
}

export interface UserStats {
  totalCardsReviewed: number;
  currentStreak: number;
  longestStreak: number;
  streakFreezeCount: number;
  xp: number;
  level: number;
  retentionRate: number;
  reviewHistory: {
    date: string;
    reviewed: number;
    correct: number;
  }[];
}

export interface SyncStatus {
  lastSyncTime?: Date;
  pendingReviews: number;
  isSyncing: boolean;
  syncError?: string;
}

export interface UserSettings {
  darkMode: boolean;
  notificationsEnabled: boolean;
  notificationTime: string;
  userId?: string;
  email?: string;
}

export interface SRSState {
  interval: number;
  easeFactor: number;
  repetitions: number;
  lapses: number;
  nextReview: Date;
}

export type RootStackParamList = {
  MainTabs: undefined;
  ReviewSession: { deckId?: string };
};

export type TabParamList = {
  TodaysReviews: undefined;
  Decks: undefined;
  Stats: undefined;
  Graph: undefined;
  Settings: undefined;
};
