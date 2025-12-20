import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { TabParamList } from '../types';

import TodaysReviewsScreen from '../screens/TodaysReviewsScreen';
import DecksScreen from '../screens/DecksScreen';
import StatsScreen from '../screens/StatsScreen';
import GraphScreen from '../screens/GraphScreen';
import SettingsScreen from '../screens/SettingsScreen';
import { useAppStore } from '../store';

const Tab = createBottomTabNavigator<TabParamList>();

export default function Navigation() {
  const { settings } = useAppStore();

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName: string;

            switch (route.name) {
              case 'TodaysReviews':
                iconName = focused ? 'cards' : 'cards-outline';
                break;
              case 'Decks':
                iconName = focused ? 'book' : 'book-outline';
                break;
              case 'Stats':
                iconName = focused ? 'chart-line' : 'chart-line';
                break;
              case 'Graph':
                iconName = focused ? 'graph' : 'graph-outline';
                break;
              case 'Settings':
                iconName = focused ? 'cog' : 'cog-outline';
                break;
              default:
                iconName = 'circle';
            }

            return <Icon name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: 'gray',
          tabBarStyle: {
            backgroundColor: settings.darkMode ? '#1C1C1E' : '#FFFFFF',
            borderTopColor: settings.darkMode ? '#38383A' : '#E5E5EA',
          },
          headerStyle: {
            backgroundColor: settings.darkMode ? '#1C1C1E' : '#FFFFFF',
          },
          headerTintColor: settings.darkMode ? '#FFFFFF' : '#000000',
        })}
      >
        <Tab.Screen
          name="TodaysReviews"
          component={TodaysReviewsScreen}
          options={{ title: "Today's Reviews" }}
        />
        <Tab.Screen
          name="Decks"
          component={DecksScreen}
          options={{ title: 'Decks' }}
        />
        <Tab.Screen
          name="Stats"
          component={StatsScreen}
          options={{ title: 'Stats' }}
        />
        <Tab.Screen
          name="Graph"
          component={GraphScreen}
          options={{ title: 'Graph' }}
        />
        <Tab.Screen
          name="Settings"
          component={SettingsScreen}
          options={{ title: 'Settings' }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
