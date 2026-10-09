import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getRelationshipState, getRelationshipHistory } from '../services/api';

const TEMP_USER_ID = "test_user_1";

export function DebugRelationshipScreen() {
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
        getRelationshipState(TEMP_USER_ID),
        getRelationshipHistory(TEMP_USER_ID)
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
          <Text style={styles.headerTitle}>Relationship Debugger</Text>
          <TouchableOpacity onPress={loadData}>
            <Text style={styles.refreshText}>Refresh</Text>
          </TouchableOpacity>
        </View>

        {state && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Level: {state.relationship_level}</Text>
            
            <View style={styles.row}>
              <Text style={styles.label}>Trust:</Text>
              <Text style={styles.value}>{state.trust.toFixed(3)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Familiarity:</Text>
              <Text style={styles.value}>{state.familiarity.toFixed(3)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Closeness:</Text>
              <Text style={styles.value}>{state.closeness.toFixed(3)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Engagement:</Text>
              <Text style={styles.value}>{state.engagement.toFixed(3)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Reliability:</Text>
              <Text style={styles.value}>{state.reliability.toFixed(3)}</Text>
            </View>
            <Text style={styles.timeText}>Updated: {new Date(state.updated_at).toLocaleString()}</Text>
          </View>
        )}

        <Text style={styles.sectionTitle}>Interaction History</Text>
        {history.map((ev, idx) => (
          <View key={ev.id || idx} style={styles.historyCard}>
            <Text style={styles.historySignal}>[{ev.severity}] {ev.signal_type}</Text>
            <Text style={styles.historyDelta}>
              {ev.dimension_changed}: {ev.delta_applied}
            </Text>
            {ev.reason && <Text style={styles.reasonText}>{ev.reason}</Text>}
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
  cardTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 15, textAlign: 'center', color: '#ffb347' },
  row: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  label: { color: '#888', fontSize: 16 },
  value: { color: '#fff', fontSize: 16, fontWeight: '500' },
  timeText: { color: '#666', fontSize: 12, marginTop: 10, textAlign: 'right' },
  historyCard: { backgroundColor: '#1e1e1e', borderRadius: 8, padding: 12, marginBottom: 8, borderWidth: 1, borderColor: '#333' },
  historySignal: { color: '#ffb347', fontSize: 14, marginBottom: 5, fontWeight: 'bold' },
  historyDelta: { color: '#88ff88', fontSize: 14 },
  reasonText: { color: '#bbb', fontSize: 12, marginTop: 5, fontStyle: 'italic' }
});
