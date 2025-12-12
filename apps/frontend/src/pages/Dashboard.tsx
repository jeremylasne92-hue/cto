import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  GridItem,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Progress,
  VStack,
  HStack,
  Button,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Badge,
} from '@chakra-ui/react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useAppStore } from '../store/useAppStore';
import { StudyStats } from '../types';
import { apiService } from '../services/api';

export const Dashboard: React.FC = () => {
  const { stats, setStats, decks, setDecks, loadDueCards, setCurrentView, setOnlineStatus } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadDashboardData();
    
    // Set up online/offline detection
    const handleOnline = () => setOnlineStatus(true);
    const handleOffline = () => setOnlineStatus(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate loading stats and decks (in real app, these would be API calls)
      const [statsResponse, decksResponse] = await Promise.all([
        apiService.getStats(),
        apiService.getDecks()
      ]);

      if (statsResponse.success && statsResponse.data) {
        setStats(statsResponse.data);
      }
      
      if (decksResponse.success && decksResponse.data) {
        setDecks(decksResponse.data);
      }
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard loading error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const mockStats: StudyStats = {
    totalCards: 1250,
    cardsDueToday: 45,
    cardsInQueue: 23,
    streakDays: 12,
    retentionPercentage: 87.5,
    averageInterval: 4.2,
    totalStudyTime: 2340, // 39 hours
    cardsReviewedToday: 32
  };

  const retentionData = [
    { day: 'Mon', retention: 85 },
    { day: 'Tue', retention: 88 },
    { day: 'Wed', retention: 82 },
    { day: 'Thu', retention: 90 },
    { day: 'Fri', retention: 87 },
    { day: 'Sat', retention: 92 },
    { day: 'Sun', retention: 89 }
  ];

  const deckDistribution = [
    { name: 'Spanish Vocabulary', value: 350, color: '#3182ce' },
    { name: 'Math Formulas', value: 280, color: '#38a169' },
    { name: 'History Dates', value: 190, color: '#d69e2e' },
    { name: 'Science Terms', value: 180, color: '#e53e3e' },
    { name: 'Literature', value: 150, color: '#805ad5' }
  ];

  const handleStartReview = () => {
    loadDueCards();
    setCurrentView('review');
    window.location.href = '/review';
  };

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
        <Button ml={4} onClick={loadDashboardData}>Retry</Button>
      </Alert>
    );
  }

  const displayStats = stats || mockStats;

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Study Dashboard</Heading>
          <Text color="gray.600">Track your learning progress and stay motivated</Text>
        </Box>

        {/* Key Stats Cards */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} gap={6}>
          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardBody>
              <Stat>
                <StatLabel>Cards Due Today</StatLabel>
                <StatNumber color="blue.500">{displayStats.cardsDueToday}</StatNumber>
                <StatHelpText>
                  <StatArrow type="decrease" />
                  3 from yesterday
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardBody>
              <Stat>
                <StatLabel>Current Streak</StatLabel>
                <StatNumber color="green.500">{displayStats.streakDays}</StatNumber>
                <StatHelpText>days</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardBody>
              <Stat>
                <StatLabel>Retention Rate</StatLabel>
                <StatNumber color="purple.500">{displayStats.retentionPercentage}%</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  2.1% from last week
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardBody>
              <Stat>
                <StatLabel>Total Study Time</StatLabel>
                <StatNumber color="orange.500">{Math.round(displayStats.totalStudyTime / 60)}h</StatNumber>
                <StatHelpText>{displayStats.totalStudyTime}m this week</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Progress Section */}
        <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardHeader>
              <Heading size="md">Today's Progress</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text>Cards Reviewed</Text>
                    <Text fontWeight="bold">{displayStats.cardsReviewedToday} / {displayStats.cardsDueToday}</Text>
                  </HStack>
                  <Progress 
                    value={(displayStats.cardsReviewedToday / displayStats.cardsDueToday) * 100} 
                    colorScheme="brand" 
                    size="lg" 
                    borderRadius="md"
                  />
                </Box>
                
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text>Time Spent</Text>
                    <Text fontWeight="bold">23 / 60 minutes</Text>
                  </HStack>
                  <Progress 
                    value={(23 / 60) * 100} 
                    colorScheme="green" 
                    size="lg" 
                    borderRadius="md"
                  />
                </Box>

                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text>Review Queue</Text>
                    <Badge colorScheme="orange">{displayStats.cardsInQueue} remaining</Badge>
                  </HStack>
                </Box>

                <Button 
                  colorScheme="brand" 
                  size="lg" 
                  onClick={handleStartReview}
                  isDisabled={displayStats.cardsDueToday === 0}
                >
                  Start Review Session
                </Button>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardHeader>
              <Heading size="md">Deck Distribution</Heading>
            </CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={deckDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {deckDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
        </Grid>

        {/* Charts Section */}
        <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={6}>
          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardHeader>
              <Heading size="md">Retention Rate (Last 7 Days)</Heading>
            </CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={retentionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis domain={[70, 100]} />
                  <Tooltip formatter={(value) => [`${value}%`, 'Retention']} />
                  <Line type="monotone" dataKey="retention" stroke="#3182ce" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>

          <Card bg={cardBg} border="1px" borderColor={cardBorder}>
            <CardHeader>
              <Heading size="md">Study Activity</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Text>This Week</Text>
                  <Text fontWeight="bold">156 cards</Text>
                </HStack>
                <HStack justify="space-between">
                  <Text>Last Week</Text>
                  <Text fontWeight="bold">142 cards</Text>
                </HStack>
                <HStack justify="space-between">
                  <Text>Average Daily</Text>
                  <Text fontWeight="bold">22 cards</Text>
                </HStack>
                <HStack justify="space-between">
                  <Text>Best Day</Text>
                  <Text fontWeight="bold">Sunday (34 cards)</Text>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Card bg={cardBg} border="1px" borderColor={cardBorder}>
          <CardHeader>
            <Heading size="md">Quick Actions</Heading>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
              <Button variant="outline" size="lg">
                Create New Deck
              </Button>
              <Button variant="outline" size="lg">
                Import Cards
              </Button>
              <Button variant="outline" size="lg">
                View Reports
              </Button>
            </Grid>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
};
