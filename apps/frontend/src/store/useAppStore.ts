import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { Card, Deck, StudyStats, StudySession, FSRSResponse, UIState } from '../types';

interface AppState extends UIState {
  // Current study session
  currentSession: StudySession | null;
  sessionStartTime: Date | null;
  sessionCardsReviewed: number;
  sessionCorrectAnswers: number;
  sessionTotalTime: number;
  
  // Study data
  cards: Card[];
  decks: Deck[];
  currentDeck: Deck | null;
  currentCardIndex: number;
  studyQueue: Card[];
  dueCards: Card[];
  
  // Stats
  stats: StudyStats | null;
  todayProgress: number;
  
  // Actions
  setDarkMode: (dark: boolean) => void;
  toggleSidebar: () => void;
  setCurrentView: (view: 'dashboard' | 'review' | 'quiz' | 'mindmap') => void;
  setOnlineStatus: (online: boolean) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | undefined) => void;
  
  // Study actions
  startSession: () => void;
  endSession: () => void;
  submitFSRSResponse: (response: FSRSResponse) => void;
  setCurrentDeck: (deck: Deck | null) => void;
  nextCard: () => void;
  previousCard: () => void;
  
  // Data actions
  setCards: (cards: Card[]) => void;
  setDecks: (decks: Deck[]) => void;
  setStats: (stats: StudyStats) => void;
  loadDueCards: (deckId?: string) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      darkMode: false,
      sidebarCollapsed: false,
      currentView: 'dashboard',
      isOnline: true,
      isLoading: false,
      
      currentSession: null,
      sessionStartTime: null,
      sessionCardsReviewed: 0,
      sessionCorrectAnswers: 0,
      sessionTotalTime: 0,
      
      cards: [],
      decks: [],
      currentDeck: null,
      currentCardIndex: 0,
      studyQueue: [],
      dueCards: [],
      
      stats: null,
      todayProgress: 0,
      
      // UI Actions
      setDarkMode: (dark) => set({ darkMode: dark }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setCurrentView: (view) => set({ currentView: view }),
      setOnlineStatus: (online) => set({ isOnline: online }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      
      // Study Actions
      startSession: () => {
        const session: StudySession = {
          id: Date.now().toString(),
          startTime: new Date(),
          cardsReviewed: 0,
          correctAnswers: 0,
          totalTime: 0,
          averageResponseTime: 0
        };
        set({
          currentSession: session,
          sessionStartTime: new Date(),
          sessionCardsReviewed: 0,
          sessionCorrectAnswers: 0,
          sessionTotalTime: 0
        });
      },
      
      endSession: () => {
        const { currentSession, sessionStartTime } = get();
        if (currentSession && sessionStartTime) {
          const endTime = new Date();
          const totalTime = (endTime.getTime() - sessionStartTime.getTime()) / 1000;
          
          set({
            currentSession: {
              ...currentSession,
              endTime,
              totalTime,
              cardsReviewed: get().sessionCardsReviewed,
              correctAnswers: get().sessionCorrectAnswers,
              averageResponseTime: totalTime / Math.max(get().sessionCardsReviewed, 1)
            }
          });
        }
      },
      
      submitFSRSResponse: (response) => {
        const { sessionCardsReviewed, sessionCorrectAnswers } = get();
        
        set({
          sessionCardsReviewed: sessionCardsReviewed + 1,
          sessionCorrectAnswers: sessionCorrectAnswers + (response.isCorrect ? 1 : 0)
        });
        
        // Update current card in queue
        const { currentCardIndex, studyQueue } = get();
        if (studyQueue.length > 0 && currentCardIndex < studyQueue.length) {
          const updatedQueue = [...studyQueue];
          // Remove the current card or update its due date
          updatedQueue.splice(currentCardIndex, 1);
          set({ studyQueue: updatedQueue });
        }
      },
      
      setCurrentDeck: (deck) => set({ currentDeck: deck }),
      
      nextCard: () => {
        const { currentCardIndex, studyQueue } = get();
        if (currentCardIndex < studyQueue.length - 1) {
          set({ currentCardIndex: currentCardIndex + 1 });
        }
      },
      
      previousCard: () => {
        const { currentCardIndex } = get();
        if (currentCardIndex > 0) {
          set({ currentCardIndex: currentCardIndex - 1 });
        }
      },
      
      // Data Actions
      setCards: (cards) => set({ cards }),
      setDecks: (decks) => set({ decks }),
      setStats: (stats) => {
        set({ 
          stats,
          todayProgress: stats.cardsReviewedToday / Math.max(stats.cardsDueToday, 1) * 100
        });
      },
      
      loadDueCards: (deckId) => {
        const { cards } = get();
        const dueCards = cards.filter(card => {
          const isDue = new Date(card.dueAt) <= new Date();
          const matchesDeck = !deckId || card.deckId === deckId;
          return isDue && matchesDeck;
        });
        
        set({ 
          dueCards,
          studyQueue: [...dueCards],
          currentCardIndex: 0
        });
      }
    }),
    {
      name: 'cognisphere-app-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        darkMode: state.darkMode,
        sidebarCollapsed: state.sidebarCollapsed,
        currentView: state.currentView,
        decks: state.decks,
        stats: state.stats
      })
    }
  )
);
