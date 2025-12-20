import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useAppStore } from '../store';
import { Deck } from '../types';

export default function DecksScreen() {
  const { decks, isLoading, settings, loadDecks, startReviewSession } = useAppStore();

  useEffect(() => {
    loadDecks();
  }, []);

  const handleDeckPress = (deck: Deck) => {
    if (deck.dueCards > 0) {
      startReviewSession(deck.id);
    }
  };

  const renderDeck = ({ item }: { item: Deck }) => {
    const progress = item.totalCards > 0 ? item.reviewedToday / item.totalCards : 0;
    const progressPercentage = Math.round(progress * 100);

    return (
      <TouchableOpacity
        style={[styles.deckCard, settings.darkMode && styles.deckCardDark]}
        onPress={() => handleDeckPress(item)}
        disabled={item.dueCards === 0}
      >
        <View style={styles.deckHeader}>
          <View style={styles.deckInfo}>
            <Text style={[styles.deckName, settings.darkMode && styles.textDark]}>
              {item.name}
            </Text>
            {item.description && (
              <Text style={[styles.deckDescription, settings.darkMode && styles.textSecondaryDark]}>
                {item.description}
              </Text>
            )}
          </View>
          <View
            style={[
              styles.progressCircle,
              { borderColor: item.dueCards > 0 ? '#007AFF' : '#8E8E93' },
            ]}
          >
            <Text style={[styles.progressText, settings.darkMode && styles.textDark]}>
              {item.dueCards}
            </Text>
          </View>
        </View>

        <View style={styles.deckStats}>
          <View style={styles.statItem}>
            <Icon
              name="cards"
              size={20}
              color={settings.darkMode ? '#8E8E93' : '#8E8E93'}
            />
            <Text style={[styles.statText, settings.darkMode && styles.textSecondaryDark]}>
              {item.totalCards} cards
            </Text>
          </View>
          <View style={styles.statItem}>
            <Icon
              name="check-circle"
              size={20}
              color={settings.darkMode ? '#34C759' : '#34C759'}
            />
            <Text style={[styles.statText, settings.darkMode && styles.textSecondaryDark]}>
              {item.reviewedToday} today
            </Text>
          </View>
        </View>

        <View style={styles.progressBarContainer}>
          <View
            style={[
              styles.progressBar,
              { width: `${progressPercentage}%` },
            ]}
          />
        </View>
      </TouchableOpacity>
    );
  };

  if (isLoading) {
    return (
      <View style={[styles.container, settings.darkMode && styles.containerDark]}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (decks.length === 0) {
    return (
      <View style={[styles.container, settings.darkMode && styles.containerDark]}>
        <View style={styles.emptyContainer}>
          <Icon
            name="book-outline"
            size={80}
            color={settings.darkMode ? '#8E8E93' : '#8E8E93'}
          />
          <Text style={[styles.emptyTitle, settings.darkMode && styles.textDark]}>
            No Decks Yet
          </Text>
          <Text style={[styles.emptyText, settings.darkMode && styles.textSecondaryDark]}>
            Sync with your desktop app to see your decks here.
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={[styles.container, settings.darkMode && styles.containerDark]}>
      <FlatList
        data={decks}
        renderItem={renderDeck}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  containerDark: {
    backgroundColor: '#000000',
  },
  listContainer: {
    padding: 16,
  },
  deckCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  deckCardDark: {
    backgroundColor: '#1C1C1E',
  },
  deckHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  deckInfo: {
    flex: 1,
    marginRight: 16,
  },
  deckName: {
    fontSize: 20,
    fontWeight: '700',
    color: '#000000',
    marginBottom: 4,
  },
  deckDescription: {
    fontSize: 14,
    color: '#8E8E93',
    lineHeight: 20,
  },
  progressCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    borderWidth: 3,
    justifyContent: 'center',
    alignItems: 'center',
  },
  progressText: {
    fontSize: 20,
    fontWeight: '700',
    color: '#000000',
  },
  deckStats: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
  },
  statText: {
    fontSize: 14,
    color: '#8E8E93',
    marginLeft: 6,
  },
  progressBarContainer: {
    height: 6,
    backgroundColor: '#E5E5EA',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 3,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#000000',
    marginTop: 20,
    marginBottom: 12,
  },
  emptyText: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
  textDark: {
    color: '#FFFFFF',
  },
  textSecondaryDark: {
    color: '#8E8E93',
  },
});
