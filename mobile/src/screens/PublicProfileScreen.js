import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
  TouchableOpacity,
} from 'react-native';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/profile';

const PublicProfileScreen = ({ route, navigation }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Get handle from route params or deep link
  const handle = route?.params?.handle || 'defaultuser';

  useEffect(() => {
    loadPublicProfile();
  }, [handle]);

  const loadPublicProfile = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE_URL}/public/${handle}`);
      
      if (response.data.success) {
        setProfile(response.data.profile);
      } else {
        setError('Profile not found');
      }
    } catch (err) {
      console.error('Error loading public profile:', err);
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading profile...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadPublicProfile}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>No profile data available</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>
            {profile.handle.charAt(0).toUpperCase()}
          </Text>
        </View>
        <Text style={styles.handle}>@{profile.handle}</Text>
        <View style={styles.socialStats}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>
              {formatNumber(profile.social?.followers_count || 0)}
            </Text>
            <Text style={styles.statLabel}>Followers</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>
              {formatNumber(profile.social?.following_count || 0)}
            </Text>
            <Text style={styles.statLabel}>Following</Text>
          </View>
        </View>
      </View>

      {/* Bio Section */}
      {profile.bio && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <Text style={styles.bioText}>{profile.bio}</Text>
        </View>
      )}

      {/* Learning Style */}
      {profile.learning_style && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Learning Style</Text>
          <Text style={styles.learningStyleText}>{profile.learning_style}</Text>
        </View>
      )}

      {/* Interests */}
      {profile.interests && profile.interests.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Interests</Text>
          <View style={styles.interestsContainer}>
            {profile.interests.map((interest, index) => (
              <View key={index} style={styles.interestTag}>
                <Text style={styles.interestText}>{interest}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Learning Metrics</Text>
        <View style={styles.metricsContainer}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {profile.metrics?.hours_studied?.toFixed(1) || '0.0'}
            </Text>
            <Text style={styles.metricLabel}>Hours Studied</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {profile.metrics?.xp_total?.toString() || '0'}
            </Text>
            <Text style={styles.metricLabel}>XP Points</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {profile.metrics?.streak_days?.toString() || '0'}
            </Text>
            <Text style={styles.metricLabel}>Day Streak</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {profile.metrics?.certifications?.length?.toString() || '0'}
            </Text>
            <Text style={styles.metricLabel}>Certifications</Text>
          </View>
        </View>
      </View>

      {/* Skills */}
      {profile.skills && profile.skills.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Skills</Text>
          {profile.skills.map((skill, index) => (
            <View key={index} style={styles.skillItem}>
              <Text style={styles.skillName}>{skill.skill_id}</Text>
              <View style={styles.skillLevelContainer}>
                <Text style={styles.skillLevel}>Level {skill.mastery_level}</Text>
                <View style={styles.skillBar}>
                  <View 
                    style={[
                      styles.skillBarFill, 
                      { width: `${(skill.mastery_level / 5) * 100}%` }
                    ]} 
                  />
                </View>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Certifications */}
      {profile.metrics?.certifications && profile.metrics.certifications.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Certifications</Text>
          {profile.metrics.certifications.map((cert, index) => (
            <View key={index} style={styles.certificationItem}>
              <Text style={styles.certificationText}>🏆 {cert}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    backgroundColor: 'white',
    alignItems: 'center',
    padding: 20,
    marginBottom: 10,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#007bff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  avatarText: {
    color: 'white',
    fontSize: 32,
    fontWeight: 'bold',
  },
  handle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  socialStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#007bff',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
  },
  section: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  bioText: {
    fontSize: 16,
    color: '#555',
    lineHeight: 22,
  },
  learningStyleText: {
    fontSize: 16,
    color: '#555',
    fontStyle: 'italic',
  },
  interestsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  interestTag: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  interestText: {
    color: '#1976d2',
    fontSize: 14,
    fontWeight: '500',
  },
  metricsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007bff',
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  skillItem: {
    marginBottom: 15,
  },
  skillName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  skillLevelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  skillLevel: {
    fontSize: 14,
    color: '#666',
    marginRight: 10,
  },
  skillBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
  },
  skillBarFill: {
    height: 8,
    backgroundColor: '#28a745',
    borderRadius: 4,
  },
  certificationItem: {
    padding: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
    marginBottom: 8,
  },
  certificationText: {
    fontSize: 14,
    color: '#333',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#dc3545',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default PublicProfileScreen;