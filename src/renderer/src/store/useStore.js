import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// App store with all application state
const useStore = create(
  persist(
    (set, get) => ({
      // Theme state
      theme: 'light',
      setTheme: (theme) => {
        set({ theme })
        // Apply theme to document
        if (typeof document !== 'undefined') {
          document.documentElement.classList.remove('light', 'dark')
          document.documentElement.classList.add(theme)
        }
      },

      // User settings
      settings: {
        theme: 'light',
        hardwareTier: 'auto',
        llmProvider: 'local',
        reviewSessionDuration: 30,
        cardOrder: 'due-first',
        notifications: true,
        soundEnabled: true,
        autoSync: true,
      },
      updateSettings: (updates) => set((state) => ({ 
        settings: { ...state.settings, ...updates } 
      })),

      // User statistics
      stats: {
        totalCards: 0,
        cardsReviewedToday: 0,
        currentStreak: 0,
        totalXP: 0,
        averageAccuracy: 0,
        retentionRate: 0,
        lastReviewDate: null,
      },
      updateStats: (updates) => set((state) => ({ 
        stats: { ...state.stats, ...updates } 
      })),

      // Deck management
      decks: [
        {
          id: 'default',
          name: 'Default Deck',
          description: 'Your main learning deck',
          totalCards: 0,
          dueCards: 0,
          newCards: 0,
          createdAt: new Date().toISOString(),
          lastReviewed: null,
        }
      ],
      currentDeck: 'default',
      setCurrentDeck: (deckId) => set({ currentDeck: deckId }),
      
      addDeck: (deck) => set((state) => ({ 
        decks: [...state.decks, { ...deck, id: Date.now().toString() }] 
      })),
      
      updateDeck: (deckId, updates) => set((state) => ({
        decks: state.decks.map(deck => 
          deck.id === deckId ? { ...deck, ...updates } : deck
        )
      })),
      
      deleteDeck: (deckId) => set((state) => ({
        decks: state.decks.filter(deck => deck.id !== deckId),
        currentDeck: state.currentDeck === deckId ? 'default' : state.currentDeck
      })),

      // Review session state
      reviewSession: {
        isActive: false,
        currentCard: null,
        cardsInSession: [],
        sessionStartTime: null,
        cardsReviewed: 0,
        correctAnswers: 0,
        sessionStats: {
          totalTime: 0,
          averageCardTime: 0,
        }
      },
      
      startReviewSession: (cards) => set((state) => ({
        reviewSession: {
          ...state.reviewSession,
          isActive: true,
          cardsInSession: cards,
          sessionStartTime: Date.now(),
          cardsReviewed: 0,
          correctAnswers: 0,
        }
      })),
      
      nextCard: () => set((state) => {
        const { cardsInSession, cardsReviewed } = state.reviewSession
        const nextIndex = cardsReviewed
        return {
          reviewSession: {
            ...state.reviewSession,
            currentCard: cardsInSession[nextIndex] || null,
            cardsReviewed: cardsReviewed + 1,
          }
        }
      }),
      
      answerCard: (correct) => set((state) => ({
        reviewSession: {
          ...state.reviewSession,
          correctAnswers: correct 
            ? state.reviewSession.correctAnswers + 1 
            : state.reviewSession.correctAnswers,
        }
      })),
      
      endReviewSession: () => set((state) => ({
        reviewSession: {
          ...state.reviewSession,
          isActive: false,
          currentCard: null,
          sessionStartTime: null,
        }
      })),

      // Ingestion state
      ingestion: {
        isActive: false,
        currentJob: null,
        jobQueue: [],
        progress: 0,
        status: 'idle',
        error: null,
      },
      
      startIngestion: (job) => set((state) => ({
        ingestion: {
          ...state.ingestion,
          isActive: true,
          currentJob: job,
          status: 'processing',
          progress: 0,
          error: null,
        }
      })),
      
      updateIngestionProgress: (progress, status) => set((state) => ({
        ingestion: {
          ...state.ingestion,
          progress,
          status: status || state.ingestion.status,
        }
      })),
      
      completeIngestion: () => set((state) => ({
        ingestion: {
          ...state.ingestion,
          isActive: false,
          currentJob: null,
          progress: 100,
          status: 'completed',
        }
      })),
      
      failIngestion: (error) => set((state) => ({
        ingestion: {
          ...state.ingestion,
          isActive: false,
          status: 'failed',
          error,
        }
      })),

      // UI state
      sidebarOpen: true,
      currentView: 'dashboard',
      notifications: [],
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setCurrentView: (view) => set({ currentView: view }),
      
      addNotification: (notification) => set((state) => ({
        notifications: [...state.notifications, {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          ...notification
        }]
      })),
      
      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter(n => n.id !== id)
      })),

      // Daily review history for charts
      reviewHistory: [],
      updateReviewHistory: (entry) => set((state) => ({
        reviewHistory: [...state.reviewHistory, entry]
      })),

      // Content items (cards, quizzes, mind maps)
      contentItems: [],
      addContentItem: (item) => set((state) => ({
        contentItems: [...state.contentItems, { ...item, id: Date.now().toString() }]
      })),
      
      updateContentItem: (id, updates) => set((state) => ({
        contentItems: state.contentItems.map(item => 
          item.id === id ? { ...item, ...updates } : item
        )
      })),
      
      deleteContentItem: (id) => set((state) => ({
        contentItems: state.contentItems.filter(item => item.id !== id)
      })),
    }),
    {
      name: 'learning-platform-store',
      partialize: (state) => ({
        theme: state.theme,
        settings: state.settings,
        stats: state.stats,
        decks: state.decks,
        currentDeck: state.currentDeck,
        reviewHistory: state.reviewHistory,
        contentItems: state.contentItems,
      }),
    }
  )
)

// Initialize theme on store creation
if (typeof document !== 'undefined') {
  const { theme, setTheme } = useStore.getState()
  document.documentElement.classList.add(theme)
}

export default useStore
