// API service for mobile app

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthResponse, ApiError } from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;
  private tokenKey = 'auth_token';

  constructor(baseURL: string = 'http://localhost:5000') {
    this.baseURL = baseURL;
    this.api = axios.create({
      baseURL: `${baseURL}/api`,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await this.clearToken();
          // Could trigger re-auth here
        }
        return Promise.reject(error);
      }
    );
  }

  async register(email: string, password: string, deviceId?: string): Promise<AuthResponse> {
    try {
      const response = await this.api.post('/auth/register', {
        email,
        password,
        device_id: deviceId,
      });
      
      const data = response.data;
      
      if (data.token) {
        await this.setToken(data.token);
      }
      
      return {
        success: true,
        user: data.user,
        token: data.token,
        expires_at: data.expires_at,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await this.api.post('/auth/login', {
        email,
        password,
      });
      
      const data = response.data;
      
      if (data.token) {
        await this.setToken(data.token);
      }
      
      return {
        success: true,
        user: data.user,
        token: data.token,
        expires_at: data.expires_at,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  async logout(): Promise<void> {
    await this.clearToken();
  }

  async getDueCards(): Promise<any> {
    try {
      const response = await this.api.get('/cards/due');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async submitReview(cardId: number, grade: number): Promise<any> {
    try {
      const response = await this.api.post('/reviews', {
        card_id: cardId,
        grade,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async getDecks(): Promise<any> {
    try {
      const response = await this.api.get('/decks');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async getDeckCards(deckId: number): Promise<any> {
    try {
      const response = await this.api.get(`/decks/${deckId}/cards`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async getCardReviews(cardId: number): Promise<any> {
    try {
      const response = await this.api.get(`/reviews/${cardId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async getContent(): Promise<any> {
    try {
      const response = await this.api.get('/content');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async syncPull(lastSync?: string): Promise<any> {
    try {
      const response = await this.api.post('/sync/pull', {
        last_sync: lastSync,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async syncPush(changes: any[]): Promise<any> {
    try {
      const response = await this.api.post('/sync/push', {
        changes,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async getSyncStatus(): Promise<any> {
    try {
      const response = await this.api.get('/sync/status');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async forceSync(): Promise<any> {
    try {
      const response = await this.api.post('/sync/force');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message);
    }
  }

  async verifyConnection(): Promise<boolean> {
    try {
      await this.api.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  // Token management
  async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(this.tokenKey);
    } catch (error) {
      console.error('Error getting token:', error);
      return null;
    }
  }

  async setToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(this.tokenKey, token);
    } catch (error) {
      console.error('Error setting token:', error);
    }
  }

  async clearToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.tokenKey);
    } catch (error) {
      console.error('Error clearing token:', error);
    }
  }

  // Network status
  async isOnline(): Promise<boolean> {
    try {
      // Simple ping to check connectivity
      const response = await this.api.get('/health', { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  // Update base URL (for development/testing)
  updateBaseURL(newBaseURL: string): void {
    this.baseURL = newBaseURL;
    this.api.defaults.baseURL = `${newBaseURL}/api`;
  }
}

export default new ApiService();