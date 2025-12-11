import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import Svg, { Circle, Line, Text as SvgText } from 'react-native-svg';
import { useAppStore } from '../store';
import { Concept } from '../types';

const { width, height } = Dimensions.get('window');
const GRAPH_WIDTH = width - 40;
const GRAPH_HEIGHT = height * 0.6;

export default function GraphScreen() {
  const { concepts, settings, loadConcepts, isLoading } = useAppStore();
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);

  useEffect(() => {
    loadConcepts();
  }, []);

  const isDarkMode = settings.darkMode;

  if (isLoading) {
    return (
      <View style={[styles.container, isDarkMode && styles.containerDark]}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (concepts.length === 0) {
    return (
      <View style={[styles.container, isDarkMode && styles.containerDark]}>
        <View style={styles.emptyContainer}>
          <Text style={[styles.emptyTitle, isDarkMode && styles.textDark]}>
            No Concepts Yet
          </Text>
          <Text style={[styles.emptyText, isDarkMode && styles.textSecondaryDark]}>
            Your knowledge graph will appear here once you have concepts with cards.
          </Text>
        </View>
      </View>
    );
  }

  // Calculate positions if not set
  const conceptsWithPositions = concepts.map((concept, index) => {
    if (concept.position) return concept;

    const angle = (index / concepts.length) * 2 * Math.PI;
    const radius = Math.min(GRAPH_WIDTH, GRAPH_HEIGHT) * 0.35;
    const centerX = GRAPH_WIDTH / 2;
    const centerY = GRAPH_HEIGHT / 2;

    return {
      ...concept,
      position: {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      },
    };
  });

  const getConceptColor = (mastery: number): string => {
    if (mastery >= 80) return '#34C759'; // Green
    if (mastery >= 50) return '#FFD60A'; // Yellow
    if (mastery >= 20) return '#FF9500'; // Orange
    return '#8E8E93'; // Gray
  };

  const renderGraph = () => {
    return (
      <Svg width={GRAPH_WIDTH} height={GRAPH_HEIGHT}>
        {conceptsWithPositions.map((concept) =>
          concept.relatedConcepts.map((relatedId) => {
            const relatedConcept = conceptsWithPositions.find((c) => c.id === relatedId);
            if (!relatedConcept || !concept.position || !relatedConcept.position) return null;

            return (
              <Line
                key={`${concept.id}-${relatedId}`}
                x1={concept.position.x}
                y1={concept.position.y}
                x2={relatedConcept.position.x}
                y2={relatedConcept.position.y}
                stroke={isDarkMode ? '#38383A' : '#E5E5EA'}
                strokeWidth="2"
              />
            );
          })
        )}

        {conceptsWithPositions.map((concept) => {
          if (!concept.position) return null;

          const color = getConceptColor(concept.mastery);
          const isSelected = selectedConcept?.id === concept.id;
          const radius = isSelected ? 30 : 20;

          return (
            <React.Fragment key={concept.id}>
              <Circle
                cx={concept.position.x}
                cy={concept.position.y}
                r={radius}
                fill={color}
                opacity={0.8}
                onPress={() => setSelectedConcept(concept)}
              />
              <SvgText
                x={concept.position.x}
                y={concept.position.y + radius + 15}
                fontSize="12"
                fill={isDarkMode ? '#FFFFFF' : '#000000'}
                textAnchor="middle"
                fontWeight={isSelected ? 'bold' : 'normal'}
              >
                {concept.name.length > 10
                  ? concept.name.substring(0, 10) + '...'
                  : concept.name}
              </SvgText>
            </React.Fragment>
          );
        })}
      </Svg>
    );
  };

  return (
    <ScrollView
      style={[styles.container, isDarkMode && styles.containerDark]}
      contentContainerStyle={styles.scrollContent}
    >
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#34C759' }]} />
          <Text style={[styles.legendText, isDarkMode && styles.textSecondaryDark]}>
            {'>'}80% Mastery
          </Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#FFD60A' }]} />
          <Text style={[styles.legendText, isDarkMode && styles.textSecondaryDark]}>
            50-80%
          </Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#FF9500' }]} />
          <Text style={[styles.legendText, isDarkMode && styles.textSecondaryDark]}>
            20-50%
          </Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendColor, { backgroundColor: '#8E8E93' }]} />
          <Text style={[styles.legendText, isDarkMode && styles.textSecondaryDark]}>
            {'<'}20%
          </Text>
        </View>
      </View>

      <View style={styles.graphContainer}>{renderGraph()}</View>

      {selectedConcept && (
        <View style={[styles.detailsCard, isDarkMode && styles.detailsCardDark]}>
          <View style={styles.detailsHeader}>
            <Text style={[styles.detailsTitle, isDarkMode && styles.textDark]}>
              {selectedConcept.name}
            </Text>
            <TouchableOpacity onPress={() => setSelectedConcept(null)}>
              <Text style={styles.closeButton}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.detailsStats}>
            <View style={styles.detailsStat}>
              <Text style={[styles.detailsStatValue, isDarkMode && styles.textDark]}>
                {selectedConcept.mastery.toFixed(0)}%
              </Text>
              <Text style={[styles.detailsStatLabel, isDarkMode && styles.textSecondaryDark]}>
                Mastery
              </Text>
            </View>
            <View style={styles.detailsStat}>
              <Text style={[styles.detailsStatValue, isDarkMode && styles.textDark]}>
                {selectedConcept.cardCount}
              </Text>
              <Text style={[styles.detailsStatLabel, isDarkMode && styles.textSecondaryDark]}>
                Cards
              </Text>
            </View>
          </View>

          {selectedConcept.relatedConcepts.length > 0 && (
            <View style={styles.relatedSection}>
              <Text style={[styles.relatedTitle, isDarkMode && styles.textDark]}>
                Related Concepts
              </Text>
              <View style={styles.relatedList}>
                {selectedConcept.relatedConcepts.map((relatedId) => {
                  const related = concepts.find((c) => c.id === relatedId);
                  if (!related) return null;

                  return (
                    <TouchableOpacity
                      key={relatedId}
                      style={[styles.relatedItem, isDarkMode && styles.relatedItemDark]}
                      onPress={() => setSelectedConcept(related)}
                    >
                      <View
                        style={[
                          styles.relatedColor,
                          { backgroundColor: getConceptColor(related.mastery) },
                        ]}
                      />
                      <Text style={[styles.relatedName, isDarkMode && styles.textDark]}>
                        {related.name}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>
          )}
        </View>
      )}

      <View style={styles.infoCard}>
        <Text style={[styles.infoText, isDarkMode && styles.textSecondaryDark]}>
          💡 Tap a concept to see details and related concepts
        </Text>
      </View>
    </ScrollView>
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
  scrollContent: {
    padding: 20,
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
    flexWrap: 'wrap',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  legendColor: {
    width: 16,
    height: 16,
    borderRadius: 8,
    marginRight: 6,
  },
  legendText: {
    fontSize: 12,
    color: '#8E8E93',
  },
  graphContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  detailsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  detailsCardDark: {
    backgroundColor: '#1C1C1E',
  },
  detailsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  detailsTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#000000',
    flex: 1,
  },
  closeButton: {
    fontSize: 24,
    color: '#8E8E93',
    padding: 4,
  },
  detailsStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  detailsStat: {
    alignItems: 'center',
  },
  detailsStatValue: {
    fontSize: 32,
    fontWeight: '700',
    color: '#000000',
  },
  detailsStatLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 4,
  },
  relatedSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
  },
  relatedTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000000',
    marginBottom: 12,
  },
  relatedList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  relatedItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    padding: 12,
    marginRight: 8,
    marginBottom: 8,
  },
  relatedItemDark: {
    backgroundColor: '#2C2C2E',
  },
  relatedColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  relatedName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#000000',
  },
  infoCard: {
    backgroundColor: 'rgba(0, 122, 255, 0.1)',
    borderRadius: 12,
    padding: 16,
  },
  infoText: {
    fontSize: 14,
    color: '#8E8E93',
    textAlign: 'center',
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
    marginBottom: 12,
    textAlign: 'center',
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
