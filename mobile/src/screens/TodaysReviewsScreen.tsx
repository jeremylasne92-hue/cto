import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { GestureHandlerRootView, PanGestureHandler } from 'react-native-gesture-handler';
import { useAppStore } from '../store';

const { width, height } = Dimensions.get('window');
const SWIPE_THRESHOLD = 120;

export default function TodaysReviewsScreen() {
  const {
    dueCards,
    currentSession,
    userStats,
    settings,
    startReviewSession,
    gradeCard,
    endReviewSession,
    loadDueCards,
  } = useAppStore();

  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [sessionSummary, setSessionSummary] = useState<{
    cardsReviewed: number;
    avgGrade: number;
  } | null>(null);

  const translateX = new Animated.Value(0);
  const translateY = new Animated.Value(0);

  useEffect(() => {
    loadDueCards();
  }, []);

  useEffect(() => {
    if (dueCards.length > 0 && !currentSession) {
      startReviewSession();
      setStartTime(Date.now());
    }
  }, [dueCards.length]);

  const currentCard = dueCards[currentCardIndex];

  const handleGrade = async (grade: 1 | 2 | 3 | 4) => {
    if (!currentCard) return;

    const duration = Date.now() - startTime;
    await gradeCard(currentCard.id, grade, duration);

    setShowAnswer(false);
    setStartTime(Date.now());

    if (currentCardIndex >= dueCards.length - 1) {
      // Session complete
      if (currentSession) {
        const summary = {
          cardsReviewed: currentSession.cardsReviewed + 1,
          avgGrade:
            currentSession.grades.reduce((sum, r) => sum + r.grade, 0) /
            (currentSession.grades.length + 1),
        };
        setSessionSummary(summary);
        endReviewSession();
      }
    } else {
      setCurrentCardIndex(currentCardIndex + 1);
    }
  };

  const onSwipe = (event: any) => {
    const { translationX, translationY } = event.nativeEvent;

    if (Math.abs(translationX) > SWIPE_THRESHOLD) {
      if (translationX > 0) {
        // Swipe right - grade 4 (easy)
        handleGrade(4);
      } else {
        // Swipe left - grade 1 (again)
        handleGrade(1);
      }
      Animated.spring(translateX, {
        toValue: 0,
        useNativeDriver: true,
      }).start();
    } else if (translationY < -SWIPE_THRESHOLD) {
      // Swipe up - grade 3 (good)
      handleGrade(3);
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
      }).start();
    } else if (translationY > SWIPE_THRESHOLD) {
      // Swipe down - grade 2 (hard)
      handleGrade(2);
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
      }).start();
    }
  };

  const isDarkMode = settings.darkMode;
  const styles = getStyles(isDarkMode);

  if (sessionSummary) {
    return (
      <View style={styles.container}>
        <View style={styles.summaryContainer}>
          <Text style={styles.summaryTitle}>Session Complete! 🎉</Text>
          <Text style={styles.summaryText}>
            Cards Reviewed: {sessionSummary.cardsReviewed}
          </Text>
          <Text style={styles.summaryText}>
            Average Grade: {sessionSummary.avgGrade.toFixed(1)}
          </Text>
          {userStats && (
            <>
              <Text style={styles.summaryText}>
                Current Streak: {userStats.currentStreak} days 🔥
              </Text>
              <Text style={styles.summaryText}>Level: {userStats.level}</Text>
              <Text style={styles.summaryText}>XP: {userStats.xp}</Text>
            </>
          )}
          <TouchableOpacity
            style={styles.doneButton}
            onPress={() => {
              setSessionSummary(null);
              setCurrentCardIndex(0);
              loadDueCards();
            }}
          >
            <Text style={styles.doneButtonText}>Done</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  if (dueCards.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyTitle}>All Caught Up! ✨</Text>
          <Text style={styles.emptyText}>No cards due for review right now.</Text>
          {userStats && (
            <View style={styles.statsPreview}>
              <Text style={styles.statsText}>
                Current Streak: {userStats.currentStreak} days 🔥
              </Text>
              <Text style={styles.statsText}>Level: {userStats.level}</Text>
            </View>
          )}
        </View>
      </View>
    );
  }

  if (!currentCard) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <GestureHandlerRootView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.counter}>
          {currentCardIndex + 1} / {dueCards.length}
        </Text>
        {userStats && (
          <Text style={styles.streak}>🔥 {userStats.currentStreak} day streak</Text>
        )}
      </View>

      <PanGestureHandler onGestureEvent={onSwipe}>
        <Animated.View
          style={[
            styles.card,
            {
              transform: [{ translateX }, { translateY }],
            },
          ]}
        >
          <TouchableOpacity
            style={styles.cardContent}
            onPress={() => setShowAnswer(!showAnswer)}
            activeOpacity={0.9}
          >
            <Text style={styles.cardLabel}>
              {showAnswer ? 'Answer' : 'Question'}
            </Text>
            <Text style={styles.cardText}>
              {showAnswer ? currentCard.back : currentCard.front}
            </Text>
            {!showAnswer && (
              <Text style={styles.tapHint}>Tap to reveal answer</Text>
            )}
          </TouchableOpacity>
        </Animated.View>
      </PanGestureHandler>

      {showAnswer && (
        <View style={styles.buttonsContainer}>
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[styles.gradeButton, styles.gradeButton1]}
              onPress={() => handleGrade(1)}
            >
              <Text style={styles.gradeButtonText}>Again</Text>
              <Text style={styles.gradeButtonSubtext}>{'<1d'}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.gradeButton, styles.gradeButton2]}
              onPress={() => handleGrade(2)}
            >
              <Text style={styles.gradeButtonText}>Hard</Text>
              <Text style={styles.gradeButtonSubtext}>{'<6d'}</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[styles.gradeButton, styles.gradeButton3]}
              onPress={() => handleGrade(3)}
            >
              <Text style={styles.gradeButtonText}>Good</Text>
              <Text style={styles.gradeButtonSubtext}>Variable</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.gradeButton, styles.gradeButton4]}
              onPress={() => handleGrade(4)}
            >
              <Text style={styles.gradeButtonText}>Easy</Text>
              <Text style={styles.gradeButtonSubtext}>Variable+</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {!showAnswer && (
        <View style={styles.swipeHints}>
          <Text style={styles.swipeHintText}>← Again</Text>
          <Text style={styles.swipeHintText}>Easy →</Text>
        </View>
      )}
    </GestureHandlerRootView>
  );
}

function getStyles(isDarkMode: boolean) {
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDarkMode ? '#000000' : '#F2F2F7',
      justifyContent: 'center',
      alignItems: 'center',
    },
    header: {
      position: 'absolute',
      top: 20,
      left: 20,
      right: 20,
      flexDirection: 'row',
      justifyContent: 'space-between',
      zIndex: 10,
    },
    counter: {
      fontSize: 18,
      fontWeight: '600',
      color: isDarkMode ? '#FFFFFF' : '#000000',
    },
    streak: {
      fontSize: 16,
      fontWeight: '600',
      color: isDarkMode ? '#FFFFFF' : '#000000',
    },
    card: {
      width: width - 40,
      height: height * 0.6,
      backgroundColor: isDarkMode ? '#1C1C1E' : '#FFFFFF',
      borderRadius: 20,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 10,
      elevation: 5,
    },
    cardContent: {
      flex: 1,
      padding: 30,
      justifyContent: 'center',
      alignItems: 'center',
    },
    cardLabel: {
      fontSize: 14,
      fontWeight: '600',
      color: '#007AFF',
      marginBottom: 20,
      textTransform: 'uppercase',
    },
    cardText: {
      fontSize: 24,
      fontWeight: '500',
      color: isDarkMode ? '#FFFFFF' : '#000000',
      textAlign: 'center',
      lineHeight: 36,
    },
    tapHint: {
      position: 'absolute',
      bottom: 30,
      fontSize: 14,
      color: '#8E8E93',
    },
    buttonsContainer: {
      position: 'absolute',
      bottom: 40,
      width: width - 40,
    },
    buttonRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: 12,
    },
    gradeButton: {
      flex: 1,
      padding: 16,
      borderRadius: 12,
      marginHorizontal: 6,
      alignItems: 'center',
    },
    gradeButton1: {
      backgroundColor: '#FF3B30',
    },
    gradeButton2: {
      backgroundColor: '#FF9500',
    },
    gradeButton3: {
      backgroundColor: '#34C759',
    },
    gradeButton4: {
      backgroundColor: '#007AFF',
    },
    gradeButtonText: {
      fontSize: 16,
      fontWeight: '600',
      color: '#FFFFFF',
      marginBottom: 4,
    },
    gradeButtonSubtext: {
      fontSize: 12,
      color: '#FFFFFF',
      opacity: 0.8,
    },
    swipeHints: {
      position: 'absolute',
      bottom: 40,
      flexDirection: 'row',
      justifyContent: 'space-between',
      width: width - 80,
    },
    swipeHintText: {
      fontSize: 14,
      color: '#8E8E93',
    },
    emptyContainer: {
      alignItems: 'center',
      paddingHorizontal: 40,
    },
    emptyTitle: {
      fontSize: 28,
      fontWeight: '700',
      color: isDarkMode ? '#FFFFFF' : '#000000',
      marginBottom: 12,
      textAlign: 'center',
    },
    emptyText: {
      fontSize: 16,
      color: isDarkMode ? '#8E8E93' : '#8E8E93',
      textAlign: 'center',
      marginBottom: 30,
    },
    statsPreview: {
      alignItems: 'center',
    },
    statsText: {
      fontSize: 16,
      color: isDarkMode ? '#FFFFFF' : '#000000',
      marginBottom: 8,
    },
    summaryContainer: {
      alignItems: 'center',
      paddingHorizontal: 40,
    },
    summaryTitle: {
      fontSize: 32,
      fontWeight: '700',
      color: isDarkMode ? '#FFFFFF' : '#000000',
      marginBottom: 30,
      textAlign: 'center',
    },
    summaryText: {
      fontSize: 18,
      color: isDarkMode ? '#FFFFFF' : '#000000',
      marginBottom: 12,
    },
    doneButton: {
      marginTop: 30,
      backgroundColor: '#007AFF',
      paddingHorizontal: 50,
      paddingVertical: 16,
      borderRadius: 12,
    },
    doneButtonText: {
      fontSize: 18,
      fontWeight: '600',
      color: '#FFFFFF',
    },
  });
}
