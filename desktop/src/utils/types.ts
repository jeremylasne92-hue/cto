export interface BackendResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface HardwareTier {
  name: 'Premium' | 'Standard' | 'Minimum';
  ramGB: number;
  hasGPU: boolean;
}

export interface ContentSource {
  id: string;
  name: string;
  type: 'pdf' | 'video' | 'article' | 'book';
  path: string;
  createdAt: string;
  updatedAt: string;
}

export interface Card {
  id: string;
  conceptId: string;
  question: string;
  answer: string;
  cardType: 'basic' | 'cloze' | 'image';
  createdAt: string;
}

export interface ReviewSession {
  cardId: string;
  quality: number;
  timestamp: string;
}
