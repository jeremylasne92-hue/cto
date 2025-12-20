import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useAppStore } from '../store';
import { format, subDays } from 'date-fns';

const { width } = Dimensions.get('window');

export default function StatsScreen() {
  const { userStats, settings, loadUserStats, isLoading } = useAppStore();

  useEffect(() => {
    loadUserStats();
  }, []);

  const isDarkMode = settings.darkMode;

  if (isLoading || !userStats) {
    return (
      <View style={[styles.container, isDarkMode && styles.containerDark]}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  // Prepare chart data
  const last30Days = Array.from({ length: 30 }, (_, i) => {
    const date = format(subDays(new Date(), 29 - i), 'yyyy-MM-dd');
    const historyEntry = userStats.reviewHistory.find((h) => h.date === date);
    return {
      date,
      reviewed: historyEntry?.reviewed || 0,
      correct: historyEntry?.correct || 0,
    };
  });

  const chartData = {
    labels: last30Days
      .filter((_, i) => i % 6 === 0)
      .map((d) => format(new Date(d.date), 'M/d')),
    datasets: [
      {
        data: last30Days.map((d) => d.reviewed),
        color: (opacity = 1) => `rgba(0, 122, 255, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const chartConfig = {
    backgroundColor: isDarkMode ? '#1C1C1E' : '#FFFFFF',
    backgroundGradientFrom: isDarkMode ? '#1C1C1E' : '#FFFFFF',
    backgroundGradientTo: isDarkMode ? '#1C1C1E' : '#FFFFFF',
    decimalPlaces: 0,
    color: (opacity = 1) =>
      isDarkMode ? `rgba(255, 255, 255, ${opacity})` : `rgba(0, 0, 0, ${opacity})`,
    labelColor: (opacity = 1) =>
      isDarkMode ? `rgba(142, 142, 147, ${opacity})` : `rgba(142, 142, 147, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: '#007AFF',
    },
  };

  const retentionRate = userStats.retentionRate;
  const totalReviews = last30Days.reduce((sum, d) => sum + d.reviewed, 0);
  const xpToNextLevel = (userStats.level * 100) - userStats.xp;

  return (
    <ScrollView
      style={[styles.container, isDarkMode && styles.containerDark]}
      contentContainerStyle={styles.scrollContent}
    >
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Overview
        </Text>

        <View style={styles.statsGrid}>
          <View style={[styles.statCard, isDarkMode && styles.statCardDark]}>
            <Icon name="fire" size={32} color="#FF9500" />
            <Text style={[styles.statValue, isDarkMode && styles.textDark]}>
              {userStats.currentStreak}
            </Text>
            <Text style={[styles.statLabel, isDarkMode && styles.textSecondaryDark]}>
              Day Streak
            </Text>
          </View>

          <View style={[styles.statCard, isDarkMode && styles.statCardDark]}>
            <Icon name="trophy" size={32} color="#FFD700" />
            <Text style={[styles.statValue, isDarkMode && styles.textDark]}>
              {userStats.longestStreak}
            </Text>
            <Text style={[styles.statLabel, isDarkMode && styles.textSecondaryDark]}>
              Best Streak
            </Text>
          </View>

          <View style={[styles.statCard, isDarkMode && styles.statCardDark]}>
            <Icon name="star" size={32} color="#007AFF" />
            <Text style={[styles.statValue, isDarkMode && styles.textDark]}>
              {userStats.level}
            </Text>
            <Text style={[styles.statLabel, isDarkMode && styles.textSecondaryDark]}>
              Level
            </Text>
          </View>

          <View style={[styles.statCard, isDarkMode && styles.statCardDark]}>
            <Icon name="chart-line" size={32} color="#34C759" />
            <Text style={[styles.statValue, isDarkMode && styles.textDark]}>
              {retentionRate.toFixed(0)}%
            </Text>
            <Text style={[styles.statLabel, isDarkMode && styles.textSecondaryDark]}>
              Retention
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Experience Points
        </Text>
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.xpHeader}>
            <Text style={[styles.xpValue, isDarkMode && styles.textDark]}>
              {userStats.xp} XP
            </Text>
            <Text style={[styles.xpNextLevel, isDarkMode && styles.textSecondaryDark]}>
              {xpToNextLevel} to Level {userStats.level + 1}
            </Text>
          </View>
          <View style={styles.xpBarContainer}>
            <View
              style={[
                styles.xpBar,
                { width: `${((userStats.xp % 100) / 100) * 100}%` },
              ]}
            />
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Streak Freezes
        </Text>
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.freezeContainer}>
            <Icon name="snowflake" size={40} color="#00C7BE" />
            <View style={styles.freezeInfo}>
              <Text style={[styles.freezeValue, isDarkMode && styles.textDark]}>
                {userStats.streakFreezeCount}
              </Text>
              <Text style={[styles.freezeLabel, isDarkMode && styles.textSecondaryDark]}>
                Freezes Available
              </Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Last 30 Days
        </Text>
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <LineChart
            data={chartData}
            width={width - 64}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
          <View style={styles.chartStats}>
            <View style={styles.chartStat}>
              <Text style={[styles.chartStatValue, isDarkMode && styles.textDark]}>
                {totalReviews}
              </Text>
              <Text style={[styles.chartStatLabel, isDarkMode && styles.textSecondaryDark]}>
                Total Reviews
              </Text>
            </View>
            <View style={styles.chartStat}>
              <Text style={[styles.chartStatValue, isDarkMode && styles.textDark]}>
                {(totalReviews / 30).toFixed(1)}
              </Text>
              <Text style={[styles.chartStatLabel, isDarkMode && styles.textSecondaryDark]}>
                Avg Per Day
              </Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          All Time
        </Text>
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.allTimeStats}>
            <View style={styles.allTimeStat}>
              <Text style={[styles.allTimeValue, isDarkMode && styles.textDark]}>
                {userStats.totalCardsReviewed}
              </Text>
              <Text style={[styles.allTimeLabel, isDarkMode && styles.textSecondaryDark]}>
                Cards Reviewed
              </Text>
            </View>
          </View>
        </View>
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
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#000000',
    marginBottom: 12,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: (width - 48) / 2,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statCardDark: {
    backgroundColor: '#1C1C1E',
  },
  statValue: {
    fontSize: 32,
    fontWeight: '700',
    color: '#000000',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 4,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardDark: {
    backgroundColor: '#1C1C1E',
  },
  xpHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  xpValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#000000',
  },
  xpNextLevel: {
    fontSize: 14,
    color: '#8E8E93',
  },
  xpBarContainer: {
    height: 12,
    backgroundColor: '#E5E5EA',
    borderRadius: 6,
    overflow: 'hidden',
  },
  xpBar: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 6,
  },
  freezeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  freezeInfo: {
    marginLeft: 20,
  },
  freezeValue: {
    fontSize: 32,
    fontWeight: '700',
    color: '#000000',
  },
  freezeLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 4,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  chartStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  chartStat: {
    alignItems: 'center',
  },
  chartStatValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#000000',
  },
  chartStatLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 4,
  },
  allTimeStats: {
    alignItems: 'center',
  },
  allTimeStat: {
    alignItems: 'center',
  },
  allTimeValue: {
    fontSize: 48,
    fontWeight: '700',
    color: '#000000',
  },
  allTimeLabel: {
    fontSize: 16,
    color: '#8E8E93',
    marginTop: 8,
  },
  textDark: {
    color: '#FFFFFF',
  },
  textSecondaryDark: {
    color: '#8E8E93',
  },
});
