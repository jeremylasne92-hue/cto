import database from './database';
import api from './api';
import { SyncStatus } from '../types';

class SyncService {
  private isSyncing = false;
  private listeners: Array<(status: SyncStatus) => void> = [];

  addListener(callback: (status: SyncStatus) => void): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }

  private notifyListeners(status: SyncStatus): void {
    this.listeners.forEach((listener) => listener(status));
  }

  async sync(): Promise<void> {
    if (this.isSyncing) {
      console.log('Sync already in progress');
      return;
    }

    this.isSyncing = true;
    const startTime = new Date();

    try {
      this.notifyListeners({
        lastSyncTime: startTime,
        pendingReviews: 0,
        isSyncing: true,
      });

      // Check if online
      const isOnline = await api.checkConnection();
      if (!isOnline) {
        throw new Error('No internet connection');
      }

      // 1. Push local reviews to server
      await this.pushReviews();

      // 2. Pull decks from server
      await this.pullDecks();

      // 3. Pull due cards from server
      await this.pullCards();

      // 4. Pull concepts from server
      await this.pullConcepts();

      // 5. Pull user stats from server
      await this.pullStats();

      this.notifyListeners({
        lastSyncTime: new Date(),
        pendingReviews: 0,
        isSyncing: false,
      });

      console.log('Sync completed successfully');
    } catch (error) {
      console.error('Sync error:', error);
      this.notifyListeners({
        lastSyncTime: startTime,
        pendingReviews: await this.getPendingReviewsCount(),
        isSyncing: false,
        syncError: error instanceof Error ? error.message : 'Unknown error',
      });
      throw error;
    } finally {
      this.isSyncing = false;
    }
  }

  private async pushReviews(): Promise<void> {
    const unsyncedReviews = await database.getUnsyncedReviews();
    
    if (unsyncedReviews.length === 0) {
      console.log('No reviews to sync');
      return;
    }

    console.log(`Pushing ${unsyncedReviews.length} reviews to server`);
    await api.submitReviews(unsyncedReviews);
    
    const cardIds = unsyncedReviews.map((r) => r.cardId);
    await database.markReviewsSynced(cardIds);
  }

  private async pullDecks(): Promise<void> {
    console.log('Pulling decks from server');
    const decks = await api.syncDecks();
    
    for (const deck of decks) {
      await database.saveDeck(deck);
    }
    
    console.log(`Synced ${decks.length} decks`);
  }

  private async pullCards(): Promise<void> {
    console.log('Pulling cards from server');
    const cards = await api.syncCards();
    
    for (const card of cards) {
      await database.saveCard(card);
    }
    
    console.log(`Synced ${cards.length} cards`);
  }

  private async pullConcepts(): Promise<void> {
    console.log('Pulling concepts from server');
    const concepts = await api.syncConcepts();
    
    for (const concept of concepts) {
      await database.saveConcept(concept);
    }
    
    console.log(`Synced ${concepts.length} concepts`);
  }

  private async pullStats(): Promise<void> {
    console.log('Pulling user stats from server');
    const stats = await api.getUserStats();
    await database.updateUserStats(stats);
  }

  private async getPendingReviewsCount(): Promise<number> {
    const reviews = await database.getUnsyncedReviews();
    return reviews.length;
  }

  async getSyncStatus(): Promise<SyncStatus> {
    return {
      pendingReviews: await this.getPendingReviewsCount(),
      isSyncing: this.isSyncing,
    };
  }
}

export default new SyncService();
