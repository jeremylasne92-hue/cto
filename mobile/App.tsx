// Main App component for React Native flashcard sync app

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Provider as PaperProvider, Button, Card as PaperCard } from 'react-native-paper';
import SyncService from '../services/syncService';
import ApiService from '../services/apiService';
import { Deck, Card, SyncState } from '../types';

const App: React.FC = () => {
  const [screen, setScreen] = useState<'login' | 'decks' | 'review'>('login');
  const [user, setUser] = useState<any>(null);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [dueCardsCount, setDueCardsCount] = useState(0);
  const [syncState, setSyncState] = useState<SyncState>('idle');

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check if user is already logged in
      const token = await ApiService.getToken();
      if (token) {
        setUser({ email: 'demo@example.com' }); // Simplified for demo
        setScreen('decks');
        loadDecks();
        loadDueCardsCount();
      }
    } catch (error) {
      console.error('App initialization error:', error);
    }
  };

  const handleLogin = async () => {
    try {
      // For demo purposes, use the default account
      const response = await ApiService.login('demo@example.com', 'demo123');
      
      if (response.success) {
        setUser(response.user);
        setScreen('decks');
        await loadDecks();
        await loadDueCardsCount();
      } else {
        console.error('Login failed:', response.error);
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  const loadDecks = async () => {
    try {
      const data = await ApiService.getDecks();
      setDecks(data.decks || []);
    } catch (error) {
      console.error('Error loading decks:', error);
    }
  };

  const loadDueCardsCount = async () => {
    try {
      const dueCards = await SyncService.getDueCards();
      setDueCardsCount(dueCards.length);
    } catch (error) {
      console.error('Error loading due cards count:', error);
    }
  };

  const syncData = async () => {
    try {
      setSyncState('syncing');
      await SyncService.syncWithServer();
      setSyncState('idle');
      await loadDecks();
      await loadDueCardsCount();
    } catch (error) {
      console.error('Sync error:', error);
      setSyncState('error');
    }
  };

  const logout = async () => {
    await ApiService.logout();
    setUser(null);
    setScreen('login');
  };

  const renderLoginScreen = () => (
    <View style={styles.centerContainer}>
      <PaperCard style={styles.card}>
        <PaperCard.Title title="Flashcard Sync" subtitle="Multi-Device Learning" />
        <PaperCard.Content>
          <Text style={styles.description}>
            Synchronize your flashcards between desktop and mobile devices.
          </Text>
        </PaperCard.Content>
        <PaperCard.Actions>
          <Button mode="contained" onPress={handleLogin}>
            Demo Login
          </Button>
        </PaperCard.Actions>
      </PaperCard>
    </View>
  );

  const renderDecksScreen = () => (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Your Decks</Text>
        <TouchableOpacity 
          style={[styles.syncButton, getSyncButtonStyle(syncState)]} 
          onPress={syncData}
          disabled={syncState === 'syncing'}
        >
          <Text style={styles.syncButtonText}>
            {getSyncStateText(syncState)}
          </Text>
        </TouchableOpacity>
      </View>

      {decks.map(deck => (
        <TouchableOpacity key={deck.id} style={styles.deckItem}>
          <View style={styles.deckContent}>
            <Text style={styles.deckName}>{deck.name}</Text>
            <Text style={styles.deckDescription}>{deck.description || 'No description'}</Text>
            <Text style={styles.deckMeta}>
              {deck.card_count} cards • Updated {new Date(deck.updated_at).toLocaleDateString()}
            </Text>
          </View>
          <Button 
            title="Review" 
            onPress={() => setScreen('review')} 
            mode="outlined"
          />
        </TouchableOpacity>
      ))}

      <View style={styles.statsContainer}>
        <Text style={styles.statsText}>
          Due for review: {dueCardsCount} cards
        </Text>
      </View>

      <View style={styles.actions}>
        <Button mode="contained" onPress={() => setScreen('review')}>
          Start Review Session
        </Button>
        <Button mode="outlined" onPress={logout}>
          Logout
        </Button>
      </View>
    </ScrollView>
  );

  const getSyncStateText = (state: SyncState): string => {
    switch (state) {
      case 'idle': return '✓ Synced';
      case 'syncing': return '🔄 Syncing...';
      case 'error': return '❌ Error';
      case 'offline': return '⊘ Offline';
      case 'conflict': return '⚠️ Conflict';
      default: return 'Unknown';
    }
  };

  const getSyncButtonStyle = (state: SyncState) => {
    switch (state) {
      case 'idle': return { backgroundColor: '#4caf50' };
      case 'syncing': return { backgroundColor: '#2196f3' };
      case 'error': return { backgroundColor: '#f44336' };
      case 'offline': return { backgroundColor: '#ff9800' };
      case 'conflict': return { backgroundColor: '#ff5722' };
      default: return { backgroundColor: '#9e9e9e' };
    }
  };

  if (screen === 'login') {
    return (
      <PaperProvider>
        {renderLoginScreen()}
      </PaperProvider>
    );
  }

  if (screen === 'review') {
    const ReviewScreen = require('./ReviewScreen').default;
    return <ReviewScreen />;
  }

  return (
    <PaperProvider>
      {renderDecksScreen()}
    </PaperProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  card: {
    width: '100%',
    maxWidth: 400,
    elevation: 4,
  },
  description: {
    fontSize: 16,
    textAlign: 'center',
    color: '#666',
    lineHeight: 24,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  syncButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  syncButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '500',
  },
  deckItem: {
    backgroundColor: 'white',
    marginHorizontal: 16,
    marginVertical: 8,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.22,
    shadowRadius: 2.22,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deckContent: {
    flex: 1,
    marginRight: 16,
  },
  deckName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  deckDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  deckMeta: {
    fontSize: 12,
    color: '#999',
  },
  statsContainer: {
    margin: 16,
    padding: 12,
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
  },
  statsText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1976d2',
    textAlign: 'center',
  },
  actions: {
    padding: 16,
    gap: 12,
  },
});

export default App;