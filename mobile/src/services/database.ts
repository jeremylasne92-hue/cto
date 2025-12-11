import SQLite, { SQLiteDatabase } from 'react-native-sqlite-storage';
import { Card, Deck, ReviewGrade, Concept, UserStats } from '../types';

SQLite.enablePromise(true);

class DatabaseService {
  private db: SQLiteDatabase | null = null;

  async init(): Promise<void> {
    try {
      this.db = await SQLite.openDatabase({
        name: 'srs_mobile.db',
        location: 'default',
      });

      await this.createTables();
    } catch (error) {
      console.error('Database initialization error:', error);
      throw error;
    }
  }

  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const tables = [
      `CREATE TABLE IF NOT EXISTS decks (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        totalCards INTEGER DEFAULT 0,
        dueCards INTEGER DEFAULT 0,
        reviewedToday INTEGER DEFAULT 0,
        createdAt TEXT,
        updatedAt TEXT
      )`,
      `CREATE TABLE IF NOT EXISTS cards (
        id TEXT PRIMARY KEY,
        deckId TEXT NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        conceptId TEXT,
        lastReviewed TEXT,
        nextReview TEXT NOT NULL,
        interval INTEGER DEFAULT 0,
        easeFactor REAL DEFAULT 2.5,
        repetitions INTEGER DEFAULT 0,
        lapses INTEGER DEFAULT 0,
        FOREIGN KEY (deckId) REFERENCES decks(id)
      )`,
      `CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cardId TEXT NOT NULL,
        grade INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        duration INTEGER NOT NULL,
        synced INTEGER DEFAULT 0,
        FOREIGN KEY (cardId) REFERENCES cards(id)
      )`,
      `CREATE TABLE IF NOT EXISTS concepts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        mastery REAL DEFAULT 0,
        cardCount INTEGER DEFAULT 0,
        relatedConcepts TEXT,
        positionX REAL,
        positionY REAL
      )`,
      `CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        totalCardsReviewed INTEGER DEFAULT 0,
        currentStreak INTEGER DEFAULT 0,
        longestStreak INTEGER DEFAULT 0,
        streakFreezeCount INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        lastReviewDate TEXT
      )`,
      `CREATE INDEX IF NOT EXISTS idx_cards_nextReview ON cards(nextReview)`,
      `CREATE INDEX IF NOT EXISTS idx_cards_deckId ON cards(deckId)`,
      `CREATE INDEX IF NOT EXISTS idx_reviews_synced ON reviews(synced)`,
    ];

    for (const sql of tables) {
      await this.db.executeSql(sql);
    }
  }

  // Deck operations
  async getAllDecks(): Promise<Deck[]> {
    if (!this.db) throw new Error('Database not initialized');

    const [results] = await this.db.executeSql('SELECT * FROM decks ORDER BY name');
    const decks: Deck[] = [];

    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i);
      decks.push({
        id: row.id,
        name: row.name,
        description: row.description,
        totalCards: row.totalCards,
        dueCards: row.dueCards,
        reviewedToday: row.reviewedToday,
        createdAt: new Date(row.createdAt),
        updatedAt: new Date(row.updatedAt),
      });
    }

    return decks;
  }

  async saveDeck(deck: Deck): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql(
      `INSERT OR REPLACE INTO decks (id, name, description, totalCards, dueCards, reviewedToday, createdAt, updatedAt)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        deck.id,
        deck.name,
        deck.description || '',
        deck.totalCards,
        deck.dueCards,
        deck.reviewedToday,
        deck.createdAt.toISOString(),
        deck.updatedAt.toISOString(),
      ]
    );
  }

  // Card operations
  async getDueCards(limit?: number): Promise<Card[]> {
    if (!this.db) throw new Error('Database not initialized');

    const now = new Date().toISOString();
    const sql = limit
      ? `SELECT * FROM cards WHERE nextReview <= ? ORDER BY nextReview LIMIT ?`
      : `SELECT * FROM cards WHERE nextReview <= ? ORDER BY nextReview`;
    const params = limit ? [now, limit] : [now];

    const [results] = await this.db.executeSql(sql, params);
    return this.mapCardsFromResults(results);
  }

  async getCardsByDeck(deckId: string): Promise<Card[]> {
    if (!this.db) throw new Error('Database not initialized');

    const [results] = await this.db.executeSql(
      'SELECT * FROM cards WHERE deckId = ?',
      [deckId]
    );
    return this.mapCardsFromResults(results);
  }

  async saveCard(card: Card): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql(
      `INSERT OR REPLACE INTO cards (id, deckId, front, back, conceptId, lastReviewed, nextReview, interval, easeFactor, repetitions, lapses)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        card.id,
        card.deckId,
        card.front,
        card.back,
        card.conceptId || null,
        card.lastReviewed?.toISOString() || null,
        card.nextReview.toISOString(),
        card.interval,
        card.easeFactor,
        card.repetitions,
        card.lapses,
      ]
    );
  }

  async updateCard(card: Card): Promise<void> {
    await this.saveCard(card);
  }

  // Review operations
  async saveReview(review: ReviewGrade): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql(
      `INSERT INTO reviews (cardId, grade, timestamp, duration, synced)
       VALUES (?, ?, ?, ?, 0)`,
      [review.cardId, review.grade, review.timestamp.toISOString(), review.duration]
    );
  }

  async getUnsyncedReviews(): Promise<ReviewGrade[]> {
    if (!this.db) throw new Error('Database not initialized');

    const [results] = await this.db.executeSql(
      'SELECT * FROM reviews WHERE synced = 0 ORDER BY timestamp'
    );

    const reviews: ReviewGrade[] = [];
    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i);
      reviews.push({
        cardId: row.cardId,
        grade: row.grade,
        timestamp: new Date(row.timestamp),
        duration: row.duration,
      });
    }

    return reviews;
  }

  async markReviewsSynced(cardIds: string[]): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    if (cardIds.length === 0) return;

    const placeholders = cardIds.map(() => '?').join(',');
    await this.db.executeSql(
      `UPDATE reviews SET synced = 1 WHERE cardId IN (${placeholders})`,
      cardIds
    );
  }

  // Concept operations
  async getAllConcepts(): Promise<Concept[]> {
    if (!this.db) throw new Error('Database not initialized');

    const [results] = await this.db.executeSql('SELECT * FROM concepts');
    const concepts: Concept[] = [];

    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i);
      concepts.push({
        id: row.id,
        name: row.name,
        mastery: row.mastery,
        cardCount: row.cardCount,
        relatedConcepts: row.relatedConcepts ? JSON.parse(row.relatedConcepts) : [],
        position:
          row.positionX !== null && row.positionY !== null
            ? { x: row.positionX, y: row.positionY }
            : undefined,
      });
    }

    return concepts;
  }

  async saveConcept(concept: Concept): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql(
      `INSERT OR REPLACE INTO concepts (id, name, mastery, cardCount, relatedConcepts, positionX, positionY)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        concept.id,
        concept.name,
        concept.mastery,
        concept.cardCount,
        JSON.stringify(concept.relatedConcepts),
        concept.position?.x || null,
        concept.position?.y || null,
      ]
    );
  }

  // User stats operations
  async getUserStats(): Promise<UserStats | null> {
    if (!this.db) throw new Error('Database not initialized');

    const [results] = await this.db.executeSql('SELECT * FROM user_stats WHERE id = 1');

    if (results.rows.length === 0) return null;

    const row = results.rows.item(0);
    const reviewHistory = await this.getReviewHistory(30);

    return {
      totalCardsReviewed: row.totalCardsReviewed,
      currentStreak: row.currentStreak,
      longestStreak: row.longestStreak,
      streakFreezeCount: row.streakFreezeCount,
      xp: row.xp,
      level: row.level,
      retentionRate: await this.calculateRetentionRate(),
      reviewHistory,
    };
  }

  async updateUserStats(stats: Partial<UserStats>): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    const fields: string[] = [];
    const values: any[] = [];

    if (stats.totalCardsReviewed !== undefined) {
      fields.push('totalCardsReviewed = ?');
      values.push(stats.totalCardsReviewed);
    }
    if (stats.currentStreak !== undefined) {
      fields.push('currentStreak = ?');
      values.push(stats.currentStreak);
    }
    if (stats.longestStreak !== undefined) {
      fields.push('longestStreak = ?');
      values.push(stats.longestStreak);
    }
    if (stats.streakFreezeCount !== undefined) {
      fields.push('streakFreezeCount = ?');
      values.push(stats.streakFreezeCount);
    }
    if (stats.xp !== undefined) {
      fields.push('xp = ?');
      values.push(stats.xp);
    }
    if (stats.level !== undefined) {
      fields.push('level = ?');
      values.push(stats.level);
    }

    if (fields.length === 0) return;

    await this.db.executeSql(
      `INSERT OR REPLACE INTO user_stats (id, ${fields.map((f) => f.split(' = ')[0]).join(', ')})
       VALUES (1, ${values.map(() => '?').join(', ')})`,
      values
    );
  }

  private async getReviewHistory(
    days: number
  ): Promise<Array<{ date: string; reviewed: number; correct: number }>> {
    if (!this.db) throw new Error('Database not initialized');

    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const [results] = await this.db.executeSql(
      `SELECT DATE(timestamp) as date, COUNT(*) as reviewed, SUM(CASE WHEN grade >= 3 THEN 1 ELSE 0 END) as correct
       FROM reviews
       WHERE timestamp >= ?
       GROUP BY DATE(timestamp)
       ORDER BY date`,
      [startDate.toISOString()]
    );

    const history: Array<{ date: string; reviewed: number; correct: number }> = [];
    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i);
      history.push({
        date: row.date,
        reviewed: row.reviewed,
        correct: row.correct,
      });
    }

    return history;
  }

  private async calculateRetentionRate(): Promise<number> {
    if (!this.db) throw new Error('Database not initialized');

    const [results] = await this.db.executeSql(
      `SELECT COUNT(*) as total, SUM(CASE WHEN grade >= 3 THEN 1 ELSE 0 END) as correct
       FROM reviews`
    );

    if (results.rows.length === 0) return 0;

    const row = results.rows.item(0);
    if (row.total === 0) return 0;

    return (row.correct / row.total) * 100;
  }

  private mapCardsFromResults(results: any): Card[] {
    const cards: Card[] = [];
    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i);
      cards.push({
        id: row.id,
        deckId: row.deckId,
        front: row.front,
        back: row.back,
        conceptId: row.conceptId,
        lastReviewed: row.lastReviewed ? new Date(row.lastReviewed) : undefined,
        nextReview: new Date(row.nextReview),
        interval: row.interval,
        easeFactor: row.easeFactor,
        repetitions: row.repetitions,
        lapses: row.lapses,
      });
    }
    return cards;
  }

  async clearAllData(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    await this.db.executeSql('DELETE FROM reviews');
    await this.db.executeSql('DELETE FROM cards');
    await this.db.executeSql('DELETE FROM decks');
    await this.db.executeSql('DELETE FROM concepts');
    await this.db.executeSql('DELETE FROM user_stats');
  }
}

export default new DatabaseService();
