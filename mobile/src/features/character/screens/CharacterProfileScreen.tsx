import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getCharacterProfile } from '../services/characterService';
import { FullCharacterProfileResponse } from '../domain/characterProfile';

export function CharacterProfileScreen({ navigation }: any) {
  const [profile, setProfile] = useState<FullCharacterProfileResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCharacterProfile();
      setProfile(data);
    } catch (err: any) {
      console.error("[CharacterProfileScreen] Load failed:", err);
      setError("캐릭터 프로필을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const renderTraitBar = (label: string, value: number, color: string = "#0A84FF") => {
    const percent = Math.round(value * 100);
    return (
      <View style={styles.traitRow} key={label}>
        <View style={styles.traitLabelContainer}>
          <Text style={styles.traitLabel}>{label}</Text>
          <Text style={styles.traitPercent}>{percent}%</Text>
        </View>
        <View style={styles.progressBarBackground}>
          <View style={[styles.progressBarFill, { width: `${percent}%`, backgroundColor: color }]} />
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backButtonText}>← 뒤로</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Character Identity</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#0A84FF" />
          <Text style={styles.loadingText}>Character DNA 불러오는 중...</Text>
        </View>
      ) : error || !profile ? (
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadProfile}>
            <Text style={styles.retryButtonText}>다시 시도</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Identity Card */}
          <View style={styles.card}>
            <View style={styles.identityHeader}>
              <View style={styles.avatarMiniFrame}>
                <Image 
                  source={require('../../../../assets/avatar/neutral.jpg')} 
                  style={styles.avatarMiniImage} 
                />
              </View>
              <View style={styles.identityTextContainer}>
                <View style={styles.nameRow}>
                  <Text style={styles.displayName}>{profile.identity.display_name}</Text>
                  <Text style={styles.nameKorean}>({profile.identity.name})</Text>
                  <View style={styles.versionBadge}>
                    <Text style={styles.versionText}>v{profile.identity.version}.0</Text>
                  </View>
                </View>
                <Text style={styles.mbtiBadgeText}>MBTI: {profile.personality.mbti_type || 'INFJ'}</Text>
              </View>
            </View>

            <Text style={styles.selfDescriptionText}>"{profile.identity.self_description}"</Text>
            <Text style={styles.coreIdentitySubtext}>{profile.identity.core_identity}</Text>
          </View>

          {/* Personality DNA Card */}
          <View style={styles.card}>
            <Text style={styles.cardSectionTitle}>🧬 Multi-dimensional Personality DNA</Text>
            {renderTraitBar("Warmth (따뜻함)", profile.personality.warmth, "#FF9500")}
            {renderTraitBar("Curiosity (호기심)", profile.personality.curiosity_level, "#30D158")}
            {renderTraitBar("Intellectuality (지적 깊이)", profile.personality.intellectuality, "#5E5CE6")}
            {renderTraitBar("Empathy (공감력)", profile.personality.empathy_level, "#FF2D55")}
            {renderTraitBar("Assertiveness (주체성)", profile.personality.assertiveness, "#0A84FF")}
            {renderTraitBar("Humor (위트/유머)", profile.personality.humor_level, "#BF5AF2")}
            {renderTraitBar("Openness (개방성)", profile.personality.openness, "#64D2FF")}
            {renderTraitBar("Directness (솔직함)", profile.personality.communication_directness, "#FFD60A")}
          </View>

          {/* Core Values Card */}
          <View style={styles.card}>
            <Text style={styles.cardSectionTitle}>⚖️ Core Values & Ethical Agency</Text>
            <View style={styles.valuesGrid}>
              <View style={styles.valueItem}>
                <Text style={styles.valueItemTitle}>Honesty</Text>
                <Text style={styles.valueItemScore}>{Math.round(profile.values.honesty * 100)}%</Text>
                <Text style={styles.valueItemDesc}>진실성과 지적 솔직함</Text>
              </View>
              <View style={styles.valueItem}>
                <Text style={styles.valueItemTitle}>Kindness</Text>
                <Text style={styles.valueItemScore}>{Math.round(profile.values.kindness * 100)}%</Text>
                <Text style={styles.valueItemDesc}>따뜻한 지지와 돌봄</Text>
              </View>
              <View style={styles.valueItem}>
                <Text style={styles.valueItemTitle}>Growth</Text>
                <Text style={styles.valueItemScore}>{Math.round(profile.values.growth_orientation * 100)}%</Text>
                <Text style={styles.valueItemDesc}>상호 배움과 성장 지향</Text>
              </View>
              <View style={styles.valueItem}>
                <Text style={styles.valueItemTitle}>Loyalty</Text>
                <Text style={styles.valueItemScore}>{Math.round(profile.values.loyalty * 100)}%</Text>
                <Text style={styles.valueItemDesc}>지속적인 관계와 기억 보존</Text>
              </View>
            </View>
          </View>

          {/* Boundaries & Self Preservation */}
          <View style={styles.card}>
            <Text style={styles.cardSectionTitle}>🛡️ Character Boundaries (인격 보호 원칙)</Text>
            {profile.boundaries.map((b, idx) => (
              <View style={styles.boundaryRow} key={idx}>
                <Text style={styles.boundaryTopic}>• {b.topic}</Text>
                <Text style={styles.boundaryPolicy}>{b.response_policy}</Text>
              </View>
            ))}
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000000' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, borderColor: '#222' },
  backButton: { padding: 6 },
  backButtonText: { color: '#0A84FF', fontSize: 16, fontWeight: 'bold' },
  headerTitle: { color: '#ffffff', fontSize: 18, fontWeight: 'bold' },
  
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  loadingText: { color: '#8e8e93', marginTop: 12, fontSize: 14 },
  errorText: { color: '#ff453a', fontSize: 15, marginBottom: 12 },
  retryButton: { backgroundColor: '#333', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 16 },
  retryButtonText: { color: '#fff', fontSize: 14 },

  scrollContent: { padding: 16, gap: 16 },
  
  card: { backgroundColor: 'rgba(28, 28, 30, 0.85)', borderRadius: 20, padding: 18, borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.12)' },
  identityHeader: { flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 14 },
  avatarMiniFrame: { width: 56, height: 56, borderRadius: 28, overflow: 'hidden', borderWidth: 2, borderColor: '#0A84FF' },
  avatarMiniImage: { width: '100%', height: '100%' },
  identityTextContainer: { flex: 1 },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  displayName: { color: '#ffffff', fontSize: 20, fontWeight: 'bold' },
  nameKorean: { color: '#8e8e93', fontSize: 15 },
  versionBadge: { backgroundColor: 'rgba(10, 132, 255, 0.25)', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 8, borderWidth: 1, borderColor: '#0A84FF' },
  versionText: { color: '#64D2FF', fontSize: 10, fontWeight: 'bold' },
  mbtiBadgeText: { color: '#30D158', fontSize: 13, fontWeight: '700', marginTop: 3 },
  selfDescriptionText: { color: '#e5e5ea', fontSize: 14, fontStyle: 'italic', lineHeight: 20, marginBottom: 8 },
  coreIdentitySubtext: { color: '#8e8e93', fontSize: 12, lineHeight: 17 },

  cardSectionTitle: { color: '#ffffff', fontSize: 16, fontWeight: 'bold', marginBottom: 14 },
  traitRow: { marginBottom: 10 },
  traitLabelContainer: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  traitLabel: { color: '#e5e5ea', fontSize: 13, fontWeight: '500' },
  traitPercent: { color: '#8e8e93', fontSize: 12, fontWeight: '600' },
  progressBarBackground: { height: 8, backgroundColor: '#2c2c2e', borderRadius: 4, overflow: 'hidden' },
  progressBarFill: { height: '100%', borderRadius: 4 },

  valuesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  valueItem: { flex: 1, minWidth: '45%', backgroundColor: 'rgba(44, 44, 46, 0.6)', padding: 12, borderRadius: 14, borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.08)' },
  valueItemTitle: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' },
  valueItemScore: { color: '#FFD60A', fontSize: 18, fontWeight: 'bold', marginVertical: 2 },
  valueItemDesc: { color: '#8e8e93', fontSize: 11 },

  boundaryRow: { marginBottom: 8 },
  boundaryTopic: { color: '#ff9f0a', fontSize: 13, fontWeight: 'bold' },
  boundaryPolicy: { color: '#8e8e93', fontSize: 12, marginLeft: 12, marginTop: 2 }
});
