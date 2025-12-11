import React, { useEffect } from 'react';
import { StatusBar, useColorScheme } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import Navigation from './src/navigation';
import { useAppStore } from './src/store';
import notifications from './src/services/notifications';

function App(): JSX.Element {
  const colorScheme = useColorScheme();
  const { initializeApp, settings } = useAppStore();

  useEffect(() => {
    const initialize = async () => {
      await initializeApp();
      notifications.configure();
    };

    initialize();
  }, []);

  const isDarkMode = settings.darkMode || colorScheme === 'dark';

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={isDarkMode ? '#000000' : '#FFFFFF'}
      />
      <Navigation />
    </GestureHandlerRootView>
  );
}

export default App;
