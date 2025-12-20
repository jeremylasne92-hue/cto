import { calculateNextReview, isDueForReview, calculateRetentionRate, calculateXP, calculateLevel } from '../utils/srs';
import { SRSState } from '../types';

describe('SRS Algorithm', () => {
  describe('calculateNextReview', () => {
    it('should reset interval on failed recall (grade 1)', () => {
      const currentState: SRSState = {
        interval: 10,
        easeFactor: 2.5,
        repetitions: 3,
        lapses: 0,
        nextReview: new Date(),
      };

      const result = calculateNextReview(currentState, 1);

      expect(result.interval).toBe(1);
      expect(result.repetitions).toBe(0);
      expect(result.lapses).toBe(1);
      expect(result.easeFactor).toBeLessThan(2.5);
    });

    it('should reset interval on hard recall (grade 2)', () => {
      const currentState: SRSState = {
        interval: 10,
        easeFactor: 2.5,
        repetitions: 3,
        lapses: 0,
        nextReview: new Date(),
      };

      const result = calculateNextReview(currentState, 2);

      expect(result.interval).toBe(1);
      expect(result.repetitions).toBe(0);
      expect(result.lapses).toBe(1);
    });

    it('should increase interval on good recall (grade 3)', () => {
      const currentState: SRSState = {
        interval: 6,
        easeFactor: 2.5,
        repetitions: 2,
        lapses: 0,
        nextReview: new Date(),
      };

      const result = calculateNextReview(currentState, 3);

      expect(result.interval).toBeGreaterThan(6);
      expect(result.repetitions).toBe(3);
      expect(result.lapses).toBe(0);
    });

    it('should increase interval and ease factor on easy recall (grade 4)', () => {
      const currentState: SRSState = {
        interval: 6,
        easeFactor: 2.5,
        repetitions: 2,
        lapses: 0,
        nextReview: new Date(),
      };

      const result = calculateNextReview(currentState, 4);

      expect(result.interval).toBeGreaterThan(6);
      expect(result.easeFactor).toBeGreaterThan(2.5);
      expect(result.repetitions).toBe(3);
    });

    it('should follow SM-2 interval progression', () => {
      let state: SRSState = {
        interval: 0,
        easeFactor: 2.5,
        repetitions: 0,
        lapses: 0,
        nextReview: new Date(),
      };

      // First review - should be 1 day
      state = calculateNextReview(state, 3);
      expect(state.interval).toBe(1);
      expect(state.repetitions).toBe(1);

      // Second review - should be 6 days
      state = calculateNextReview(state, 3);
      expect(state.interval).toBe(6);
      expect(state.repetitions).toBe(2);

      // Third review - should multiply by ease factor
      state = calculateNextReview(state, 3);
      expect(state.interval).toBe(15); // 6 * 2.5 = 15
      expect(state.repetitions).toBe(3);
    });

    it('should not let ease factor drop below 1.3', () => {
      let state: SRSState = {
        interval: 1,
        easeFactor: 1.3,
        repetitions: 1,
        lapses: 5,
        nextReview: new Date(),
      };

      state = calculateNextReview(state, 1);
      expect(state.easeFactor).toBe(1.3);
    });
  });

  describe('isDueForReview', () => {
    it('should return true for cards due in the past', () => {
      const card = {
        nextReview: new Date(Date.now() - 24 * 60 * 60 * 1000),
      };

      expect(isDueForReview(card)).toBe(true);
    });

    it('should return true for cards due now', () => {
      const card = {
        nextReview: new Date(),
      };

      expect(isDueForReview(card)).toBe(true);
    });

    it('should return false for cards due in the future', () => {
      const card = {
        nextReview: new Date(Date.now() + 24 * 60 * 60 * 1000),
      };

      expect(isDueForReview(card)).toBe(false);
    });
  });

  describe('calculateRetentionRate', () => {
    it('should return 0 for empty review list', () => {
      expect(calculateRetentionRate([])).toBe(0);
    });

    it('should calculate correct retention rate', () => {
      const reviews = [
        { grade: 4 },
        { grade: 3 },
        { grade: 2 },
        { grade: 1 },
        { grade: 3 },
      ];

      const rate = calculateRetentionRate(reviews);
      expect(rate).toBe(60); // 3 out of 5 = 60%
    });

    it('should return 100 for all successful reviews', () => {
      const reviews = [
        { grade: 4 },
        { grade: 3 },
        { grade: 4 },
      ];

      expect(calculateRetentionRate(reviews)).toBe(100);
    });

    it('should return 0 for all failed reviews', () => {
      const reviews = [
        { grade: 1 },
        { grade: 2 },
        { grade: 1 },
      ];

      expect(calculateRetentionRate(reviews)).toBe(0);
    });
  });

  describe('calculateXP', () => {
    it('should return 0 XP for grade 1', () => {
      expect(calculateXP(1)).toBe(0);
    });

    it('should return 5 XP for grade 2', () => {
      expect(calculateXP(2)).toBe(5);
    });

    it('should return 10 XP for grade 3', () => {
      expect(calculateXP(3)).toBe(10);
    });

    it('should return 15 XP for grade 4', () => {
      expect(calculateXP(4)).toBe(15);
    });
  });

  describe('calculateLevel', () => {
    it('should return level 1 for 0 XP', () => {
      expect(calculateLevel(0)).toBe(1);
    });

    it('should return level 1 for 99 XP', () => {
      expect(calculateLevel(99)).toBe(1);
    });

    it('should return level 2 for 100 XP', () => {
      expect(calculateLevel(100)).toBe(2);
    });

    it('should return level 3 for 250 XP', () => {
      expect(calculateLevel(250)).toBe(3);
    });

    it('should return correct level for high XP', () => {
      expect(calculateLevel(1000)).toBe(11);
    });
  });
});
