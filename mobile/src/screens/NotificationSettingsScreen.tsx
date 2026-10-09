import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Switch, ScrollView, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getNotificationSettings, updateNotificationSettings } from '../services/notificationApi';

const TEMP_USER_ID = "test_user_1";

export function NotificationSettingsScreen() {
  const [settings, setSettings] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      const s = await getNotificationSettings(TEMP_USER_ID);
      setSettings(s);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (key: string, value: boolean) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    await updateNotificationSettings(TEMP_USER_ID, { [key]: value });
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
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.headerTitle}>Notifications</Text>

        {settings && (
          <View style={styles.card}>
            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Enable Notifications</Text>
              <Switch value={settings.notifications_enabled} onValueChange={(v) => handleToggle('notifications_enabled', v)} />
            </View>
            <Text style={styles.description}>Master switch for all Companion notifications.</Text>
            
            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Proactive Messages</Text>
              <Switch value={settings.proactive_messages_enabled} onValueChange={(v) => handleToggle('proactive_messages_enabled', v)} />
            </View>
            <Text style={styles.description}>Allow Companion to start conversations.</Text>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Notification Preview</Text>
              <Switch value={settings.notification_preview_enabled} onValueChange={(v) => handleToggle('notification_preview_enabled', v)} />
            </View>
            <Text style={styles.description}>Show message content on lock screen.</Text>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>Never Disturb</Text>
              <Switch value={settings.never_disturb} onValueChange={(v) => handleToggle('never_disturb', v)} />
            </View>
            <Text style={styles.description}>Silences all notifications indefinitely until turned off.</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212' },
  centerContainer: { flex: 1, backgroundColor: '#121212', justifyContent: 'center', alignItems: 'center' },
  scrollContent: { padding: 20 },
  headerTitle: { color: '#fff', fontSize: 24, fontWeight: 'bold', marginBottom: 20 },
  card: { backgroundColor: '#1e1e1e', borderRadius: 12, padding: 20 },
  settingRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 5 },
  settingLabel: { color: '#fff', fontSize: 16 },
  description: { color: '#888', fontSize: 13, marginBottom: 20, fontStyle: 'italic' },
});
