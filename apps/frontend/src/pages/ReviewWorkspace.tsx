import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Card,
  CardBody,
  Text,
  Button,
  Progress,
  Heading,
  useColorModeValue,
  Badge,
  Flex,
  IconButton,
  useToast,
  Alert,
  AlertIcon,
  Spinner,
} from '@chakra-ui/react';
import { FiSkipBack, FiSkipForward, FiRotateCcw } from 'react-icons/fi';
import { useAppStore } from '../store/useAppStore';
import { Card as StudyCard, FSRSResponse } from '../types';
import { apiService } from '../services/api';

export const ReviewWorkspace: React.FC = () => {
  const {
    studyQueue,
    currentCardIndex,
    nextCard,
    previousCard,
    startSession,
    endSession,
    submitFSRSResponse,
    currentDeck,
    darkMode,
    isOnline
  } = useAppStore();

  const [currentCard, setCurrentCard] = useState<StudyCard | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [responseTime, setResponseTime] = useState(0);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const toast = useToast();

  // Timer for response time
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (currentCard && !showAnswer) {
      setSessionStartTime(new Date());
      interval = setInterval(() => {
        setResponseTime(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [currentCard, showAnswer]);

  // Load initial card
  useEffect(() => {
    loadNextCard();
    startSession();
  }, []);

  const loadNextCard = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Try to get next card from backend
      const response = await apiService.getNextCard(currentDeck?.id);
      if (response.success && response.data) {
        setCurrentCard(response.data);
        setShowAnswer(false);
        setResponseTime(0);
      } else {
        // Fallback to local queue
        if (currentCardIndex < studyQueue.length) {
          setCurrentCard(studyQueue[currentCardIndex]);
          setShowAnswer(false);
          setResponseTime(0);
        } else {
          setCurrentCard(null);
          setShowAnswer(false);
        }
      }
    } catch (err) {
      console.error('Failed to load card:', err);
      setError('Failed to load card. Using local data.');
      
      // Fallback to local queue
      if (currentCardIndex < studyQueue.length) {
        setCurrentCard(studyQueue[currentCardIndex]);
        setShowAnswer(false);
        setResponseTime(0);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
  };

  const handleRating = async (rating: 'again' | 'hard' | 'good' | 'easy') => {
    if (!currentCard) return;

    const fsrsResponse: FSRSResponse = {
      cardId: currentCard.id,
      rating,
      responseTime,
      timestamp: new Date(),
      isCorrect: rating !== 'again'
    };

    try {
      // Submit to backend
      await apiService.submitFSRSResponse(fsrsResponse);
      
      // Update local state
      submitFSRSResponse(fsrsResponse);
      
      // Show feedback
      const feedbackMessages = {
        again: 'Card will be shown again soon',
        hard: 'Card difficulty increased',
        good: 'Good response!',
        easy: 'Card will be shown less frequently'
      };
      
      toast({
        title: 'Response Recorded',
        description: feedbackMessages[rating],
        status: 'success',
        duration: 2000,
      });

      // Move to next card
      nextCard();
      
      if (currentCardIndex + 1 >= studyQueue.length) {
        // End session
        endSession();
        toast({
          title: 'Session Complete!',
          description: 'Great job reviewing your cards!',
          status: 'success',
          duration: 3000,
        });
      }
      
      // Load next card
      setTimeout(loadNextCard, 500);
      
    } catch (error) {
      console.error('Failed to submit response:', error);
      toast({
        title: 'Error',
        description: 'Failed to record response. It will be saved locally.',
        status: 'warning',
        duration: 3000,
      });
      
      // Still move to next card for offline mode
      nextCard();
      setTimeout(loadNextCard, 500);
    }
  };

  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    if (!currentCard || showAnswer) return;

    switch (event.key) {
      case ' ':
      case 'Enter':
        event.preventDefault();
        handleShowAnswer();
        break;
      case '1':
        event.preventDefault();
        handleRating('again');
        break;
      case '2':
        event.preventDefault();
        handleRating('hard');
        break;
      case '3':
        event.preventDefault();
        handleRating('good');
        break;
      case '4':
        event.preventDefault();
        handleRating('easy');
        break;
    }
  }, [currentCard, showAnswer]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleKeyPress]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading && !currentCard) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" h="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (studyQueue.length === 0 && !currentCard) {
    return (
      <VStack spacing={4} align="center" py={10}>
        <Heading size="lg" color="gray.500">
          No cards to review!
        </Heading>
        <Text color="gray.500">
          All caught up. Great work!
        </Text>
        <Badge colorScheme="green" fontSize="lg" p={2}>
          Session Complete
        </Badge>
      </VStack>
    );
  }

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Session Header */}
        <Flex justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="md">
              {currentDeck ? `Reviewing: ${currentDeck.name}` : 'Review Session'}
            </Heading>
            <Text fontSize="sm" color="gray.500">
              Card {currentCardIndex + 1} of {studyQueue.length}
            </Text>
          </VStack>
          
          <HStack spacing={4}>
            <Badge colorScheme={isOnline ? 'green' : 'orange'} fontSize="sm">
              {isOnline ? 'Online' : 'Offline Mode'}
            </Badge>
            <Badge colorScheme="blue" fontSize="sm">
              {formatTime(responseTime)}
            </Badge>
          </HStack>
        </Flex>

        {/* Progress Bar */}
        <Progress 
          value={((currentCardIndex + (showAnswer ? 1 : 0)) / studyQueue.length) * 100} 
          colorScheme="brand" 
          size="lg" 
          borderRadius="md"
        />

        {/* Error Alert */}
        {error && (
          <Alert status="warning">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {/* Card Display */}
        {currentCard && (
          <Card 
            bg={cardBg} 
            border="2px" 
            borderColor={showAnswer ? 'green.300' : cardBorder}
            minH="400px"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <CardBody textAlign="center" w="full">
              {!showAnswer ? (
                <VStack spacing={6}>
                  <Text fontSize="lg" fontWeight="medium" mb={4}>
                    {currentCard.front}
                  </Text>
                  <Button 
                    size="lg" 
                    colorScheme="brand" 
                    onClick={handleShowAnswer}
                    minW="200px"
                  >
                    Show Answer
                  </Button>
                  <Text fontSize="sm" color="gray.500">
                    Press Space or Enter to show answer
                  </Text>
                </VStack>
              ) : (
                <VStack spacing={6}>
                  <VStack spacing={3}>
                    <Text fontSize="lg" fontWeight="medium" color="gray.600">
                      Q: {currentCard.front}
                    </Text>
                    <Text fontSize="xl" fontWeight="bold" color="green.600">
                      A: {currentCard.back}
                    </Text>
                  </VStack>
                  
                  <Text fontSize="sm" color="gray.500" mb={4}>
                    How did you do?
                  </Text>
                  
                  <HStack spacing={4} flexWrap="wrap" justify="center">
                    <Button
                      size="lg"
                      colorScheme="red"
                      variant="outline"
                      onClick={() => handleRating('again')}
                      leftIcon={<FiRotateCcw />}
                    >
                      1. Again
                    </Button>
                    <Button
                      size="lg"
                      colorScheme="orange"
                      variant="outline"
                      onClick={() => handleRating('hard')}
                    >
                      2. Hard
                    </Button>
                    <Button
                      size="lg"
                      colorScheme="green"
                      variant="outline"
                      onClick={() => handleRating('good')}
                    >
                      3. Good
                    </Button>
                    <Button
                      size="lg"
                      colorScheme="blue"
                      variant="outline"
                      onClick={() => handleRating('easy')}
                    >
                      4. Easy
                    </Button>
                  </HStack>
                  
                  <Text fontSize="sm" color="gray.500">
                    Use keyboard shortcuts: 1-Again, 2-Hard, 3-Good, 4-Easy
                  </Text>
                </VStack>
              )}
            </CardBody>
          </Card>
        )}

        {/* Navigation */}
        <HStack justify="space-between">
          <IconButton
            aria-label="Previous card"
            icon={<FiSkipBack />}
            onClick={previousCard}
            isDisabled={currentCardIndex === 0}
            size="lg"
          />
          
          <Text fontSize="sm" color="gray.500">
            {studyQueue.length - currentCardIndex - 1} cards remaining
          </Text>
          
          <IconButton
            aria-label="Skip card"
            icon={<FiSkipForward />}
            onClick={nextCard}
            isDisabled={currentCardIndex >= studyQueue.length - 1}
            size="lg"
            variant="outline"
          />
        </HStack>
      </VStack>
    </Box>
  );
};
