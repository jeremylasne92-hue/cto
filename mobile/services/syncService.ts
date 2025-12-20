// Sync service for mobile app with offline support and conflict resolution

import SQLite from 'react-native-sqlite-storage';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ApiService from './apiService';
import { SyncChange, SyncState, SyncStatus, Card, ReviewLog } from '../types';

class SyncService {
  private db: SQLite.SQLiteDatabase | null = null;
  private isInitialized = false;
  private syncQueue: SyncChange[] = [];
  private syncState: SyncState = 'idle';
  private lastSyncTime: string | null = null;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase(): Promise<void> {
    try {
      this.db = await SQLite.openDatabase({
        name: 'FlashcardsDB',
        location: 'default',
      });

      await this.createTables();
      this.isInitialized = true;
      
      // Load sync queue from local storage
      await this.loadSyncQueue();
    } catch (error) {
      console.error('Failed to initialize database:', error);
      throw error;
    }
  }

  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    // Cards table
    await this.db.executeSql(`
      CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY,
        deck_id INTEGER,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        ease_factor REAL DEFAULT 2.5,
        interval INTEGER DEFAULT 1,
        repetition INTEGER DEFAULT 0,
        next_review DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_synced DATETIME,
        sync_version INTEGER DEFAULT 1,
        is_dirty INTEGER DEFAULT 0
      )
    `);

    // Decks table
    await this.db.executeSql(`
      CREATE TABLE IF NOT EXISTS decks (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_synced DATETIME,
        sync_version INTEGER DEFAULT 1,
        is_dirty INTEGER DEFAULT 0
      )
    `);

    // Review logs table
    await this.db.executeSql(`
      CREATE TABLE IF NOT EXISTS review_logs (
        id INTEGER PRIMARY KEY,
        card_id INTEGER,
        grade INTEGER NOT NULL,
        review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        previous_ease_factor REAL,
        previous_interval INTEGER,
        previous_repetition INTEGER,
        new_ease_factor REAL,
        new_interval INTEGER,
        new_repetition INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        synced INTEGER DEFAULT 0
      )
    `);

    // Sync queue table
    await this.db.executeSql(`
      CREATE TABLE IF NOT EXISTS sync_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        object_type TEXT NOT NULL,
        operation TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3
      )
    `);

    // Sync metadata table
    await this.db.executeSql(`
      CREATE TABLE IF NOT EXISTS sync_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);
  }

  async saveCard(card: Card, sync: boolean = true): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      await this.db.transaction(async (tx) => {
        await tx.executeSql(
          `INSERT OR REPLACE INTO cards 
           (id, deck_id, question, answer, ease_factor, interval, repetition, 
            next_review, created_at, updated_at, last_synced, sync_version, is_dirty)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            card.id,
            card.deck_id,
            card.question,
            card.answer,
            card.ease_factor,
            card.interval,
            card.repetition,
            card.next_review,
            card.created_at,
            card.updated_at,
            card.last_synced,
            card.sync_version,
            sync ? 0 : 1
          ]
        );

        if (!sync) {
          await this.queueSyncChange({
            object_type: 'card',
            operation: 'UPDATE',
            data: card
          });
        }
      });
    } catch (error) {
      console.error('Error saving card:', error);
      throw error;
    }
  }

  async getDueCards(): Promise<Card[]> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      const [results] = await this.db.executeSql(
        `SELECT * FROM cards 
         WHERE next_review <= datetime('now') 
         AND (next_review IS NOT NULL) 
         ORDER BY next_review ASC 
         LIMIT 50`
      );

      const cards: Card[] = [];
      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        cards.push({
          id: row.id,
          deck_id: row.deck_id,
          question: row.question,
          answer: row.answer,
          ease_factor: row.ease_factor,
          interval: row.interval,
          repetition: row.repetition,
          next_review: row.next_review,
          created_at: row.created_at,
          updated_at: row.updated_at,
          last_synced: row.last_synced,
          sync_version: row.sync_version
        });
      }

      return cards;
    } catch (error) {
      console.error('Error getting due cards:', error);
      throw error;
    }
  }

  async submitReview(cardId: number, grade: number): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      // Get card from local database
      const [results] = await this.db.executeSql(
        'SELECT * FROM cards WHERE id = ?',
        [cardId]
      );

      if (results.rows.length === 0) {
        throw new Error('Card not found');
      }

      const card = results.rows.item(0);
      
      // Calculate new SRS values
      const newSRS = this.calculateSRSUpdate(card, grade);

      await this.db.transaction(async (tx) => {
        // Update card
        await tx.executeSql(
          `UPDATE cards 
           SET ease_factor = ?, interval = ?, repetition = ?, 
               next_review = datetime('now', '+' || ? || ' days'),
               updated_at = datetime('now'), is_dirty = 1
           WHERE id = ?`,
          [
            newSRS.ease_factor,
            newSRS.interval,
            newSRS.repetition,
            newSRS.interval,
            cardId
          ]
        );

        // Insert review log
        await tx.executeSql(
          `INSERT INTO review_logs 
           (card_id, grade, previous_ease_factor, previous_interval, previous_repetition,
            new_ease_factor, new_interval, new_repetition, synced)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)`,
          [
            cardId,
            grade,
            card.ease_factor,
            card.interval,
            card.repetition,
            newSRS.ease_factor,
            newSRS.interval,
            newSRS.repetition
          ]
        );

        // Queue review for sync
        await this.queueSyncChange(tx, {
          object_type: 'review',
          operation: 'CREATE',
          data: {
            card_id: cardId,
            grade,
            review_time: new Date().toISOString()
          }
        });
      });

    } catch (error) {
      console.error('Error submitting review:', error);
      throw error;
    }
  }

  private calculateSRSUpdate(card: any, grade: number) {
    let easeFactor = card.ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02));
    
    if (easeFactor < 1.3) {
      easeFactor = 1.3;
    }

    let repetition = card.repetition;
    let interval = card.interval;

    if (grade < 3) {
      repetition = 0;
      interval = 1;
    } else {
      if (repetition === 0) {
        interval = 1;
      } else if (repetition === 1) {
        interval = 6;
      } else {
        interval = Math.round(interval * easeFactor);
      }
      repetition += 1;
    }

    return {
      ease_factor: Math.round(easeFactor * 100) / 100,
      interval,
      repetition
    };
  }

  private async queueSyncChange(tx: any, change: SyncChange): Promise<void> {
    await tx.executeSql(
      'INSERT INTO sync_queue (object_type, operation, data) VALUES (?, ?, ?)',
      [change.object_type, change.operation, JSON.stringify(change.data)]
    );
  }

  async queueSyncChange(change: SyncChange): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql(
      'INSERT INTO sync_queue (object_type, operation, data) VALUES (?, ?, ?)',
      [change.object_type, change.operation, JSON.stringify(change.data)]
    );

    // Update local queue cache
    this.syncQueue.push(change);
  }

  private async loadSyncQueue(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      const [results] = await this.db.executeSql(
        'SELECT * FROM sync_queue ORDER BY timestamp ASC'
      );

      this.syncQueue = [];
      for (let i = 0; i < results.rows.length; i++) {
        const row = results.rows.item(i);
        this.syncQueue.push({
          object_type: row.object_type,
          operation: row.operation,
          data: JSON.parse(row.data),
          timestamp: row.timestamp
        });
      }
    } catch (error) {
      console.error('Error loading sync queue:', error);
      this.syncQueue = [];
    }
  }

  async syncWithServer(): Promise<void> {
    if (this.syncState === 'syncing') {
      return; // Already syncing
    }

    this.setSyncState('syncing');

    try {
      // Check if online
      const isOnline = await ApiService.isOnline();
      if (!isOnline) {
        this.setSyncState('offline');
        return;
      }

      // Pull changes from server
      await this.pullChanges();
      
      // Push queued changes
      await this.pushChanges();
      
      // Update last sync time
      this.lastSyncTime = new Date().toISOString();
      await this.saveLastSyncTime(this.lastSyncTime);

      this.setSyncState('idle');
    } catch (error) {
      console.error('Sync error:', error);
      this.setSyncState('error');
      throw error;
    }
  }

  private async pullChanges(): Promise<void> {
    try {
      const response = await ApiService.syncPull(this.lastSyncTime);
      
      if (response.success && response.data) {
        await this.applyPulledChanges(response.data);
      }
    } catch (error) {
      console.error('Error pulling changes:', error);
      throw error;
    }
  }

  private async applyPulledChanges(data: any): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.transaction(async (tx) => {
      // Apply decks
      if (data.decks && Array.isArray(data.decks)) {
        for (const deck of data.decks) {
          await tx.executeSql(
            `INSERT OR REPLACE INTO decks 
             (id, name, description, created_at, updated_at, last_synced, sync_version, is_dirty)
             VALUES (?, ?, ?, ?, ?, ?, ?, 0)`,
            [
              deck.id,
              deck.name,
              deck.description,
              deck.created_at,
              deck.updated_at,
              deck.last_synced,
              deck.sync_version
            ]
          );
        }
      }

      // Apply cards
      if (data.cards && Array.isArray(data.cards)) {
        for (const card of data.cards) {
          await tx.executeSql(
            `INSERT OR REPLACE INTO cards 
             (id, deck_id, question, answer, ease_factor, interval, repetition,
              next_review, created_at, updated_at, last_synced, sync_version, is_dirty)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)`,
            [
              card.id,
              card.deck_id,
              card.question,
              card.answer,
              card.ease_factor,
              card.interval,
              card.repetition,
              card.next_review,
              card.created_at,
              card.updated_at,
              card.last_synced,
              card.sync_version
            ]
          );
        }
      }

      // Apply reviews (append-only)
      if (data.reviews && Array.isArray(data.reviews)) {
        for (const review of data.reviews) {
          await tx.executeSql(
            `INSERT OR IGNORE INTO review_logs 
             (id, card_id, grade, review_time, previous_ease_factor, previous_interval,
              previous_repetition, new_ease_factor, new_interval, new_repetition, created_at, synced)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)`,
            [
              review.id,
              review.card_id,
              review.grade,
              review.review_time,
              review.previous_srs.ease_factor,
              review.previous_srs.interval,
              review.previous_srs.repetition,
              review.new_srs.ease_factor,
              review.new_srs.interval,
              review.new_srs.repetition,
              review.created_at
            ]
          );
        }
      }
    });
  }

  private async pushChanges(): Promise<void> {
    if (this.syncQueue.length === 0) {
      return;
    }

    try {
      const response = await ApiService.syncPush(this.syncQueue);
      
      if (response.success) {
        // Clear successfully synced changes
        await this.clearSyncedChanges();
        this.syncQueue = [];
      }
    } catch (error) {
      console.error('Error pushing changes:', error);
      throw error;
    }
  }

  private async clearSyncedChanges(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql('DELETE FROM sync_queue');
  }

  private async saveLastSyncTime(timestamp: string): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql(
      'INSERT OR REPLACE INTO sync_metadata (key, value) VALUES (?, ?)',
      ['last_sync_time', timestamp]
    );

    // Also save to AsyncStorage as backup
    await AsyncStorage.setItem('last_sync_time', timestamp);
  }

  async loadLastSyncTime(): Promise<string | null> {
    try {
      // Try AsyncStorage first
      const stored = await AsyncStorage.getItem('last_sync_time');
      if (stored) {
        this.lastSyncTime = stored;
        return stored;
      }

      // Try database
      if (this.db) {
        const [results] = await this.db.executeSql(
          'SELECT value FROM sync_metadata WHERE key = ?',
          ['last_sync_time']
        );

        if (results.rows.length > 0) {
          const value = results.rows.item(0).value;
          this.lastSyncTime = value;
          return value;
        }
      }
    } catch (error) {
      console.error('Error loading last sync time:', error);
    }

    return null;
  }

  async getSyncStatus(): Promise<SyncStatus> {
    try {
      const response = await ApiService.getSyncStatus();
      return {
        unsynced_changes: response.unsynced_changes,
        last_sync: response.last_sync,
        device_id: response.device_id,
        recent_sessions: response.recent_sessions
      };
    } catch (error) {
      // Return local status if server unavailable
      const unsyncedCount = this.syncQueue.length;
      const lastSync = this.lastSyncTime;

      return {
        unsynced_changes: unsyncedCount,
        last_sync: lastSync,
        device_id: 'mobile-device',
        recent_sessions: []
      };
    }
  }

  async forceSync(): Promise<void> {
    try {
      await ApiService.forceSync();
      // After force sync, pull latest data
      await this.syncWithServer();
    } catch (error) {
      console.error('Force sync error:', error);
      throw error;
    }
  }

  setSyncState(state: SyncState): void {
    this.syncState = state;
    // Could emit events here for UI updates
  }

  getSyncState(): SyncState {
    return this.syncState;
  }

  getSyncQueueLength(): number {
    return this.syncQueue.length;
  }

  isReady(): boolean {
    return this.isInitialized;
  }

  async close(): Promise<void> {
    if (this.db) {
      await this.db.close();
      this.db = null;
      this.isInitialized = false;
    }
  }
}

export default new SyncService();