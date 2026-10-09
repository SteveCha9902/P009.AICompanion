import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getCurrentRelationship, getRelationshipTimeline } from '../features/relationship/services/relationshipService';
import { CurrentRelationshipResponse, RelationshipTimelineResponse } from '../features/relationship/domain/relationshipProfile';

export function RelationshipScreen({ navigation }: any) {
  const [relData, setRelData] = useState<CurrentRelationshipResponse | null>(null);
  const [timeline, setTimeline] = useState<RelationshipTimelineResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRelationship();
  }, []);

  const loadRelationship = async () => {
    try {
      setLoading(true);
      setError(null);
      const [current, time] = await Promise.all([
        getCurrentRelationship(),
        getRelationshipTimeline()
      ]);
      setRelData(current);
      setTimeline(time);
    } catch (err: any) {
      console.error("[RelationshipScreen] Load error:", err);
      setError("관계 정보를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const renderBondBar = (label: string, value: number, color: string = "#0A84FF") => {
    const percent = Math.round(value * 100);
    return (
      <View style={styles.bondRow} key={label}>
        <View style={styles.bondLabelRow}>
          <Text style={styles.bondLabel}>{label}</Text>
          <Text style={styles.bondPercent}>{percent}%</Text>
        </View>
        <View style={styles.progressBackground}>
          <View style={[styles.progressFill, { width: `${percent}%`, backgroundColor: color }]} />
        </View>
      </View>
    );
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'trusted_companion': return '#BF5AF2';
      case 'close_friend': return '#FF2D55';
      case 'friend': return '#30D158';
      case 'acquaintance': return '#0A84FF';
      default: return '#8E8E93';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Top Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Our Relationship</Text>
        <TouchableOpacity onPress={loadRelationship} style={styles.refreshButton}>
          <Text style={styles.refreshButtonText}>새로고침</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#0A84FF" />
          <Text style={styles.loadingText}>소셜 본드 불러오는 중...</Text>
        </View>
      ) : error || !relData ? (
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadRelationship}>
            <Text style={styles.retryButtonText}>다시 시도</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Stage Card */}
          <View style={styles.card}>
            <View style={styles.stageHeader}>
              <View style={[styles.stageBadge, { borderColor: getStageColor(relData.stage) }]}>
                <Text style={[styles.stageBadgeText, { color: getStageColor(relData.stage) }]}>
                  {relData.stage_display}
                </Text>
              </View>
              <Text style={styles.conversationCountText}>
                함께 나눈 대화: <Text style={styles.highlightNumber}>{relData.total_conversations}</Text>회
              </Text>
            </View>
            <Text style={styles.stageDescription}>
              지니와 깊은 신뢰와 정서적 유대를 나누며 점진적으로 성숙해진 관계입니다.
            </Text>
          </View>

          {/* 7-Dimensional Social Bond Card */}
          <View style={styles.card}>
            <Text style={styles.cardSectionTitle}>💞 7-Dimensional Social Bond</Text>
            {renderBondBar("Familiarity (친숙함)", relData.dimensions.familiarity, "#64D2FF")}
            {renderBondBar("Trust (상호 신뢰)", relData.dimensions.trust, "#30D158")}
            {renderBondBar("Affection (호감과 애정)", relData.dimensions.affection, "#FF2D55")}
            {renderBondBar("Comfort (편안함과 자연스러움)", relData.dimensions.comfort, "#FF9500")}
            {renderBondBar("Respect (서로에 대한 존중)", relData.dimensions.respect, "#5E5CE6")}
            {renderBondBar("Intimacy (속마음의 깊이)", relData.dimensions.intimacy, "#BF5AF2")}
            {renderBondBar("Attachment (정서적 연결)", relData.dimensions.attachment, "#FFD60A")}
          </View>

          {/* Relationship Milestones & Timeline Anchors */}
          <View style={styles.card}>
            <Text style={styles.cardSectionTitle}>📖 Our Shared Journey (관계 마일스톤)</Text>
            {timeline?.milestones && timeline.milestones.length > 0 ? (
              timeline.milestones.map((m, idx) => (
                <View style={styles.milestoneItem} key={idx}>
                  <View style={styles.milestoneDot} />
                  <View style={styles.milestoneContent}>
                    <Text style={styles.milestoneSummary}>{m.summary}</Text>
                    <Text style={styles.milestoneDate}>
                      {new Date(m.created_at).toLocaleDateString('ko-KR')}
                    </Text>
                  </View>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>첫 대화를 시작하면 소중한 마일스톤이 기록됩니다.</Text>
            )}
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000000' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, borderColor: '#222' },
  headerTitle: { color: '#ffffff', fontSize: 18, fontWeight: 'bold' },
  refreshButton: { padding: 6 },
  refreshButtonText: { color: '#0A84FF', fontSize: 14, fontWeight: '600' },

  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  loadingText: { color: '#8e8e93', marginTop: 12, fontSize: 14 },
  errorText: { color: '#ff453a', fontSize: 15, marginBottom: 12 },
  retryButton: { backgroundColor: '#333', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 16 },
  retryButtonText: { color: '#fff', fontSize: 14 },

  scrollContent: { padding: 16, gap: 16 },
  card: { backgroundColor: 'rgba(28, 28, 30, 0.85)', borderRadius: 20, padding: 18, borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.12)' },

  stageHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  stageBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 14, borderWidth: 1.5, backgroundColor: 'rgba(0,0,0,0.5)' },
  stageBadgeText: { fontSize: 14, fontWeight: 'bold' },
  conversationCountText: { color: '#8e8e93', fontSize: 13 },
  highlightNumber: { color: '#ffffff', fontWeight: 'bold' },
  stageDescription: { color: '#e5e5ea', fontSize: 13, lineHeight: 18 },

  cardSectionTitle: { color: '#ffffff', fontSize: 16, fontWeight: 'bold', marginBottom: 14 },
  bondRow: { marginBottom: 10 },
  bondLabelRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  bondLabel: { color: '#e5e5ea', fontSize: 13, fontWeight: '500' },
  bondPercent: { color: '#8e8e93', fontSize: 12, fontWeight: '600' },
  progressBackground: { height: 8, backgroundColor: '#2c2c2e', borderRadius: 4, overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: 4 },

  milestoneItem: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 14 },
  milestoneDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#0A84FF', marginTop: 5 },
  milestoneContent: { flex: 1 },
  milestoneSummary: { color: '#ffffff', fontSize: 13, fontWeight: '500', lineHeight: 18 },
  milestoneDate: { color: '#8e8e93', fontSize: 11, marginTop: 2 },
  emptyText: { color: '#8e8e93', fontSize: 13, fontStyle: 'italic' }
});
