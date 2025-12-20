"""
Mobile Knowledge Graph Screen - Read-only visualization for mobile devices
"""
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Dimensions
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';

interface MobileKnowledgeGraphScreenProps {}

interface ConceptNode {
  id: number;
  name: string;
  description: string;
  content: string;
  mastery: number;
  color: 'green' | 'yellow' | 'orange' | 'gray';
  prerequisites?: number[];
  dependencies?: number[];
}

interface NeighborConcept {
  concept_id: number;
  name: string;
  description: string;
  similarity_score: number;
}

interface RouteParams {
  conceptId: number;
  conceptName: string;
}

const { width: screenWidth } = Dimensions.get('window');

const KnowledgeGraphScreen: React.FC<MobileKnowledgeGraphScreenProps> = () => {
  const navigation = useNavigation();
  const route = useRoute<RouteProp<{ params: RouteParams }, 'params'>>();
  
  const { conceptId, conceptName } = route.params;

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [concept, setConcept] = useState<ConceptNode | null>(null);
  const [neighbors, setNeighbors] = useState<NeighborConcept[]>([]);
  const [activeTab, setActiveTab] = useState<'neighbors' | 'details'>('neighbors');

  useEffect(() => {
    loadConceptData();
  }, [conceptId]);

  const loadConceptData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // In a real implementation, this would call the backend API
      // For now, we'll simulate the data structure
      const mockConcept: ConceptNode = {
        id: conceptId,
        name: conceptName,
        description: `Description for ${conceptName}`,
        content: `Content for ${conceptName}`,
        mastery: 75,
        color: 'yellow',
        prerequisites: [1, 2, 3],
        dependencies: [4, 5]
      };

      const mockNeighbors: NeighborConcept[] = [
        {
          concept_id: 6,
          name: 'Related Concept A',
          description: 'A related concept in the knowledge graph',
          similarity_score: 0.85
        },
        {
          concept_id: 7,
          name: 'Related Concept B',
          description: 'Another related concept',
          similarity_score: 0.72
        },
        {
          concept_id: 8,
          name: 'Related Concept C',
          description: 'A third related concept',
          similarity_score: 0.68
        }
      ];

      setConcept(mockConcept);
      setNeighbors(mockNeighbors);
    } catch (err) {
      setError('Failed to load concept data');
      console.error('Error loading concept:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getMasteryColor = (color: string) => {
    switch (color) {
      case 'green': return '#10B981';
      case 'yellow': return '#F59E0B';
      case 'orange': return '#F97316';
      case 'gray': return '#6B7280';
      default: return '#6B7280';
    }
  };

  const getMasteryLabel = (mastery: number) => {
    if (mastery >= 80) return 'Mastered';
    if (mastery >= 50) return 'Learning';
    if (mastery >= 20) return 'Struggling';
    return 'Not Started';
  };

  const renderMasteryIndicator = (mastery: number, color: string) => {
    const colorHex = getMasteryColor(color);
    
    return (
      <View style={styles.masteryContainer}>
        <View style={styles.masteryHeader}>
          <Text style={styles.masteryLabel}>Mastery Level</Text>
          <Text style={[styles.masteryValue, { color: colorHex }]}>
            {mastery.toFixed(1)}%
          </Text>
        </View>
        
        <View style={styles.masteryBar}>
          <View 
            style={[
              styles.masteryProgress, 
              { 
                width: `${mastery}%`, 
                backgroundColor: colorHex 
              }
            ]} 
          />
        </View>
        
        <Text style={[styles.masteryStatus, { color: colorHex }]}>
          {getMasteryLabel(mastery)}
        </Text>
      </View>
    );
  };

  const renderNeighborCard = (neighbor: NeighborConcept) => {
    return (
      <TouchableOpacity
        key={neighbor.concept_id}
        style={styles.neighborCard}
        onPress={() => {
          // Navigate to the concept detail
          navigation.navigate('KnowledgeGraph', {
            screen: 'KnowledgeGraphScreen',
            params: {
              conceptId: neighbor.concept_id,
              conceptName: neighbor.name
            }
          });
        }}
      >
        <View style={styles.neighborHeader}>
          <Text style={styles.neighborName}>{neighbor.name}</Text>
          <View style={styles.similarityBadge}>
            <Text style={styles.similarityText}>
              {(neighbor.similarity_score * 100).toFixed(0)}%
            </Text>
          </View>
        </View>
        
        <Text style={styles.neighborDescription} numberOfLines={2}>
          {neighbor.description}
        </Text>
        
        <View style={styles.neighborActions}>
          <Text style={styles.viewConceptText}>View Concept</Text>
        </View>
      </TouchableOpacity>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>Loading knowledge graph...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadConceptData}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        
        <Text style={styles.headerTitle} numberOfLines={1}>
          {concept?.name || 'Concept'}
        </Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[
            styles.tab,
            activeTab === 'neighbors' && styles.activeTab
          ]}
          onPress={() => setActiveTab('neighbors')}
        >
          <Text style={[
            styles.tabText,
            activeTab === 'neighbors' && styles.activeTabText
          ]}>
            Neighbors ({neighbors.length})
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[
            styles.tab,
            activeTab === 'details' && styles.activeTab
          ]}
          onPress={() => setActiveTab('details')}
        >
          <Text style={[
            styles.tabText,
            activeTab === 'details' && styles.activeTabText
          ]}>
            Details
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {concept && renderMasteryIndicator(concept.mastery, concept.color)}

        {activeTab === 'neighbors' ? (
          <View style={styles.neighborsSection}>
            <Text style={styles.sectionTitle}>Related Concepts</Text>
            
            {neighbors.length > 0 ? (
              neighbors.map(renderNeighborCard)
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>
                  No related concepts found
                </Text>
              </View>
            )}
          </View>
        ) : (
          <View style={styles.detailsSection}>
            <Text style={styles.sectionTitle}>Concept Details</Text>
            
            <View style={styles.detailCard}>
              <Text style={styles.detailLabel}>Description</Text>
              <Text style={styles.detailValue}>
                {concept?.description || 'No description available'}
              </Text>
            </View>
            
            <View style={styles.detailCard}>
              <Text style={styles.detailLabel}>Content</Text>
              <Text style={styles.detailValue}>
                {concept?.content || 'No content available'}
              </Text>
            </View>
            
            {concept?.prerequisites && concept.prerequisites.length > 0 && (
              <View style={styles.detailCard}>
                <Text style={styles.detailLabel}>Prerequisites</Text>
                <Text style={styles.detailValue}>
                  {concept.prerequisites.length} concept(s) required
                </Text>
              </View>
            )}
            
            {concept?.dependencies && concept.dependencies.length > 0 && (
              <View style={styles.detailCard}>
                <Text style={styles.detailLabel}>Dependencies</Text>
                <Text style={styles.detailValue}>
                  {concept.dependencies.length} concept(s) depend on this
                </Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      {/* Color Legend */}
      <View style={styles.legend}>
        <Text style={styles.legendTitle}>Mastery Levels</Text>
        <View style={styles.legendItems}>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#10B981' }]} />
            <Text style={styles.legendText}>Mastered (80%+)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#F59E0B' }]} />
            <Text style={styles.legendText}>Learning (50-80%)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#F97316' }]} />
            <Text style={styles.legendText}>Struggling (20-50%)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#6B7280' }]} />
            <Text style={styles.legendText}>Not Started (<20%)</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    paddingVertical: 8,
    paddingRight: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '500',
  },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginLeft: 8,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#3B82F6',
  },
  tabText: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  activeTabText: {
    color: '#3B82F6',
  },
  content: {
    flex: 1,
  },
  masteryContainer: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  masteryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  masteryLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  masteryValue: {
    fontSize: 18,
    fontWeight: '700',
  },
  masteryBar: {
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    marginBottom: 8,
  },
  masteryProgress: {
    height: '100%',
    borderRadius: 4,
  },
  masteryStatus: {
    fontSize: 14,
    fontWeight: '500',
  },
  neighborsSection: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  neighborCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  neighborHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  neighborName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
  },
  similarityBadge: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  similarityText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6B7280',
  },
  neighborDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 12,
  },
  neighborActions: {
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    paddingTop: 12,
  },
  viewConceptText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '500',
  },
  detailsSection: {
    padding: 16,
  },
  detailCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  detailLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  emptyState: {
    backgroundColor: '#FFFFFF',
    padding: 32,
    borderRadius: 8,
    alignItems: 'center',
  },
  emptyStateText: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  legend: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  legendTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  legendItems: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
    marginBottom: 4,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 6,
  },
  legendText: {
    fontSize: 12,
    color: '#6B7280',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    padding: 32,
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 6,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '500',
  },
});

export default KnowledgeGraphScreen;