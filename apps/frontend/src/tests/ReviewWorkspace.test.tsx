import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChakraProvider } from '@chakra-ui/react';
import { ReviewWorkspace } from '../pages/ReviewWorkspace';
import { useAppStore } from '../store/useAppStore';
import { StudyCard } from '../types';

// Mock the store
jest.mock('../store/useAppStore', () => ({
  useAppStore: jest.fn()
}));

// Mock the API service
jest.mock('../services/api', () => ({
  apiService: {
    getNextCard: jest.fn(),
    submitFSRSResponse: jest.fn()
  }
}));

const mockStore = {
  studyQueue: [
    {
      id: '1',
      front: 'What is the Spanish word for "hello"?',
      back: 'Hola',
      deckId: '1',
      dueAt: new Date(),
      interval: 1,
      easeFactor: 2.5,
      repetitions: 3,
      lapses: 1,
      createdAt: new Date(),
      updatedAt: new Date()
    }
  ],
  currentCardIndex: 0,
  nextCard: jest.fn(),
  previousCard: jest.fn(),
  startSession: jest.fn(),
  endSession: jest.fn(),
  submitFSRSResponse: jest.fn(),
  currentDeck: { id: '1', name: 'Spanish', description: '', cardCount: 50, createdAt: new Date(), updatedAt: new Date() },
  darkMode: false,
  isOnline: true
};

const mockApiService = {
  getNextCard: jest.fn(),
  submitFSRSResponse: jest.fn()
};

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <ChakraProvider>
      {component}
    </ChakraProvider>
  );
};

describe('ReviewWorkspace', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useAppStore as jest.Mock).mockReturnValue(mockStore);
    
    // Mock API to return a card
    mockApiService.getNextCard.mockResolvedValue({
      success: true,
      data: mockStore.studyQueue[0]
    });
    
    mockApiService.submitFSRSResponse.mockResolvedValue({
      success: true,
      data: {}
    });
  });

  test('renders review workspace with card', async () => {
    renderWithProviders(<ReviewWorkspace />);
    
    // Wait for the card to load
    await waitFor(() => {
      expect(screen.getByText('What is the Spanish word for "hello"?')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Card 1 of 1')).toBeInTheDocument();
    expect(screen.getByText('Show Answer')).toBeInTheDocument();
  });

  test('shows answer when button is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ReviewWorkspace />);
    
    // Wait for the card to load
    await waitFor(() => {
      expect(screen.getByText('What is the Spanish word for "hello"?')).toBeInTheDocument();
    });
    
    // Click show answer button
    const showAnswerButton = screen.getByText('Show Answer');
    await user.click(showAnswerButton);
    
    // Verify answer is shown with rating buttons
    await waitFor(() => {
      expect(screen.getByText('A: Hola')).toBeInTheDocument();
      expect(screen.getByText('1. Again')).toBeInTheDocument();
      expect(screen.getByText('2. Hard')).toBeInTheDocument();
      expect(screen.getByText('3. Good')).toBeInTheDocument();
      expect(screen.getByText('4. Easy')).toBeInTheDocument();
    });
  });

  test('handles grading responses correctly', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ReviewWorkspace />);
    
    // Wait for the card to load
    await waitFor(() => {
      expect(screen.getByText('What is the Spanish word for "hello"?')).toBeInTheDocument();
    });
    
    // Show answer
    const showAnswerButton = screen.getByText('Show Answer');
    await user.click(showAnswerButton);
    
    // Click "Good" rating
    const goodButton = screen.getByText('3. Good');
    await user.click(goodButton);
    
    // Verify API calls were made
    await waitFor(() => {
      expect(mockApiService.submitFSRSResponse).toHaveBeenCalledWith({
        cardId: '1',
        rating: 'good',
        responseTime: expect.any(Number),
        timestamp: expect.any(Date),
        isCorrect: true
      });
      expect(mockStore.submitFSRSResponse).toHaveBeenCalled();
    });
  });

  test('handles keyboard shortcuts', async () => {
    const user = userEvent.setup();
    renderWithProviders(<ReviewWorkspace />);
    
    // Wait for the card to load
    await waitFor(() => {
      expect(screen.getByText('What is the Spanish word for "hello"?')).toBeInTheDocument();
    });
    
    // Press space to show answer
    fireEvent.keyDown(window, { key: ' ' });
    
    await waitFor(() => {
      expect(screen.getByText('A: Hola')).toBeInTheDocument();
    });
    
    // Press "3" for good rating
    fireEvent.keyDown(window, { key: '3' });
    
    await waitFor(() => {
      expect(mockApiService.submitFSRSResponse).toHaveBeenCalledWith({
        cardId: '1',
        rating: 'good',
        responseTime: expect.any(Number),
        timestamp: expect.any(Date),
        isCorrect: true
      });
    });
  });

  test('displays offline mode when not online', () => {
    (useAppStore as jest.Mock).mockReturnValue({
      ...mockStore,
      isOnline: false
    });
    
    renderWithProviders(<ReviewWorkspace />);
    
    expect(screen.getByText('Offline Mode')).toBeInTheDocument();
  });

  test('shows completion message when queue is empty', () => {
    (useAppStore as jest.Mock).mockReturnValue({
      ...mockStore,
      studyQueue: [],
      currentCardIndex: 0
    });
    
    renderWithProviders(<ReviewWorkspace />);
    
    expect(screen.getByText('No cards to review!')).toBeInTheDocument();
    expect(screen.getByText('All caught up. Great work!')).toBeInTheDocument();
    expect(screen.getByText('Session Complete')).toBeInTheDocument();
  });

  test('displays timer correctly', async () => {
    renderWithProviders(<ReviewWorkspace />);
    
    // Wait for the card to load
    await waitFor(() => {
      expect(screen.getByText('What is the Spanish word for "hello"?')).toBeInTheDocument();
    });
    
    // Timer should be visible (displaying 0 or elapsed time)
    expect(screen.getByText(/^\d+:\d+$/)).toBeInTheDocument();
  });
});
