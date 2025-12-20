// Mobile app entry point

import React, { useEffect, useState } from 'react';
import { View, Text, Button, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { Provider as PaperProvider } from 'react-native-paper';
import SyncService from '../services/syncService';
import ApiService from '../services/apiService';
import { Card, SyncState } from '../types';

const ReviewScreen: React.FC = () => {
  const [cards, setCards] = useState<Card[]>([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [syncState, setSyncState] = useState<SyncState>('idle');

  useEffect(() => {
    loadDueCards();
    checkSyncStatus();
  }, []);

  const loadDueCards = async () => {
    try {
      const dueCards = await SyncService.getDueCards();
      setCards(dueCards);
    } catch (error) {
      console.error('Error loading due cards:', error);
    }
  };

  const checkSyncStatus = async () => {
    try {
      setSyncState(SyncService.getSyncState());
      const status = await SyncService.getSyncStatus();
      console.log('Sync status:', status);
    } catch (error) {
      console.error('Error checking sync status:', error);
    }
  };

  const submitReview = async (grade: number) => {
    if (cards.length === 0 || currentCardIndex >= cards.length) return;

    try {
      const currentCard = cards[currentCardIndex];
      
      // Submit review to local database and queue for sync
      await SyncService.submitReview(currentCard.id, grade);
      
      // Move to next card
      setCurrentCardIndex(prev => prev + 1);
      setShowAnswer(false);

      // If we've reviewed all cards, reload
      if (currentCardIndex + 1 >= cards.length) {
        await loadDueCards();
        setCurrentCardIndex(0);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  const forceSync = async () => {
    try {
      setSyncState('syncing');
      await SyncService.syncWithServer();
      setSyncState('idle');
    } catch (error) {
      console.error('Sync error:', error);
      setSyncState('error');
    }
  };

  const getSyncStatusText = (state: SyncState): string => {
    switch (state) {
      case 'idle': return 'Synced ✓';
      case 'syncing': return 'Syncing...';
      case 'error': return 'Sync Error ❌';
      case 'offline': return 'Offline ⊘';
      case 'conflict': return 'Conflict ⚠️';
      default: return 'Unknown';
    }
  };

  const currentCard = cards[currentCardIndex];

  if (!currentCard) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>No cards due for review</Text>
        <SyncStatus />
        <Button title="Sync Now" onPress={forceSync} />
      </View>
    );
  }

  return (
    <PaperProvider>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Flashcards Review</Text>
          <SyncStatus />
        </View>

        <View style={styles.cardContainer}>
          <Text style={styles.cardText}>
            {showAnswer ? currentCard.answer : currentCard.question}
          </Text>
          
          {!showAnswer ? (
            <Button title="Show Answer" onPress={() => setShowAnswer(true)} />
          ) : (
            <View style={styles.gradesContainer}>
              <Text style={styles.gradesTitle}>How well did you recall?</Text>
              <View style={styles.gradesRow}>
                {[0, 1, 2, 3, 4, 5].map(grade => (
                  <TouchableOpacity
                    key={grade}
                    style={[styles.gradeButton, { backgroundColor: getGradeColor(grade) }]}
                    onPress={() => submitReview(grade)}
                  >
                    <Text style={styles.gradeText}>{grade}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          )}
        </View>

        <View style={styles.footer}>
          <Text style={styles.progress}>
            {currentCardIndex + 1} / {cards.length}
          </Text>
          <Button title="Manual Sync" onPress={forceSync} />
        </View>
      </View>
    </PaperProvider>
  );
};

const SyncStatus: React.FC = () => {
  const [status, setStatus] = useState<any>(null);
  const [syncState, setSyncState] = useState<SyncState>('idle');

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const syncStatus = await SyncService.getSyncStatus();
        setStatus(syncStatus);
        setSyncState(SyncService.getSyncState());
      } catch (error) {
        console.error('Error loading sync status:', error);
      }
    };

    loadStatus();
    const interval = setInterval(loadStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusText = (state: SyncState): string => {
    switch (state) {
      case 'idle': return 'Synced ✓';
      case 'syncing': return 'Syncing... 🔄';
      case 'error': return 'Sync Error ❌';
      case 'offline': return 'Offline ⊘';
      case 'conflict': return 'Conflict ⚠️';
      default: return 'Unknown';
    }
  };

  if (!status) {
    return <Text style={styles.syncStatus}>Loading...</Text>;
  }

  return (
    <View style={styles.syncStatusContainer}>
      <Text style={styles.syncStatus}>
        {getStatusText(syncState)}
      </Text>
      <Text style={styles.lastSync}>
        Last sync: {status.last_sync ? new Date(status.last_sync).toLocaleTimeString() : 'Never'}
      </Text>
      <Text style={styles.unsynced}>
        Pending: {status.unsynced_changes}
      </Text>
    </View>
  );
};

const getGradeColor = (grade: number): string => {
  const colors = ['#ff4444', '#ff8800', '#ffcc00', '#88cc00', '#00cc88', '#0088cc'];
  return colors[grade] || '#cccccc';
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  cardContainer: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginVertical: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  cardText: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 24,
  },
  gradesContainer: {
    marginTop: 20,
  },
  gradesTitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 15,
    color: '#666',
  },
  gradesRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
  },
  gradeButton: {
    padding: 12,
    borderRadius: 8,
    minWidth: 45,
    alignItems: 'center',
    marginVertical: 2,
  },
  gradeText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
  },
  progress: {
    fontSize: 16,
    color: '#666',
  },
  syncStatusContainer: {
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#e8f4fd',
    borderRadius: 8,
  },
  syncStatus: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1976d2',
  },
  lastSync: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  unsynced: {
    fontSize: 12,
    color: '#666',
  },
});

export default ReviewScreen;