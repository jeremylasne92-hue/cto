import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useAppStore } from '../store';
import notifications from '../services/notifications';
import { format } from 'date-fns';

export default function SettingsScreen() {
  const { settings, syncStatus, updateSettings, syncData } = useAppStore();
  const [isSyncing, setIsSyncing] = useState(false);

  const isDarkMode = settings.darkMode;

  const handleToggleDarkMode = () => {
    updateSettings({ darkMode: !settings.darkMode });
  };

  const handleToggleNotifications = async () => {
    const newValue = !settings.notificationsEnabled;
    
    if (newValue) {
      const granted = await notifications.requestPermissions();
      if (!granted) {
        Alert.alert(
          'Permissions Required',
          'Please enable notifications in your device settings.'
        );
        return;
      }

      const [hours, minutes] = settings.notificationTime.split(':');
      await notifications.scheduleDailyReminder(parseInt(hours), parseInt(minutes));
    } else {
      notifications.cancelAllNotifications();
    }

    updateSettings({ notificationsEnabled: newValue });
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await syncData();
      Alert.alert('Success', 'Data synced successfully');
    } catch (error) {
      Alert.alert(
        'Sync Failed',
        error instanceof Error ? error.message : 'Failed to sync data'
      );
    } finally {
      setIsSyncing(false);
    }
  };

  const handleChangeNotificationTime = () => {
    Alert.alert(
      'Change Notification Time',
      'This feature will open a time picker in production',
      [{ text: 'OK' }]
    );
  };

  return (
    <ScrollView
      style={[styles.container, isDarkMode && styles.containerDark]}
      contentContainerStyle={styles.scrollContent}
    >
      {/* Account Section */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Account
        </Text>
        
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.accountInfo}>
            <Icon
              name="account-circle"
              size={60}
              color={isDarkMode ? '#FFFFFF' : '#007AFF'}
            />
            <View style={styles.accountDetails}>
              <Text style={[styles.accountName, isDarkMode && styles.textDark]}>
                {settings.email || 'Guest User'}
              </Text>
              {settings.userId && (
                <Text style={[styles.accountId, isDarkMode && styles.textSecondaryDark]}>
                  ID: {settings.userId}
                </Text>
              )}
            </View>
          </View>
        </View>
      </View>

      {/* Sync Section */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Sync
        </Text>
        
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Icon
                name="sync"
                size={24}
                color={isDarkMode ? '#FFFFFF' : '#000000'}
              />
              <View style={styles.settingText}>
                <Text style={[styles.settingLabel, isDarkMode && styles.textDark]}>
                  Sync Status
                </Text>
                <Text style={[styles.settingValue, isDarkMode && styles.textSecondaryDark]}>
                  {syncStatus.lastSyncTime
                    ? `Last synced: ${format(syncStatus.lastSyncTime, 'MMM d, h:mm a')}`
                    : 'Never synced'}
                </Text>
                {syncStatus.pendingReviews > 0 && (
                  <Text style={[styles.pendingText, isDarkMode && styles.textSecondaryDark]}>
                    {syncStatus.pendingReviews} pending reviews
                  </Text>
                )}
              </View>
            </View>
          </View>

          <TouchableOpacity
            style={[styles.syncButton, isSyncing && styles.syncButtonDisabled]}
            onPress={handleSync}
            disabled={isSyncing}
          >
            {isSyncing ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <>
                <Icon name="cloud-sync" size={20} color="#FFFFFF" />
                <Text style={styles.syncButtonText}>Sync Now</Text>
              </>
            )}
          </TouchableOpacity>
        </View>
      </View>

      {/* Notifications Section */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Notifications
        </Text>
        
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Icon
                name="bell"
                size={24}
                color={isDarkMode ? '#FFFFFF' : '#000000'}
              />
              <View style={styles.settingText}>
                <Text style={[styles.settingLabel, isDarkMode && styles.textDark]}>
                  Daily Reminders
                </Text>
                <Text style={[styles.settingValue, isDarkMode && styles.textSecondaryDark]}>
                  Get notified when cards are due
                </Text>
              </View>
            </View>
            <Switch
              value={settings.notificationsEnabled}
              onValueChange={handleToggleNotifications}
              trackColor={{ false: '#767577', true: '#007AFF' }}
              thumbColor="#FFFFFF"
            />
          </View>

          {settings.notificationsEnabled && (
            <TouchableOpacity
              style={styles.timeRow}
              onPress={handleChangeNotificationTime}
            >
              <Text style={[styles.timeLabel, isDarkMode && styles.textDark]}>
                Reminder Time
              </Text>
              <View style={styles.timeValue}>
                <Text style={[styles.timeText, isDarkMode && styles.textDark]}>
                  {settings.notificationTime}
                </Text>
                <Icon name="chevron-right" size={20} color="#8E8E93" />
              </View>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Appearance Section */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          Appearance
        </Text>
        
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Icon
                name="theme-light-dark"
                size={24}
                color={isDarkMode ? '#FFFFFF' : '#000000'}
              />
              <View style={styles.settingText}>
                <Text style={[styles.settingLabel, isDarkMode && styles.textDark]}>
                  Dark Mode
                </Text>
                <Text style={[styles.settingValue, isDarkMode && styles.textSecondaryDark]}>
                  Use dark theme throughout the app
                </Text>
              </View>
            </View>
            <Switch
              value={settings.darkMode}
              onValueChange={handleToggleDarkMode}
              trackColor={{ false: '#767577', true: '#007AFF' }}
              thumbColor="#FFFFFF"
            />
          </View>
        </View>
      </View>

      {/* About Section */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDarkMode && styles.textDark]}>
          About
        </Text>
        
        <View style={[styles.card, isDarkMode && styles.cardDark]}>
          <View style={styles.aboutRow}>
            <Text style={[styles.aboutLabel, isDarkMode && styles.textDark]}>
              Version
            </Text>
            <Text style={[styles.aboutValue, isDarkMode && styles.textSecondaryDark]}>
              1.0.0
            </Text>
          </View>
          
          <View style={styles.aboutRow}>
            <Text style={[styles.aboutLabel, isDarkMode && styles.textDark]}>
              Build
            </Text>
            <Text style={[styles.aboutValue, isDarkMode && styles.textSecondaryDark]}>
              MVP
            </Text>
          </View>

          <TouchableOpacity
            style={styles.aboutLink}
            onPress={() => Alert.alert('About', 'SRS Mobile Companion App\nReview-Only MVP')}
          >
            <Text style={styles.aboutLinkText}>About This App</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={[styles.footerText, isDarkMode && styles.textSecondaryDark]}>
          Made with ❤️ for effective learning
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
    padding: 16,
    paddingBottom: 40,
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
  accountInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  accountDetails: {
    marginLeft: 16,
    flex: 1,
  },
  accountName: {
    fontSize: 20,
    fontWeight: '600',
    color: '#000000',
    marginBottom: 4,
  },
  accountId: {
    fontSize: 14,
    color: '#8E8E93',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 16,
    flex: 1,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000000',
    marginBottom: 4,
  },
  settingValue: {
    fontSize: 14,
    color: '#8E8E93',
  },
  pendingText: {
    fontSize: 12,
    color: '#FF9500',
    marginTop: 4,
  },
  syncButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  syncButtonDisabled: {
    opacity: 0.6,
  },
  syncButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
  },
  timeLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000000',
  },
  timeValue: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timeText: {
    fontSize: 16,
    color: '#000000',
    marginRight: 4,
  },
  aboutRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  aboutLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#000000',
  },
  aboutValue: {
    fontSize: 16,
    color: '#8E8E93',
  },
  aboutLink: {
    marginTop: 12,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
  },
  aboutLinkText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#007AFF',
    textAlign: 'center',
  },
  footer: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 20,
  },
  footerText: {
    fontSize: 14,
    color: '#8E8E93',
  },
  textDark: {
    color: '#FFFFFF',
  },
  textSecondaryDark: {
    color: '#8E8E93',
  },
});
