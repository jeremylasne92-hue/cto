import React from 'react';
import { SafeAreaView, StyleSheet, StatusBar } from 'react-native';
import KnowledgeGraphScreen from './KnowledgeGraphScreen';

const App = () => {
  return (
    <>
      <StatusBar barStyle="dark-content" />
      <SafeAreaView style={styles.container}>
        <KnowledgeGraphScreen />
      </SafeAreaView>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
});

export default App;
