import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';

const KnowledgeGraphScreen = () => {
  const [nodes, setNodes] = useState<any[]>([]);
  
  useEffect(() => {
    // In a real scenario, this would fetch from the backend API.
    // For now, we mock the data to demonstrate the UI.
    setNodes([
        { id: '1', name: 'Python Basics', mastery: 85, color: 'green' },
        { id: '2', name: 'Data Structures', mastery: 60, color: 'yellow' },
        { id: '3', name: 'Algorithms', mastery: 45, color: 'orange' },
        { id: '4', name: 'Machine Learning', mastery: 10, color: 'gray' },
    ]);
  }, []);

  const renderItem = ({ item }: { item: any }) => (
    <View style={styles.item}>
      <View style={[styles.dot, { backgroundColor: item.color }]} />
      <View>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.mastery}>Mastery: {item.mastery}%</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Knowledge Graph Concepts</Text>
      <FlatList
        data={nodes}
        renderItem={renderItem}
        keyExtractor={item => item.id}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  dot: {
    width: 20,
    height: 20,
    borderRadius: 10,
    marginRight: 15,
  },
  name: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  mastery: {
    fontSize: 14,
    color: '#666',
  },
});

export default KnowledgeGraphScreen;
