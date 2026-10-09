import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export interface MemoryItemUI {
  id: string;
  type: 'FACT' | 'PREFERENCE' | 'EVENT' | 'GOAL' | 'RELATIONSHIP_EVENT';
  content: string;
  importance: number;
  createdAt: string;
}

const INITIAL_MEMORIES: MemoryItemUI[] = [
  { id: '1', type: 'FACT', content: '사용자는 카메라 및 컴퓨터 비전 개발을 진행 중이다.', importance: 0.9, createdAt: '2026-08-20' },
  { id: '2', type: 'PREFERENCE', content: '기술적인 배경 설명을 선호한다.', importance: 0.85, createdAt: '2026-08-22' },
  { id: '3', type: 'GOAL', content: 'AICompanion Android v1.0 정식 릴리즈 완료.', importance: 0.95, createdAt: '2026-08-25' },
  { id: '4', type: 'EVENT', content: '주말에 새로운 사진 촬영 계획이 있음.', importance: 0.75, createdAt: '2026-08-28' },
];

export function MemoryScreen({ navigation }: any) {
  const [memories, setMemories] = useState<MemoryItemUI[]>(INITIAL_MEMORIES);

  const handleDeleteMemory = (id: string) => {
    Alert.alert(
      "기억 삭제",
      "이 기억을 삭제하시겠습니까? Companion이 더 이상 기억하지 않습니다.",
      [
        { text: "취소", style: "cancel" },
        { 
          text: "삭제", 
          style: "destructive", 
          onPress: () => {
            setMemories(prev => prev.filter(m => m.id !== id));
          }
        }
      ]
    );
  };

  const handleClearAll = () => {
    Alert.alert(
      "모든 기억 초기화",
      "모든 장기 기억을 삭제하시겠습니까? 되돌릴 수 없습니다.",
      [
        { text: "취소", style: "cancel" },
        { 
          text: "전체 삭제", 
          style: "destructive", 
          onPress: () => setMemories([]) 
        }
      ]
    );
  };

  const renderItem = ({ item }: { item: MemoryItemUI }) => (
    <View style={styles.memoryCard}>
      <View style={styles.cardHeader}>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{item.type}</Text>
        </View>
        <Text style={styles.dateText}>{item.createdAt}</Text>
      </View>
      <Text style={styles.contentText}>{item.content}</Text>
      <View style={styles.cardFooter}>
        <Text style={styles.importanceText}>중요도: {Math.round(item.importance * 100)}%</Text>
        <TouchableOpacity onPress={() => handleDeleteMemory(item.id)}>
          <Text style={styles.deleteText}>삭제</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Companion Memories</Text>
        <TouchableOpacity onPress={handleClearAll}>
          <Text style={styles.clearAllText}>전체 삭제</Text>
        </TouchableOpacity>
      </View>

      {memories.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>저장된 장기 기억이 없습니다.</Text>
        </View>
      ) : (
        <FlatList
          data={memories}
          keyExtractor={item => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderColor: '#2c2c2e' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#ffffff' },
  clearAllText: { color: '#FF453A', fontSize: 14, fontWeight: '600' },
  listContent: { padding: 16, gap: 12 },
  memoryCard: { backgroundColor: '#1c1c1e', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#2c2c2e' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  badge: { backgroundColor: '#0A84FF22', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, borderWidth: 1, borderColor: '#0A84FF' },
  badgeText: { color: '#0A84FF', fontSize: 11, fontWeight: 'bold' },
  dateText: { color: '#8e8e93', fontSize: 12 },
  contentText: { color: '#ffffff', fontSize: 15, lineHeight: 22, marginBottom: 12 },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  importanceText: { color: '#30D158', fontSize: 12, fontWeight: '500' },
  deleteText: { color: '#FF453A', fontSize: 13, fontWeight: '600' },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { color: '#8e8e93', fontSize: 15 }
});
