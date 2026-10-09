import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAppStore } from '../state/useAppStore';
import { useEffect } from 'react';
import { checkHealth } from '../services/api';

export function HomeScreen({ navigation }: any) {
  const { isConnected, setConnected } = useAppStore();

  useEffect(() => {
    checkHealth().then(status => {
      setConnected(status);
    });
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>P009</Text>
        <Text style={styles.subtitle}>AI Companion</Text>
        <Text style={styles.status}>Backend Status: {isConnected ? "Connected 🟢" : "Disconnected 🔴"}</Text>
      </View>

      <View style={styles.companionArea}>
        <Text style={styles.companionPlaceholder}>Companion Placeholder</Text>
        <Text style={styles.greeting}>"무엇을 도와드릴까요?"</Text>
      </View>

      <View style={styles.menuArea}>
        <Text style={styles.menuItem} onPress={() => navigation.navigate('Conversation')}>[ Conversation ]</Text>
        <Text style={styles.menuItem} onPress={() => navigation.navigate('Memories')}>[ Memories ]</Text>
        <Text style={styles.menuItem} onPress={() => navigation.navigate('Relationship')}>[ Relationship ]</Text>
        <Text style={styles.menuItem} onPress={() => navigation.navigate('Settings')}>[ Settings ]</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212', padding: 20 },
  header: { marginBottom: 40, alignItems: 'center' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#fff' },
  subtitle: { fontSize: 16, color: '#aaa' },
  status: { fontSize: 12, color: '#888', marginTop: 10 },
  companionArea: { flex: 1, justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: '#333', borderRadius: 12, marginBottom: 40 },
  companionPlaceholder: { fontSize: 20, color: '#666', marginBottom: 20 },
  greeting: { fontSize: 18, color: '#ddd', fontStyle: 'italic' },
  menuArea: { justifyContent: 'flex-end', gap: 15, marginBottom: 20 },
  menuItem: { fontSize: 18, color: '#007AFF', textAlign: 'center', padding: 10, backgroundColor: '#222', borderRadius: 8 },
});
