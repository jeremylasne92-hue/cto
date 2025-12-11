import { create } from 'zustand';
import {
  Card,
  Deck,
  ReviewGrade,
  Concept,
  UserStats,
  SyncStatus,
  UserSettings,
  ReviewSession,
} from '../types';
import database from '../services/database';
import sync from '../services/sync';
import { calculateNextReview, calculateXP, calculateLevel } from '../utils/srs';

interface AppState {
  // Data
  decks: Deck[];
  dueCards: Card[];
  concepts: Concept[];
  userStats: UserStats | null;
  syncStatus: SyncStatus;
  settings: UserSettings;
  currentSession: ReviewSession | null;

  // Loading states
  isLoading: boolean;
  error: string | null;

  // Actions
  initializeApp: () => Promise<void>;
  loadDecks: () => Promise<void>;
  loadDueCards: () => Promise<void>;
  loadConcepts: () => Promise<void>;
  loadUserStats: () => Promise<void>;
  startReviewSession: (deckId?: string) => Promise<void>;
  gradeCard: (cardId: string, grade: 1 | 2 | 3 | 4, duration: number) => Promise<void>;
  endReviewSession: () => void;
  syncData: () => Promise<void>;
  updateSettings: (settings: Partial<UserSettings>) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  decks: [],
  dueCards: [],
  concepts: [],
  userStats: null,
  syncStatus: {
    pendingReviews: 0,
    isSyncing: false,
  },
  settings: {
    darkMode: false,
    notificationsEnabled: true,
    notificationTime: '09:00',
  },
  currentSession: null,
  isLoading: false,
  error: null,

  // Initialize app
  initializeApp: async () => {
    set({ isLoading: true, error: null });
    try {
      await database.init();
      await get().loadDecks();
      await get().loadDueCards();
      await get().loadConcepts();
      await get().loadUserStats();
      
      // Try to sync in background
      get().syncData().catch(console.error);
      
      set({ isLoading: false });
    } catch (error) {
      console.error('App initialization error:', error);
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Initialization failed',
      });
    }
  },

  // Load decks
  loadDecks: async () => {
    try {
      const decks = await database.getAllDecks();
      set({ decks });
    } catch (error) {
      console.error('Error loading decks:', error);
      throw error;
    }
  },

  // Load due cards
  loadDueCards: async () => {
    try {
      const dueCards = await database.getDueCards();
      set({ dueCards });
    } catch (error) {
      console.error('Error loading due cards:', error);
      throw error;
    }
  },

  // Load concepts
  loadConcepts: async () => {
    try {
      const concepts = await database.getAllConcepts();
      set({ concepts });
    } catch (error) {
      console.error('Error loading concepts:', error);
      throw error;
    }
  },

  // Load user stats
  loadUserStats: async () => {
    try {
      let userStats = await database.getUserStats();
      
      // Initialize stats if not exists
      if (!userStats) {
        userStats = {
          totalCardsReviewed: 0,
          currentStreak: 0,
          longestStreak: 0,
          streakFreezeCount: 0,
          xp: 0,
          level: 1,
          retentionRate: 0,
          reviewHistory: [],
        };
        await database.updateUserStats(userStats);
      }
      
      set({ userStats });
    } catch (error) {
      console.error('Error loading user stats:', error);
      throw error;
    }
  },

  // Start review session
  startReviewSession: async (deckId?: string) => {
    try {
      const cards = deckId
        ? await database.getCardsByDeck(deckId).then((cards) =>
            cards.filter((c) => new Date(c.nextReview) <= new Date())
          )
        : await database.getDueCards();

      const session: ReviewSession = {
        id: Date.now().toString(),
        deckId,
        startTime: new Date(),
        cardsReviewed: 0,
        grades: [],
      };

      set({ currentSession: session, dueCards: cards });
    } catch (error) {
      console.error('Error starting review session:', error);
      throw error;
    }
  },

  // Grade card
  gradeCard: async (cardId: string, grade: 1 | 2 | 3 | 4, duration: number) => {
    try {
      const { dueCards, currentSession, userStats } = get();
      const card = dueCards.find((c) => c.id === cardId);
      
      if (!card || !currentSession || !userStats) return;

      // Calculate new SRS state
      const newState = calculateNextReview(
        {
          interval: card.interval,
          easeFactor: card.easeFactor,
          repetitions: card.repetitions,
          lapses: card.lapses,
          nextReview: card.nextReview,
        },
        grade
      );

      // Update card
      const updatedCard: Card = {
        ...card,
        lastReviewed: new Date(),
        ...newState,
      };
      await database.updateCard(updatedCard);

      // Save review
      const review: ReviewGrade = {
        cardId,
        grade,
        timestamp: new Date(),
        duration,
      };
      await database.saveReview(review);

      // Update session
      const updatedSession = {
        ...currentSession,
        cardsReviewed: currentSession.cardsReviewed + 1,
        grades: [...currentSession.grades, review],
      };

      // Update user stats
      const xpGain = calculateXP(grade);
      const newXP = userStats.xp + xpGain;
      const newLevel = calculateLevel(newXP);
      const updatedStats = {
        ...userStats,
        totalCardsReviewed: userStats.totalCardsReviewed + 1,
        xp: newXP,
        level: newLevel,
      };
      await database.updateUserStats(updatedStats);

      // Update state
      set({
        dueCards: dueCards.filter((c) => c.id !== cardId),
        currentSession: updatedSession,
        userStats: updatedStats,
      });

      // Reload decks to update stats
      await get().loadDecks();
    } catch (error) {
      console.error('Error grading card:', error);
      throw error;
    }
  },

  // End review session
  endReviewSession: () => {
    const { currentSession } = get();
    if (currentSession) {
      set({
        currentSession: { ...currentSession, endTime: new Date() },
      });
    }
    setTimeout(() => {
      set({ currentSession: null });
    }, 100);
  },

  // Sync data
  syncData: async () => {
    try {
      await sync.sync();
      
      // Reload all data after sync
      await get().loadDecks();
      await get().loadDueCards();
      await get().loadConcepts();
      await get().loadUserStats();
      
      const syncStatus = await sync.getSyncStatus();
      set({ syncStatus });
    } catch (error) {
      console.error('Sync error:', error);
      const syncStatus = await sync.getSyncStatus();
      set({ syncStatus });
      throw error;
    }
  },

  // Update settings
  updateSettings: (settings: Partial<UserSettings>) => {
    set((state) => ({
      settings: { ...state.settings, ...settings },
    }));
  },

  // Set error
  setError: (error: string | null) => {
    set({ error });
  },
}));
