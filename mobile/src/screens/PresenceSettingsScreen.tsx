import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Switch, TextInput, ScrollView, TouchableOpacity, ActivityIndicator, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getProactiveSettings, updateProactiveSettings, getProactiveHistory } from '../services/presenceApi';

const TEMP_USER_ID = "test_user_1";
const { width } = Dimensions.get('window');
const isTablet = width > 600;

export function PresenceSettingsScreen() {
  const [settings, setSettings] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [s, h] = await Promise.all([
        getProactiveSettings(TEMP_USER_ID),
        getProactiveHistory(TEMP_USER_ID)
      ]);
      setSettings(s);
      setHistory(h);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (value: boolean) => {
    setSettings({ ...settings, enabled: value });
    await updateProactiveSettings(TEMP_USER_ID, { enabled: value });
  };

  if (isLoading && !settings) {
    return (
      <SafeAreaView style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={isTablet ? styles.tabletContent : styles.scrollContent}>
        <View style={styles.headerRow}>
          <Text style={styles.headerTitle}>Proactive Companion</Text>
        </View>

        {settings && (
          <View style={styles.card}>
            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Enable Proactive Messages</Text>
              <Switch value={settings.enabled} onValueChange={handleToggle} />
            </View>
            <Text style={styles.description}>Allow Companion to initiate conversations when appropriate.</Text>
            
            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Daily Limit</Text>
              <Text style={styles.settingValue}>{settings.daily_limit}</Text>
            </View>
            
            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Quiet Hours Start</Text>
              <Text style={styles.settingValue}>{settings.quiet_hours_start}</Text>
            </View>
            
            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Quiet Hours End</Text>
              <Text style={styles.settingValue}>{settings.quiet_hours_end}</Text>
            </View>
          </View>
        )}

        <Text style={styles.sectionTitle}>Decision History</Text>
        {history.map((ev, idx) => (
          <View key={ev.id || idx} style={styles.historyCard}>
            <View style={styles.historyRow}>
              <Text style={styles.triggerText}>[{ev.trigger_type}]</Text>
              <Text style={[styles.decisionText, { color: ev.decision === 'ALLOW' ? '#4CAF50' : '#F44336' }]}>
                {ev.decision}
              </Text>
            </View>
            <Text style={styles.reasonText}>{ev.decision_reason}</Text>
            <Text style={styles.scoreText}>Score: {ev.score.toFixed(2)}</Text>
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
  tabletContent: { padding: 40, paddingBottom: 50, maxWidth: 800, alignSelf: 'center', width: '100%' },
  headerRow: { marginBottom: 20 },
  headerTitle: { color: '#fff', fontSize: 24, fontWeight: 'bold' },
  card: { backgroundColor: '#1e1e1e', borderRadius: 12, padding: 20, marginBottom: 20 },
  settingRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 },
  settingLabel: { color: '#fff', fontSize: 16 },
  settingValue: { color: '#007AFF', fontSize: 16, fontWeight: 'bold' },
  description: { color: '#888', fontSize: 14, marginBottom: 20, fontStyle: 'italic' },
  sectionTitle: { color: '#aaa', fontSize: 14, marginTop: 10, marginBottom: 10, textTransform: 'uppercase', fontWeight: 'bold' },
  historyCard: { backgroundColor: '#252525', borderRadius: 8, padding: 15, marginBottom: 10 },
  historyRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 5 },
  triggerText: { color: '#ffb347', fontWeight: 'bold' },
  decisionText: { fontWeight: 'bold' },
  reasonText: { color: '#ccc', fontSize: 14, marginBottom: 5 },
  scoreText: { color: '#666', fontSize: 12, textAlign: 'right' }
});
