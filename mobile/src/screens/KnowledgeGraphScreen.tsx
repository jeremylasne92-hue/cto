import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { apiClient } from '../services/api';

interface Concept {
  id: string;
  name: string;
  description: string;
  mastery: number;
  review_count: number;
  color: string;
}

interface Neighbor {
  id: string;
  name: string;
  description: string;
  mastery: number;
  color: string;
}

const KnowledgeGraphScreen: React.FC = () => {
  const navigation = useNavigation();
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);
  const [neighbors, setNeighbors] = useState<Neighbor[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  useEffect(() => {
    loadConcepts();
  }, []);
  
  const loadConcepts = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/concepts');
      if (response.data.concepts) {
        setConcepts(response.data.concepts);
      }
    } catch (error) {
      console.error('Failed to load concepts:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  const loadNeighbors = async (conceptId: string) => {
    try {
      const response = await apiClient.post('/api/knowledge-graph/related', {
        concept_id: conceptId,
        max_depth: 1,
      });
      
      if (response.data.direct_neighbors) {
        setNeighbors(response.data.direct_neighbors);
      }
    } catch (error) {
      console.error('Failed to load neighbors:', error);
    }
  };
  
  const handleConceptPress = async (concept: Concept) => {
    setSelectedConcept(concept);
    await loadNeighbors(concept.id);
  };
  
  const getMasteryLabel = (mastery: number): string => {
    if (mastery > 80) return 'Mastered';
    if (mastery >= 50) return 'Learning';
    if (mastery >= 20) return 'Beginner';
    return 'Not Started';
  };
  
  const filteredConcepts = concepts.filter(concept =>
    concept.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    concept.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const renderConcept = ({ item }: { item: Concept }) => (
    <TouchableOpacity
      style={[
        styles.conceptCard,
        selectedConcept?.id === item.id && styles.conceptCardSelected,
      ]}
      onPress={() => handleConceptPress(item)}
    >
      <View style={styles.conceptHeader}>
        <View style={styles.conceptTitleRow}>
          <View style={[styles.colorDot, { backgroundColor: item.color }]} />
          <Text style={styles.conceptName}>{item.name}</Text>
        </View>
        <Text style={styles.masteryLabel}>{getMasteryLabel(item.mastery || 0)}</Text>
      </View>
      
      {item.description && (
        <Text style={styles.conceptDescription} numberOfLines={2}>
          {item.description}
        </Text>
      )}
      
      <View style={styles.conceptStats}>
        <Text style={styles.statText}>Mastery: {Math.round(item.mastery || 0)}%</Text>
        <Text style={styles.statText}>Reviews: {item.review_count || 0}</Text>
      </View>
      
      <View style={styles.masteryBar}>
        <View
          style={[
            styles.masteryFill,
            { width: `${item.mastery || 0}%`, backgroundColor: item.color },
          ]}
        />
      </View>
    </TouchableOpacity>
  );
  
  const renderNeighbor = ({ item }: { item: Neighbor }) => (
    <View style={styles.neighborCard}>
      <View style={styles.neighborHeader}>
        <View style={[styles.colorDot, { backgroundColor: item.color }]} />
        <Text style={styles.neighborName}>{item.name}</Text>
      </View>
      {item.description && (
        <Text style={styles.neighborDescription} numberOfLines={2}>
          {item.description}
        </Text>
      )}
      <Text style={styles.neighborMastery}>
        {getMasteryLabel(item.mastery || 0)} - {Math.round(item.mastery || 0)}%
      </Text>
    </View>
  );
  
  if (loading && concepts.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Loading knowledge graph...</Text>
      </View>
    );
  }
  
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Knowledge Graph</Text>
        <Text style={styles.headerSubtitle}>Read-only view</Text>
      </View>
      
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search concepts..."
          placeholderTextColor="#999"
          value={searchTerm}
          onChangeText={setSearchTerm}
        />
      </View>
      
      {selectedConcept && neighbors.length > 0 && (
        <View style={styles.neighborsSection}>
          <View style={styles.neighborsSectionHeader}>
            <Text style={styles.neighborsSectionTitle}>
              Connected to "{selectedConcept.name}"
            </Text>
            <TouchableOpacity onPress={() => setSelectedConcept(null)}>
              <Text style={styles.closeButton}>✕</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            horizontal
            data={neighbors}
            renderItem={renderNeighbor}
            keyExtractor={(item) => item.id}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.neighborsList}
          />
        </View>
      )}
      
      <FlatList
        data={filteredConcepts}
        renderItem={renderConcept}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.conceptsList}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => {
              setRefreshing(true);
              loadConcepts();
            }}
            tintColor="#3b82f6"
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No concepts found</Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1e1e1e',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1e1e1e',
  },
  loadingText: {
    marginTop: 16,
    color: '#e0e0e0',
    fontSize: 16,
  },
  header: {
    padding: 20,
    backgroundColor: '#252525',
    borderBottomWidth: 1,
    borderBottomColor: '#404040',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#e0e0e0',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#b0b0b0',
  },
  searchContainer: {
    padding: 16,
    backgroundColor: '#252525',
  },
  searchInput: {
    backgroundColor: '#1e1e1e',
    borderWidth: 1,
    borderColor: '#404040',
    borderRadius: 8,
    padding: 12,
    color: '#e0e0e0',
    fontSize: 16,
  },
  conceptsList: {
    padding: 16,
  },
  conceptCard: {
    backgroundColor: '#2d2d2d',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#404040',
  },
  conceptCardSelected: {
    borderColor: '#3b82f6',
    borderWidth: 2,
  },
  conceptHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  conceptTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  colorDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  conceptName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#e0e0e0',
    flex: 1,
  },
  masteryLabel: {
    fontSize: 12,
    color: '#b0b0b0',
    textTransform: 'uppercase',
  },
  conceptDescription: {
    fontSize: 14,
    color: '#b0b0b0',
    marginBottom: 12,
    lineHeight: 20,
  },
  conceptStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statText: {
    fontSize: 12,
    color: '#b0b0b0',
  },
  masteryBar: {
    height: 6,
    backgroundColor: '#404040',
    borderRadius: 3,
    overflow: 'hidden',
  },
  masteryFill: {
    height: '100%',
  },
  neighborsSection: {
    backgroundColor: '#252525',
    borderBottomWidth: 1,
    borderBottomColor: '#404040',
    paddingVertical: 12,
  },
  neighborsSectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  neighborsSectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#e0e0e0',
    flex: 1,
  },
  closeButton: {
    fontSize: 20,
    color: '#b0b0b0',
    paddingHorizontal: 8,
  },
  neighborsList: {
    paddingHorizontal: 16,
  },
  neighborCard: {
    backgroundColor: '#1e1e1e',
    borderRadius: 8,
    padding: 12,
    marginRight: 12,
    width: 200,
    borderWidth: 1,
    borderColor: '#404040',
  },
  neighborHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  neighborName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#e0e0e0',
    flex: 1,
  },
  neighborDescription: {
    fontSize: 12,
    color: '#b0b0b0',
    marginBottom: 6,
    lineHeight: 16,
  },
  neighborMastery: {
    fontSize: 11,
    color: '#b0b0b0',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#b0b0b0',
  },
});

export default KnowledgeGraphScreen;
