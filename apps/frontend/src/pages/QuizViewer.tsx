import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Card,
  CardBody,
  CardHeader,
  Text,
  Button,
  Progress,
  Heading,
  useColorModeValue,
  Badge,
  Radio,
  RadioGroup,
  Stack,
  useToast,
  Alert,
  AlertIcon,
  Spinner,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Divider,
} from '@chakra-ui/react';
import { useAppStore } from '../store/useAppStore';
import { QuizData, QuizQuestion } from '../types';
import { apiService } from '../services/api';

export const QuizViewer: React.FC = () => {
  const [quizzes, setQuizzes] = useState<QuizData[]>([]);
  const [currentQuiz, setCurrentQuiz] = useState<QuizData | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const toast = useToast();

  useEffect(() => {
    loadQuizzes();
  }, []);

  const loadQuizzes = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getQuizzes();
      if (response.success && response.data) {
        setQuizzes(response.data);
        if (response.data.length > 0) {
          setCurrentQuiz(response.data[0]);
        }
      }
    } catch (err) {
      setError('Failed to load quizzes');
      console.error('Quiz loading error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuizSelect = (quizId: string) => {
    const quiz = quizzes.find(q => q.id === quizId);
    if (quiz) {
      setCurrentQuiz(quiz);
      setCurrentQuestionIndex(0);
      setSelectedAnswers({});
      setShowResults(false);
      setScore(0);
    }
  };

  const handleAnswerSelect = (questionId: string, answer: string) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuiz && currentQuestionIndex < currentQuiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitQuiz = () => {
    if (!currentQuiz) return;

    let correctAnswers = 0;
    currentQuiz.questions.forEach(question => {
      const userAnswer = selectedAnswers[question.id];
      const correctAnswer = Array.isArray(question.correctAnswer) 
        ? question.correctAnswer.join(', ')
        : question.correctAnswer;
      
      if (userAnswer === correctAnswer) {
        correctAnswers++;
      }
    });

    setScore(correctAnswers);
    setShowResults(true);

    toast({
      title: 'Quiz Completed!',
      description: `You scored ${correctAnswers} out of ${currentQuiz.questions.length}`,
      status: 'success',
      duration: 3000,
    });
  };

  const handleResetQuiz = () => {
    setSelectedAnswers({});
    setShowResults(false);
    setScore(0);
    setCurrentQuestionIndex(0);
  };

  const currentQuestion = currentQuiz?.questions[currentQuestionIndex];
  const progress = currentQuiz 
    ? ((currentQuestionIndex + (showResults ? 1 : 0)) / currentQuiz.questions.length) * 100 
    : 0;

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" h="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {error}
        <Button ml={4} onClick={loadQuizzes}>Retry</Button>
      </Alert>
    );
  }

  if (quizzes.length === 0) {
    return (
      <VStack spacing={4} align="center" py={10}>
        <Heading size="lg" color="gray.500">
          No quizzes available
        </Heading>
        <Text color="gray.500">
          Create some quizzes to get started!
        </Text>
      </VStack>
    );
  }

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Quiz Viewer</Heading>
          <Text color="gray.600">Test your knowledge with interactive quizzes</Text>
        </Box>

        {/* Quiz Selection */}
        <Card bg={cardBg} border="1px" borderColor={cardBorder}>
          <CardHeader>
            <Heading size="md">Select Quiz</Heading>
          </CardHeader>
          <CardBody>
            <Tabs onChange={(index) => handleQuizSelect(quizzes[index].id)}>
              <TabList>
                {quizzes.map((quiz) => (
                  <Tab key={quiz.id}>{quiz.title}</Tab>
                ))}
              </TabList>
            </Tabs>
          </CardBody>
        </Card>

        {/* Current Quiz */}
        {currentQuiz && (
          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardHeader>
              <VStack align="start" spacing={2}>
                <Heading size="md">{currentQuiz.title}</Heading>
                <HStack>
                  <Badge colorScheme="blue">
                    {currentQuiz.questions.length} questions
                  </Badge>
                  <Badge colorScheme="green">
                    {currentQuiz.questions.filter(q => q.difficulty === 'easy').length} easy
                  </Badge>
                  <Badge colorScheme="orange">
                    {currentQuiz.questions.filter(q => q.difficulty === 'medium').length} medium
                  </Badge>
                  <Badge colorScheme="red">
                    {currentQuiz.questions.filter(q => q.difficulty === 'hard').length} hard
                  </Badge>
                </HStack>
              </VStack>
            </CardHeader>
            
            <CardBody>
              <VStack spacing={6} align="stretch">
                {/* Progress */}
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" color="gray.600">
                      Question {currentQuestionIndex + 1} of {currentQuiz.questions.length}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {Math.round(progress)}% complete
                    </Text>
                  </HStack>
                  <Progress 
                    value={progress} 
                    colorScheme="brand" 
                    size="lg" 
                    borderRadius="md"
                  />
                </Box>

                {/* Question */}
                {currentQuestion && !showResults && (
                  <Card 
                    bg={useColorModeValue('gray.50', 'gray.700')} 
                    p={6}
                    borderRadius="lg"
                  >
                    <VStack spacing={6} align="stretch">
                      <VStack align="start" spacing={3}>
                        <HStack>
                          <Badge 
                            colorScheme={
                              currentQuestion.difficulty === 'easy' ? 'green' :
                              currentQuestion.difficulty === 'medium' ? 'orange' : 'red'
                            }
                          >
                            {currentQuestion.difficulty}
                          </Badge>
                        </HStack>
                        <Text fontSize="lg" fontWeight="medium">
                          {currentQuestion.question}
                        </Text>
                      </VStack>

                      {currentQuestion.options && (
                        <RadioGroup
                          value={selectedAnswers[currentQuestion.id] || ''}
                          onChange={(value) => handleAnswerSelect(currentQuestion.id, value)}
                        >
                          <Stack spacing={3}>
                            {currentQuestion.options.map((option, index) => (
                              <Radio key={index} value={option}>
                                <Text>{option}</Text>
                              </Radio>
                            ))}
                          </Stack>
                        </RadioGroup>
                      )}

                      <HStack justify="space-between">
                        <Button
                          variant="outline"
                          onClick={handlePreviousQuestion}
                          isDisabled={currentQuestionIndex === 0}
                        >
                          Previous
                        </Button>
                        
                        {currentQuestionIndex === currentQuiz.questions.length - 1 ? (
                          <Button
                            colorScheme="brand"
                            onClick={handleSubmitQuiz}
                            isDisabled={Object.keys(selectedAnswers).length !== currentQuiz.questions.length}
                          >
                            Submit Quiz
                          </Button>
                        ) : (
                          <Button
                            colorScheme="brand"
                            onClick={handleNextQuestion}
                            isDisabled={!selectedAnswers[currentQuestion.id]}
                          >
                            Next Question
                          </Button>
                        )}
                      </HStack>
                    </VStack>
                  </Card>
                )}

                {/* Results */}
                {showResults && (
                  <Card 
                    bg={useColorModeValue('green.50', 'green.900')} 
                    p={6}
                    borderRadius="lg"
                    borderColor="green.200"
                  >
                    <VStack spacing={6} align="stretch">
                      <Box textAlign="center">
                        <Heading size="lg" color="green.600">
                          Quiz Results
                        </Heading>
                        <Text fontSize="2xl" fontWeight="bold" color="green.700">
                          {score} / {currentQuiz.questions.length}
                        </Text>
                        <Text color="green.600">
                          {Math.round((score / currentQuiz.questions.length) * 100)}% Correct
                        </Text>
                      </Box>

                      <Divider />

                      <VStack spacing={4} align="stretch">
                        {currentQuiz.questions.map((question, index) => {
                          const userAnswer = selectedAnswers[question.id];
                          const correctAnswer = Array.isArray(question.correctAnswer) 
                            ? question.correctAnswer.join(', ')
                            : question.correctAnswer;
                          const isCorrect = userAnswer === correctAnswer;

                          return (
                            <Card key={question.id} size="sm" p={4}>
                              <VStack align="start" spacing={3}>
                                <HStack>
                                  <Badge colorScheme={isCorrect ? 'green' : 'red'}>
                                    {isCorrect ? 'Correct' : 'Incorrect'}
                                  </Badge>
                                  <Text fontSize="sm" fontWeight="medium">
                                    Question {index + 1}
                                  </Text>
                                </HStack>
                                <Text>{question.question}</Text>
                                <Box>
                                  <Text fontSize="sm" color="gray.600">
                                    Your answer: <Text as="span" fontWeight="bold">{userAnswer || 'No answer'}</Text>
                                  </Text>
                                  {!isCorrect && (
                                    <Text fontSize="sm" color="green.600">
                                      Correct answer: <Text as="span" fontWeight="bold">{correctAnswer}</Text>
                                    </Text>
                                  )}
                                </Box>
                                {question.explanation && (
                                  <Text fontSize="sm" color="gray.600" fontStyle="italic">
                                    {question.explanation}
                                  </Text>
                                )}
                              </VStack>
                            </Card>
                          );
                        })}
                      </VStack>

                      <HStack justify="center">
                        <Button colorScheme="brand" onClick={handleResetQuiz}>
                          Retake Quiz
                        </Button>
                      </HStack>
                    </VStack>
                  </Card>
                )}
              </VStack>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  );
};
