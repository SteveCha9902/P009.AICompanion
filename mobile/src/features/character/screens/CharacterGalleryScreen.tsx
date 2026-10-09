import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useCharacterStore } from '../../../state/useCharacterStore';
import { CharacterSummary } from '../services/characterApi';

const getCharacterEmoji = (name: string, role: string) => {
  if (name.includes('지니') || role.includes('아내')) return '💖';
  if (name.includes('마니') || role.includes('딸')) return '💕';
  if (name.includes('하나') || role.includes('친구')) return '🎨';
  return '🤖';
};

export const CharacterGalleryScreen: React.FC<{
  navigation?: any;
  onSelectCharacter?: (char: CharacterSummary) => void;
  onOpenWizard?: () => void;
}> = ({ navigation, onSelectCharacter, onOpenWizard }) => {
  const {
    characterList,
    activeCharacterId,
    isLoading,
    isSwitching,
    error,
    fetchCharacters,
    switchCharacter,
    clearError
  } = useCharacterStore();

  useEffect(() => {
    fetchCharacters();
  }, []);

  useEffect(() => {
    if (error) {
      Alert.alert('알림', error, [{ text: '확인', onPress: clearError }]);
    }
  }, [error]);

  const handleSelectCharacter = async (item: CharacterSummary) => {
    if (item.companion_id === activeCharacterId) return;

    const success = await switchCharacter(item.companion_id);
    if (success) {
      if (onSelectCharacter) onSelectCharacter(item);
    }
  };

  const handleCreateNew = () => {
    if (onOpenWizard) {
      onOpenWizard();
    } else if (navigation) {
      navigation.navigate('CharacterCreationWizard');
    }
  };

  const renderCharacterCard = ({ item }: { item: CharacterSummary }) => {
    const isActive = item.companion_id === activeCharacterId;
    const emoji = getCharacterEmoji(item.name, item.role_title);

    return (
      <TouchableOpacity
        style={[styles.card, isActive && styles.activeCard]}
        onPress={() => handleSelectCharacter(item)}
        disabled={isSwitching}
        activeOpacity={0.8}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.emoji}>{emoji}</Text>
          {isActive && (
            <View style={styles.activeBadge}>
              <Text style={styles.activeBadgeText}>✓ Active</Text>
            </View>
          )}
        </View>

        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.roleTitle}>{item.role_title}</Text>

        <View style={styles.cardFooter}>
          <Text style={styles.voiceInfo}>🎙️ {item.voice_name || 'Standard Voice'}</Text>
          {isSwitching && isActive && (
            <ActivityIndicator size="small" color="#38bdf8" />
          )}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Top Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🎭 Character Gallery</Text>
        <TouchableOpacity style={styles.createButton} onPress={handleCreateNew}>
          <Text style={styles.createButtonText}>＋ 새 캐릭터</Text>
        </TouchableOpacity>
      </View>

      {isLoading && characterList.length === 0 ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#38bdf8" />
          <Text style={styles.loadingText}>캐릭터 목록 불러오는 중...</Text>
        </View>
      ) : (
        <FlatList
          data={characterList}
          keyExtractor={(item) => item.companion_id}
          renderItem={renderCharacterCard}
          numColumns={2}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>등록된 캐릭터가 없습니다.</Text>
            </View>
          }
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderColor: '#334155',
    backgroundColor: '#1e293b'
  },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: '#f8fafc' },
  createButton: {
    backgroundColor: '#2563eb',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20
  },
  createButtonText: { color: '#ffffff', fontWeight: 'bold', fontSize: 13 },
  listContent: { padding: 12 },
  card: {
    flex: 1,
    margin: 8,
    padding: 16,
    backgroundColor: '#1e293b',
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: '#334155',
    minHeight: 150,
    justifyContent: 'space-between'
  },
  activeCard: {
    borderColor: '#38bdf8',
    backgroundColor: '#0c2d48'
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  emoji: { fontSize: 28 },
  activeBadge: {
    backgroundColor: '#0284c7',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12
  },
  activeBadgeText: { color: '#ffffff', fontSize: 10, fontWeight: 'bold' },
  name: { fontSize: 18, fontWeight: 'bold', color: '#f8fafc', marginTop: 12 },
  roleTitle: { fontSize: 13, color: '#94a3b8', marginTop: 4 },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 },
  voiceInfo: { fontSize: 11, color: '#64748b' },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { color: '#94a3b8', marginTop: 12, fontSize: 14 },
  emptyContainer: { padding: 40, alignItems: 'center' },
  emptyText: { color: '#64748b', fontSize: 14 }
});
