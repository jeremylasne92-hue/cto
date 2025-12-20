import { SRSState } from '../types';

/**
 * SM-2 Algorithm Implementation
 * Calculates next review interval based on grade (1-4)
 */
export function calculateNextReview(
  currentState: SRSState,
  grade: 1 | 2 | 3 | 4
): SRSState {
  let { interval, easeFactor, repetitions, lapses } = currentState;

  // Grade 1 or 2: Failed recall
  if (grade < 3) {
    return {
      interval: 1, // Review again in 1 day
      easeFactor: Math.max(1.3, easeFactor - 0.2),
      repetitions: 0,
      lapses: lapses + 1,
      nextReview: new Date(Date.now() + 24 * 60 * 60 * 1000),
    };
  }

  // Grade 3 or 4: Successful recall
  repetitions += 1;

  // Adjust ease factor based on grade
  const easeAdjustment = grade === 4 ? 0.15 : 0.0;
  easeFactor = Math.max(1.3, easeFactor + easeAdjustment);

  // Calculate new interval
  if (repetitions === 1) {
    interval = 1;
  } else if (repetitions === 2) {
    interval = 6;
  } else {
    interval = Math.round(interval * easeFactor);
  }

  const nextReview = new Date(Date.now() + interval * 24 * 60 * 60 * 1000);

  return {
    interval,
    easeFactor,
    repetitions,
    lapses,
    nextReview,
  };
}

export function isDueForReview(card: { nextReview: Date }): boolean {
  return new Date(card.nextReview) <= new Date();
}

export function calculateRetentionRate(
  reviews: Array<{ grade: number }>
): number {
  if (reviews.length === 0) return 0;
  const successfulReviews = reviews.filter((r) => r.grade >= 3).length;
  return (successfulReviews / reviews.length) * 100;
}

export function calculateXP(grade: 1 | 2 | 3 | 4): number {
  const xpMap = {
    1: 0,
    2: 5,
    3: 10,
    4: 15,
  };
  return xpMap[grade];
}

export function calculateLevel(xp: number): number {
  return Math.floor(xp / 100) + 1;
}
