import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export function MemoriesScreen({ navigation }: any) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Memories & Story</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.card}>
          <Text style={styles.cardHeader}>📖 Autobiographical Memory</Text>
          <Text style={styles.cardTitle}>우리가 함께한 시간과 공동 역사</Text>
          <Text style={styles.cardDesc}>
            단순한 단편 기억을 넘어, 지니와 함께 극복하고 완성해 온 프로젝트와 이야기 챕터를 확인하세요.
          </Text>

          <TouchableOpacity 
            style={styles.storyButton}
            onPress={() => navigation.navigate('SharedStory')}
          >
            <Text style={styles.storyButtonText}>✨ 우리의 이야기 타임라인 보기 →</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000000' },
  header: { paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, borderColor: '#222' },
  headerTitle: { color: '#ffffff', fontSize: 18, fontWeight: 'bold' },
  content: { flex: 1, padding: 16, justifyContent: 'center' },
  card: { backgroundColor: 'rgba(28, 28, 30, 0.9)', borderRadius: 20, padding: 22, borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.15)' },
  cardHeader: { color: '#64D2FF', fontSize: 12, fontWeight: 'bold', letterSpacing: 1, marginBottom: 6 },
  cardTitle: { color: '#ffffff', fontSize: 20, fontWeight: 'bold', marginBottom: 10 },
  cardDesc: { color: '#8e8e93', fontSize: 13, lineHeight: 19, marginBottom: 20 },
  storyButton: { backgroundColor: '#0A84FF', paddingVertical: 12, borderRadius: 14, alignItems: 'center' },
  storyButtonText: { color: '#ffffff', fontSize: 15, fontWeight: 'bold' }
});
