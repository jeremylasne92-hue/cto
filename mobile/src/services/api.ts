import axios, { AxiosInstance } from 'axios';
import { Card, Deck, ReviewGrade, Concept, UserStats } from '../types';

class APIService {
  private client: AxiosInstance;
  private baseURL: string = 'http://localhost:3000/api'; // Configure as needed

  constructor() {
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth interceptor
    this.client.interceptors.request.use(async (config) => {
      // Add auth token if available
      const token = await this.getAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  private async getAuthToken(): Promise<string | null> {
    // Implement token retrieval from secure storage
    return null;
  }

  setBaseURL(url: string): void {
    this.baseURL = url;
    this.client.defaults.baseURL = url;
  }

  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async syncDecks(): Promise<Deck[]> {
    const response = await this.client.get('/decks');
    return response.data;
  }

  async syncCards(deckId?: string): Promise<Card[]> {
    const url = deckId ? `/cards?deckId=${deckId}` : '/cards/due';
    const response = await this.client.get(url);
    return response.data;
  }

  async submitReviews(reviews: ReviewGrade[]): Promise<void> {
    await this.client.post('/reviews', { reviews });
  }

  async syncConcepts(): Promise<Concept[]> {
    const response = await this.client.get('/concepts');
    return response.data;
  }

  async getUserStats(): Promise<UserStats> {
    const response = await this.client.get('/stats');
    return response.data;
  }

  async checkConnection(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch {
      return false;
    }
  }
}

export default new APIService();
