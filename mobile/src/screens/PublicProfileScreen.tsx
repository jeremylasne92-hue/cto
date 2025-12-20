import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  SafeAreaView
} from 'react-native';

interface PublicProfile {
  handle: string;
  visibility_default: string;
  bio?: string;
  interests?: string;
  learning_style?: string;
  skills: Array<{
    skill_id: string;
    skill_name: string;
    mastery: number;
  }>;
  metrics?: {
    hours_studied: number;
    xp_total: number;
    streak_days: number;
    certifications: string[];
  };
  follower_count: number;
}

interface PublicProfileScreenProps {
  route: {
    params: {
      handle: string;
    };
  };
}

const PublicProfileScreen: React.FC<PublicProfileScreenProps> = ({ route }) => {
  const { handle } = route.params;
  const [profile, setProfile] = useState<PublicProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfile();
  }, [handle]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`http://localhost:5000/public/profile/${handle}`);
      
      if (!response.ok) {
        throw new Error('Profile not found');
      }
      
      const data = await response.json();
      setProfile(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#3498db" />
          <Text style={styles.loadingText}>Loading profile...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !profile) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>{error || 'Profile not found'}</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.handle}>@{profile.handle}</Text>
          <View style={styles.badge}>
            <Text style={styles.badgeText}>{profile.visibility_default}</Text>
          </View>
        </View>

        {profile.bio && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Bio</Text>
            <Text style={styles.sectionContent}>{profile.bio}</Text>
          </View>
        )}

        {profile.interests && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Interests</Text>
            <View style={styles.interestsContainer}>
              {profile.interests.split(',').map((interest, idx) => (
                <View key={idx} style={styles.chip}>
                  <Text style={styles.chipText}>{interest.trim()}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {profile.learning_style && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Learning Style</Text>
            <Text style={styles.sectionContent}>{profile.learning_style}</Text>
          </View>
        )}

        {profile.metrics && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Metrics</Text>
            <View style={styles.metricsGrid}>
              <View style={styles.metricCard}>
                <Text style={styles.metricValue}>{profile.metrics.hours_studied.toFixed(1)}</Text>
                <Text style={styles.metricLabel}>Hours</Text>
              </View>
              <View style={styles.metricCard}>
                <Text style={styles.metricValue}>{profile.metrics.xp_total}</Text>
                <Text style={styles.metricLabel}>XP</Text>
              </View>
              <View style={styles.metricCard}>
                <Text style={styles.metricValue}>{profile.metrics.streak_days}</Text>
                <Text style={styles.metricLabel}>Streak</Text>
              </View>
              <View style={styles.metricCard}>
                <Text style={styles.metricValue}>{profile.metrics.certifications.length}</Text>
                <Text style={styles.metricLabel}>Certs</Text>
              </View>
            </View>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Skills</Text>
          {profile.skills.length === 0 ? (
            <Text style={styles.emptyText}>No public skills</Text>
          ) : (
            <View style={styles.skillsList}>
              {profile.skills.map((skill, idx) => (
                <View key={idx} style={styles.skillItem}>
                  <View style={styles.skillHeader}>
                    <Text style={styles.skillName}>{skill.skill_name}</Text>
                    <Text style={styles.skillMastery}>
                      {(skill.mastery * 100).toFixed(0)}%
                    </Text>
                  </View>
                  <View style={styles.skillBar}>
                    <View
                      style={[
                        styles.skillBarFill,
                        { width: `${skill.mastery * 100}%` }
                      ]}
                    />
                  </View>
                </View>
              ))}
            </View>
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Followers</Text>
          <Text style={styles.followerCount}>{profile.follower_count} followers</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#e74c3c',
    textAlign: 'center',
  },
  header: {
    backgroundColor: '#2c3e50',
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  handle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  badge: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  section: {
    backgroundColor: '#fff',
    padding: 16,
    marginVertical: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 12,
  },
  sectionContent: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  interestsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  chipText: {
    color: '#1976d2',
    fontSize: 14,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  metricCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#f9f9f9',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#3498db',
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 14,
    color: '#666',
  },
  skillsList: {
    gap: 12,
  },
  skillItem: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
  },
  skillHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  skillName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
  },
  skillMastery: {
    fontSize: 16,
    fontWeight: '600',
    color: '#27ae60',
  },
  skillBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  skillBarFill: {
    height: '100%',
    backgroundColor: '#3498db',
  },
  followerCount: {
    fontSize: 16,
    color: '#666',
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
  },
});

export default PublicProfileScreen;
