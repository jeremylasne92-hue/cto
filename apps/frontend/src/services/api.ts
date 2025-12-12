import axios from 'axios';
import { StudyStats, Deck, Card, FSRSResponse, QuizData, MindMapData, ApiResponse } from '../types';

// Mock API service for development
// In production, this would connect to the FastAPI backend

class ApiService {
  private baseURL = 'http://localhost:8000/api';

  // Stats endpoints
  async getStats(): Promise<ApiResponse<StudyStats>> {
    // Mock data for development
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: {
            totalCards: 1250,
            cardsDueToday: 45,
            cardsInQueue: 23,
            streakDays: 12,
            retentionPercentage: 87.5,
            averageInterval: 4.2,
            totalStudyTime: 2340,
            cardsReviewedToday: 32
          }
        });
      }, 100);
    });
  }

  async getRetentionData(): Promise<ApiResponse<any[]>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: [
            { day: 'Mon', retention: 85 },
            { day: 'Tue', retention: 88 },
            { day: 'Wed', retention: 82 },
            { day: 'Thu', retention: 90 },
            { day: 'Fri', retention: 87 },
            { day: 'Sat', retention: 92 },
            { day: 'Sun', retention: 89 }
          ]
        });
      }, 100);
    });
  }

  // Deck endpoints
  async getDecks(): Promise<ApiResponse<Deck[]>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: [
            {
              id: '1',
              name: 'Spanish Vocabulary',
              description: 'Common Spanish words and phrases',
              cardCount: 350,
              createdAt: new Date('2023-01-15'),
              updatedAt: new Date('2023-12-01')
            },
            {
              id: '2',
              name: 'Math Formulas',
              description: 'Important mathematical formulas',
              cardCount: 280,
              createdAt: new Date('2023-02-10'),
              updatedAt: new Date('2023-11-28')
            },
            {
              id: '3',
              name: 'History Dates',
              description: 'Key historical dates and events',
              cardCount: 190,
              createdAt: new Date('2023-03-05'),
              updatedAt: new Date('2023-12-05')
            }
          ]
        });
      }, 100);
    });
  }

  async getDeck(id: string): Promise<ApiResponse<Deck>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: {
            id,
            name: `Deck ${id}`,
            description: 'A study deck',
            cardCount: 100,
            createdAt: new Date(),
            updatedAt: new Date()
          }
        });
      }, 100);
    });
  }

  // Card endpoints
  async getDueCards(deckId?: string): Promise<ApiResponse<Card[]>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockCards: Card[] = [
          {
            id: '1',
            front: 'What is the Spanish word for "book"?',
            back: 'libro',
            deckId: deckId || '1',
            dueAt: new Date(),
            interval: 1,
            easeFactor: 2.5,
            repetitions: 3,
            lapses: 1,
            createdAt: new Date('2023-01-15'),
            updatedAt: new Date()
          },
          {
            id: '2',
            front: 'What is the derivative of x²?',
            back: '2x',
            deckId: deckId || '2',
            dueAt: new Date(),
            interval: 3,
            easeFactor: 2.3,
            repetitions: 5,
            lapses: 0,
            createdAt: new Date('2023-02-10'),
            updatedAt: new Date()
          },
          {
            id: '3',
            front: 'When did World War II end?',
            back: '1945',
            deckId: deckId || '3',
            dueAt: new Date(),
            interval: 6,
            easeFactor: 2.6,
            repetitions: 4,
            lapses: 0,
            createdAt: new Date('2023-03-05'),
            updatedAt: new Date()
          }
        ];

        resolve({
          success: true,
          data: deckId ? mockCards.filter(card => card.deckId === deckId) : mockCards
        });
      }, 100);
    });
  }

  async getNextCard(deckId?: string): Promise<ApiResponse<Card | null>> {
    const dueCards = await this.getDueCards(deckId);
    if (dueCards.success && dueCards.data && dueCards.data.length > 0) {
      return {
        success: true,
        data: dueCards.data[0]
      };
    }
    return {
      success: true,
      data: null
    };
  }

  // FSRS response submission
  async submitFSRSResponse(response: FSRSResponse): Promise<ApiResponse<any>> {
    try {
      // Check if we have Electron API available
      if (window.electronAPI) {
        const result = await window.electronAPI.submitFSRSResponse(response);
        return {
          success: result.success,
          data: result
        };
      }
    } catch (error) {
      console.error('Electron API error:', error);
    }

    // Fallback to HTTP API
    try {
      const apiResponse = await axios.post(`${this.baseURL}/fsrs/response`, response);
      return {
        success: true,
        data: apiResponse.data
      };
    } catch (error) {
      // Mock success for development
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            success: true,
            data: { message: 'Response recorded (mock)' }
          });
        }, 100);
      });
    }
  }

  // Quiz endpoints
  async getQuizzes(): Promise<ApiResponse<QuizData[]>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: [
            {
              id: '1',
              title: 'Spanish Basics Quiz',
              createdAt: new Date('2023-12-01'),
              questions: [
                {
                  id: '1',
                  question: 'How do you say "hello" in Spanish?',
                  options: ['Hola', 'Adiós', 'Gracias', 'Por favor'],
                  correctAnswer: 'Hola',
                  difficulty: 'easy'
                },
                {
                  id: '2',
                  question: 'What is the Spanish word for "water"?',
                  options: ['Agua', 'Fuego', 'Tierra', 'Aire'],
                  correctAnswer: 'Agua',
                  difficulty: 'easy'
                }
              ]
            }
          ]
        });
      }, 100);
    });
  }

  async getQuiz(id: string): Promise<ApiResponse<QuizData>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: {
            id,
            title: 'Sample Quiz',
            createdAt: new Date(),
            questions: [
              {
                id: '1',
                question: 'Sample question?',
                options: ['A', 'B', 'C', 'D'],
                correctAnswer: 'A',
                difficulty: 'easy'
              }
            ]
          }
        });
      }, 100);
    });
  }

  // Mind map endpoints
  async getMindMaps(): Promise<ApiResponse<MindMapData[]>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: [
            {
              id: '1',
              title: 'Spanish Grammar',
              createdAt: new Date('2023-12-01'),
              nodes: [
                {
                  id: 'root',
                  content: 'Spanish Grammar',
                  x: 400,
                  y: 300,
                  children: ['verbs', 'nouns', 'adjectives'],
                  expanded: true,
                  color: '#3182ce'
                },
                {
                  id: 'verbs',
                  content: 'Verbs',
                  x: 200,
                  y: 200,
                  children: ['conjugation'],
                  expanded: false,
                  color: '#38a169'
                },
                {
                  id: 'nouns',
                  content: 'Nouns',
                  x: 600,
                  y: 200,
                  children: ['gender', 'plural'],
                  expanded: false,
                  color: '#d69e2e'
                },
                {
                  id: 'adjectives',
                  content: 'Adjectives',
                  x: 400,
                  y: 500,
                  children: ['agreement'],
                  expanded: false,
                  color: '#e53e3e'
                }
              ]
            }
          ]
        });
      }, 100);
    });
  }

  async getMindMap(id: string): Promise<ApiResponse<MindMapData>> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          data: {
            id,
            title: 'Sample Mind Map',
            createdAt: new Date(),
            nodes: []
          }
        });
      }, 100);
    });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<any>> {
    try {
      const response = await axios.get(`${this.baseURL}/health`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: 'Backend not available'
      };
    }
  }
}

export const apiService = new ApiService();
