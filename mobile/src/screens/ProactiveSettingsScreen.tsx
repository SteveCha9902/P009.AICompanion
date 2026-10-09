import React, { useState } from 'react';
import { View, Text, StyleSheet, Switch, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export function ProactiveSettingsScreen({ navigation }: any) {
  const [proactiveEnabled, setProactiveEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [routineSuggestions, setRoutineSuggestions] = useState(true);
  const [goalReminders, setGoalReminders] = useState(true);
  const [memorySuggestions, setMemorySuggestions] = useState(true);

  const showWhyDialog = () => {
    Alert.alert(
      "컴패니언의 알림 원칙",
      "컴패니언은 다음과 같은 원칙으로 먼저 말을 겁니다:\n\n• 사용자가 대화하는 주요 시간대\n• 이전에 이야기했던 중요한 목표나 기억\n• 방해 금지 시간대(22:00~07:00) 준수\n• 하루 최대 3회 이내의 보수적인 알림\n• 불필요할 때는 조용히 기다립니다.",
      [{ text: "확인" }]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Proactive Companion</Text>
        <TouchableOpacity onPress={showWhyDialog}>
          <Text style={styles.whyText}>원칙 보기</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>기본 설정</Text>
          
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>먼저 말 걸기 (Proactive)</Text>
              <Text style={styles.settingDesc}>적절한 순간에 컴패니언이 먼저 말을 겁니다.</Text>
            </View>
            <Switch 
              value={proactiveEnabled} 
              onValueChange={setProactiveEnabled}
              trackColor={{ false: '#3a3a3c', true: '#30D158' }}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>푸시 알림 허용</Text>
              <Text style={styles.settingDesc}>앱이 닫혀 있을 때 로컬 알림을 수신합니다.</Text>
            </View>
            <Switch 
              value={notificationsEnabled} 
              onValueChange={setNotificationsEnabled}
              trackColor={{ false: '#3a3a3c', true: '#30D158' }}
              disabled={!proactiveEnabled}
            />
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>맥락 및 루틴</Text>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>일상 루틴 감지 및 제안</Text>
              <Text style={styles.settingDesc}>자주 대화하는 시간대에 맞춘 가벼운 체크인.</Text>
            </View>
            <Switch 
              value={routineSuggestions} 
              onValueChange={setRoutineSuggestions}
              trackColor={{ false: '#3a3a3c', true: '#30D158' }}
              disabled={!proactiveEnabled}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>목표 리마인더 (Goal)</Text>
              <Text style={styles.settingDesc}>이전에 이야기한 프로젝트나 목표를 상기합니다.</Text>
            </View>
            <Switch 
              value={goalReminders} 
              onValueChange={setGoalReminders}
              trackColor={{ false: '#3a3a3c', true: '#30D158' }}
              disabled={!proactiveEnabled}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>기억 기반 대화 주제 제안</Text>
              <Text style={styles.settingDesc}>관심사나 선호도를 바탕으로 새로운 주제를 제안합니다.</Text>
            </View>
            <Switch 
              value={memorySuggestions} 
              onValueChange={setMemorySuggestions}
              trackColor={{ false: '#3a3a3c', true: '#30D158' }}
              disabled={!proactiveEnabled}
            />
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>보호 정책 (Anti-Spam)</Text>
          <View style={styles.policyCard}>
            <Text style={styles.policyItem}>• 일일 최대 알림: 3회 제한</Text>
            <Text style={styles.policyItem}>• 재알림 쿨다운: 최소 4시간</Text>
            <Text style={styles.policyItem}>• 방해 금지 시간: 22:00 ~ 07:00</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderColor: '#2c2c2e' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#ffffff' },
  whyText: { color: '#0A84FF', fontSize: 14, fontWeight: '600' },
  content: { padding: 16, gap: 20 },
  section: { backgroundColor: '#1c1c1e', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#2c2c2e' },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#ffffff', marginBottom: 12 },
  settingRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderColor: '#2c2c2e' },
  settingInfo: { flex: 1, marginRight: 12 },
  settingLabel: { fontSize: 15, fontWeight: '600', color: '#ffffff' },
  settingDesc: { fontSize: 12, color: '#8e8e93', marginTop: 2 },
  policyCard: { backgroundColor: '#2c2c2e', padding: 12, borderRadius: 8, gap: 6 },
  policyItem: { color: '#30D158', fontSize: 13, fontWeight: '500' }
});
