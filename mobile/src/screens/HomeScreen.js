import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const HomeScreen = ({ navigation }) => {
  const [userId, setUserId] = useState(null);
  const [recentProfiles, setRecentProfiles] = useState([]);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const storedUserId = await AsyncStorage.getItem('userId');
      if (storedUserId) {
        setUserId(parseInt(storedUserId));
      }
      
      // Load recent profiles from storage
      const recent = await AsyncStorage.getItem('recentProfiles');
      if (recent) {
        setRecentProfiles(JSON.parse(recent));
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const handleDeepLink = (handle) => {
    navigation.navigate('PublicProfile', { handle });
  };

  const addRecentProfile = async (handle) => {
    try {
      const updated = [handle, ...recentProfiles.filter(p => p !== handle)].slice(0, 5);
      setRecentProfiles(updated);
      await AsyncStorage.setItem('recentProfiles', JSON.stringify(updated));
    } catch (error) {
      console.error('Error saving recent profile:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Welcome Section */}
      <View style={styles.welcomeSection}>
        <Text style={styles.welcomeTitle}>Social Learning Platform</Text>
        <Text style={styles.welcomeSubtitle}>
          Connect with other learners and track your progress
        </Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => navigation.navigate('Profile')}
        >
          <Text style={styles.actionButtonText}>View My Profile</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.secondaryButton}
          onPress={() => {
            Alert.prompt(
              'Search Public Profile',
              'Enter a user handle:',
              [
                {
                  text: 'Cancel',
                  style: 'cancel',
                },
                {
                  text: 'Search',
                  onPress: (handle) => {
                    if (handle && handle.trim()) {
                      addRecentProfile(handle.trim());
                      navigation.navigate('PublicProfile', { handle: handle.trim() });
                    }
                  },
                },
              ],
              'plain-text'
            );
          }}
        >
          <Text style={styles.secondaryButtonText}>Search Public Profile</Text>
        </TouchableOpacity>
      </View>

      {/* Recent Profiles */}
      {recentProfiles.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recently Viewed</Text>
          {recentProfiles.map((handle, index) => (
            <TouchableOpacity
              key={index}
              style={styles.profileItem}
              onPress={() => handleDeepLink(handle)}
            >
              <Text style={styles.profileHandle}>@{handle}</Text>
              <Text style={styles.profileAction}>View Profile →</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Feature Cards */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Features</Text>
        
        <View style={styles.featureGrid}>
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>🎯</Text>
            <Text style={styles.featureTitle}>Skill Tracking</Text>
            <Text style={styles.featureDescription}>
              Track your learning progress and skills
            </Text>
          </View>
          
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>👥</Text>
            <Text style={styles.featureTitle}>Social Learning</Text>
            <Text style={styles.featureDescription}>
              Connect with other learners
            </Text>
          </View>
          
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>📊</Text>
            <Text style={styles.featureTitle}>Progress Analysis</Text>
            <Text style={styles.featureDescription}>
              Compare your progress with others
            </Text>
          </View>
          
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>🏆</Text>
            <Text style={styles.featureTitle}>Achievements</Text>
            <Text style={styles.featureDescription}>
              Earn certifications and rewards
            </Text>
          </View>
        </View>
      </View>

      {/* Quick Tips */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Getting Started</Text>
        <View style={styles.tipItem}>
          <Text style={styles.tipNumber}>1</Text>
          <Text style={styles.tipText}>
            Set up your profile with your learning goals and interests
          </Text>
        </View>
        <View style={styles.tipItem}>
          <Text style={styles.tipNumber}>2</Text>
          <Text style={styles.tipText}>
            Add your skills and track your learning progress
          </Text>
        </View>
        <View style={styles.tipItem}>
          <Text style={styles.tipNumber}>3</Text>
          <Text style={styles.tipText}>
            Connect with other learners and compare your skills
          </Text>
        </View>
        <View style={styles.tipItem}>
          <Text style={styles.tipNumber}>4</Text>
          <Text style={styles.tipText}>
            Use the comparison tool to find learning opportunities
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  welcomeSection: {
    backgroundColor: '#007bff',
    padding: 20,
    alignItems: 'center',
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  welcomeSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
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
    marginBottom: 15,
  },
  actionButton: {
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  secondaryButtonText: {
    color: '#007bff',
    fontSize: 16,
    fontWeight: '600',
  },
  profileItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
    marginBottom: 8,
  },
  profileHandle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  profileAction: {
    fontSize: 14,
    color: '#007bff',
  },
  featureGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  featureCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  featureIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  featureTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
    textAlign: 'center',
  },
  featureDescription: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    lineHeight: 16,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  tipNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#007bff',
    color: 'white',
    textAlign: 'center',
    lineHeight: 24,
    fontSize: 12,
    fontWeight: 'bold',
    marginRight: 10,
    marginTop: 2,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
  },
});

export default HomeScreen;