import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:5000/api/profile';

const ProfileScreen = ({ navigation }) => {
  const [userId, setUserId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      // Get user ID from storage or create a default one
      let storedUserId = await AsyncStorage.getItem('userId');
      if (!storedUserId) {
        // For demo purposes, create a default user
        storedUserId = '1';
        await AsyncStorage.setItem('userId', storedUserId);
      }
      
      setUserId(parseInt(storedUserId));
      
      // Load profile data
      const response = await axios.get(`${API_BASE_URL}/${storedUserId}?include_private=true`);
      
      if (response.data.success) {
        setProfile(response.data.profile);
      } else {
        // Create a basic profile if none exists
        await createBasicProfile(storedUserId);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      Alert.alert('Error', 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const createBasicProfile = async (userId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/upsert`, {
        user_id: parseInt(userId),
        handle: `user${userId}`,
        bio: 'Welcome to your learning journey!',
        interests: ['Learning', 'Technology'],
        learning_style: 'Visual',
        is_private: false
      });

      if (response.data.success) {
        setProfile(response.data.profile.profile);
      }
    } catch (error) {
      console.error('Error creating basic profile:', error);
    }
  };

  const saveProfile = async () => {
    if (!profile || !userId) return;
    
    setSaving(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/upsert`, {
        user_id: userId,
        handle: profile.user?.handle || `user${userId}`,
        bio: profile.profile?.bio || '',
        interests: profile.profile?.interests || [],
        learning_style: profile.profile?.learning_style || ''
      });

      if (response.data.success) {
        Alert.alert('Success', 'Profile saved successfully');
        setProfile(response.data.profile);
      } else {
        Alert.alert('Error', 'Failed to save profile');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      Alert.alert('Error', 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const updateMetrics = async () => {
    if (!userId) return;
    
    try {
      const response = await axios.post(`${API_BASE_URL}/metrics`, {
        user_id: userId,
        update_from_logs: true
      });

      if (response.data.success && response.data.metrics) {
        setProfile(prev => ({
          ...prev,
          metrics: response.data.metrics
        }));
        Alert.alert('Success', 'Metrics updated successfully');
      }
    } catch (error) {
      console.error('Error updating metrics:', error);
      Alert.alert('Error', 'Failed to update metrics');
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num?.toString() || '0';
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading profile...</Text>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>No profile data available</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadProfile}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Profile Header */}
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>
            {(profile.user?.handle || 'U').charAt(0).toUpperCase()}
          </Text>
        </View>
        <Text style={styles.handle}>@{profile.user?.handle || 'Unknown'}</Text>
        
        {/* Social Stats */}
        <View style={styles.socialStats}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>
              {formatNumber(profile.profile?.followers_count || 0)}
            </Text>
            <Text style={styles.statLabel}>Followers</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>
              {formatNumber(profile.profile?.following_count || 0)}
            </Text>
            <Text style={styles.statLabel}>Following</Text>
          </View>
        </View>
      </View>

      {/* Bio Section - Editable */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Bio</Text>
        <TouchableOpacity
          style={styles.editField}
          onPress={() => Alert.prompt(
            'Edit Bio',
            'Enter your bio:',
            [
              {
                text: 'Cancel',
                style: 'cancel',
              },
              {
                text: 'Save',
                onPress: (bio) => {
                  setProfile(prev => ({
                    ...prev,
                    profile: { ...prev.profile, bio }
                  }));
                },
              },
            ],
            'plain-text',
            profile.profile?.bio || ''
          )}
        >
          <Text style={styles.editFieldText}>
            {profile.profile?.bio || 'Tap to add a bio'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Learning Style - Editable */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Learning Style</Text>
        <TouchableOpacity
          style={styles.editField}
          onPress={() => Alert.prompt(
            'Edit Learning Style',
            'e.g., Visual, Auditory, Kinesthetic',
            [
              {
                text: 'Cancel',
                style: 'cancel',
              },
              {
                text: 'Save',
                onPress: (learningStyle) => {
                  setProfile(prev => ({
                    ...prev,
                    profile: { ...prev.profile, learning_style: learningStyle }
                  }));
                },
              },
            ],
            'plain-text',
            profile.profile?.learning_style || ''
          )}
        >
          <Text style={styles.editFieldText}>
            {profile.profile?.learning_style || 'Tap to add learning style'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Metrics */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Learning Metrics</Text>
          <TouchableOpacity 
            style={styles.updateButton}
            onPress={updateMetrics}
          >
            <Text style={styles.updateButtonText}>Update</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.metricsContainer}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {profile.metrics?.hours_studied?.toFixed(1) || '0.0'}
            </Text>
            <Text style={styles.metricLabel}>Hours Studied</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {formatNumber(profile.metrics?.xp_total || 0)}
            </Text>
            <Text style={styles.metricLabel}>XP Points</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {profile.metrics?.streak_days || 0}
            </Text>
            <Text style={styles.metricLabel}>Day Streak</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {formatNumber(profile.metrics?.certifications?.length || 0)}
            </Text>
            <Text style={styles.metricLabel}>Certifications</Text>
          </View>
        </View>
      </View>

      {/* Skills Preview */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Skills</Text>
          <TouchableOpacity 
            style={styles.viewAllButton}
            onPress={() => navigation.navigate('Skills')}
          >
            <Text style={styles.viewAllButtonText}>Manage</Text>
          </TouchableOpacity>
        </View>
        {profile.skills && profile.skills.length > 0 ? (
          profile.skills.slice(0, 3).map((skill, index) => (
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
          ))
        ) : (
          <Text style={styles.noDataText}>No skills added yet</Text>
        )}
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <Text style={styles.noDataText}>Study sessions and achievements will appear here</Text>
      </View>

      {/* Save Button */}
      <TouchableOpacity 
        style={[styles.saveButton, saving && styles.saveButtonDisabled]}
        onPress={saveProfile}
        disabled={saving}
      >
        <Text style={styles.saveButtonText}>
          {saving ? 'Saving...' : 'Save Profile'}
        </Text>
      </TouchableOpacity>
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
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  editField: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  editFieldText: {
    fontSize: 16,
    color: '#333',
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
    fontSize: 20,
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
    minWidth: 60,
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
  noDataText: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: 20,
  },
  updateButton: {
    backgroundColor: '#28a745',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  updateButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  viewAllButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  viewAllButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  saveButton: {
    backgroundColor: '#007bff',
    margin: 10,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveButtonDisabled: {
    backgroundColor: '#6c757d',
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#dc3545',
    textAlign: 'center',
    marginBottom: 20,
    marginTop: 50,
  },
  retryButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
    alignSelf: 'center',
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProfileScreen;