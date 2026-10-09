import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getEmotionState, getEmotionHistory } from '../services/api';

const TEMP_USER_ID = "test_user_1";

export function DebugEmotionScreen() {
  const [state, setState] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [stateData, historyData] = await Promise.all([
        getEmotionState(TEMP_USER_ID),
        getEmotionHistory(TEMP_USER_ID)
      ]);
      setState(stateData);
      setHistory(historyData);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !state) {
    return (
      <SafeAreaView style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerRow}>
          <Text style={styles.headerTitle}>Emotion Debugger</Text>
          <TouchableOpacity onPress={loadData}>
            <Text style={styles.refreshText}>Refresh</Text>
          </TouchableOpacity>
        </View>

        {state && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Current State</Text>
            <View style={styles.row}>
              <Text style={styles.label}>Primary:</Text>
              <Text style={styles.value}>{state.primary_emotion}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Valence:</Text>
              <Text style={styles.value}>{state.valence.toFixed(2)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Arousal:</Text>
              <Text style={styles.value}>{state.arousal.toFixed(2)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Warmth:</Text>
              <Text style={styles.value}>{state.warmth.toFixed(2)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Engagement:</Text>
              <Text style={styles.value}>{state.engagement.toFixed(2)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Tension:</Text>
              <Text style={styles.value}>{state.tension.toFixed(2)}</Text>
            </View>
            <Text style={styles.timeText}>Last updated: {new Date(state.updated_at).toLocaleTimeString()}</Text>
          </View>
        )}

        <Text style={styles.sectionTitle}>Transition History</Text>
        {history.map((ev, idx) => (
          <View key={ev.id || idx} style={styles.historyCard}>
            <Text style={styles.historyTrigger}>[{ev.event_type}] {ev.trigger}</Text>
            <Text style={styles.historyTransition}>
              {ev.previous_state} ➔ {ev.new_state}
            </Text>
            <Text style={styles.timeText}>{new Date(ev.created_at).toLocaleString()}</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212' },
  centerContainer: { flex: 1, backgroundColor: '#121212', justifyContent: 'center', alignItems: 'center' },
  scrollContent: { padding: 20, paddingBottom: 50 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  headerTitle: { color: '#fff', fontSize: 24, fontWeight: 'bold' },
  refreshText: { color: '#007AFF', fontSize: 16 },
  sectionTitle: { color: '#aaa', fontSize: 14, marginTop: 20, marginBottom: 10, textTransform: 'uppercase', fontWeight: 'bold' },
  card: { backgroundColor: '#222', borderRadius: 8, padding: 15, marginBottom: 10 },
  cardTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginBottom: 15 },
  row: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  label: { color: '#888', fontSize: 16 },
  value: { color: '#fff', fontSize: 16, fontWeight: '500' },
  timeText: { color: '#666', fontSize: 12, marginTop: 10, textAlign: 'right' },
  historyCard: { backgroundColor: '#1e1e1e', borderRadius: 8, padding: 12, marginBottom: 8, borderWidth: 1, borderColor: '#333' },
  historyTrigger: { color: '#bbb', fontSize: 14, marginBottom: 5 },
  historyTransition: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
