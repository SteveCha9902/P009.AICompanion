import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getStoryChapters, getSharedTimeline, getLifeEvents, generateNarrative } from '../features/memory/services/memoryTimelineService';
import { StoryChapterData, TimelineEventData, LifeEventData } from '../features/memory/domain/timeline';

export function SharedStoryScreen({ navigation }: any) {
  const [chapters, setChapters] = useState<StoryChapterData[]>([]);
  const [timeline, setTimeline] = useState<TimelineEventData[]>([]);
  const [lifeEvents, setLifeEvents] = useState<LifeEventData[]>([]);
  const [narrative, setNarrative] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStoryData();
  }, []);

  const loadStoryData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [chData, timeData, lifeData] = await Promise.all([
        getStoryChapters(),
        getSharedTimeline(),
        getLifeEvents()
      ]);
      setChapters(chData);
      setTimeline(timeData);
      setLifeEvents(lifeData);
    } catch (err: any) {
      console.error("[SharedStoryScreen] Load error:", err);
      setError("우리의 이야기를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateNarrative = async () => {
    try {
      setGenerating(true);
      const res = await generateNarrative();
      setNarrative(res.narrative);
    } catch (err: any) {
      console.error("[SharedStoryScreen] Narrative error:", err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Top Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backButtonText}>← 뒤로</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Our Shared Story</Text>
        <TouchableOpacity onPress={loadStoryData} style={styles.refreshButton}>
          <Text style={styles.refreshButtonText}>새로고침</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#0A84FF" />
          <Text style={styles.loadingText}>우리가 함께한 서사 불러오는 중...</Text>
        </View>
      ) : error ? (
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadStoryData}>
            <Text style={styles.retryButtonText}>다시 시도</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Hero Banner */}
          <View style={styles.heroCard}>
            <Text style={styles.heroSub}>AUTOBIOGRAPHICAL MEMORY</Text>
            <Text style={styles.heroTitle}>우리가 함께 쌓아온 이야기</Text>
            <Text style={styles.heroDescription}>
              단순한 대화 기록을 넘어, 우리가 함께 나누고 고민하며 극복해 온 삶의 순간들입니다.
            </Text>
            <TouchableOpacity 
              style={styles.narrativeButton} 
              onPress={handleGenerateNarrative}
              disabled={generating}
            >
              {generating ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text style={styles.narrativeButtonText}>✨ 지니의 이야기 회고 듣기</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Narrative Speech Bubble if Generated */}
          {narrative && (
            <View style={styles.narrativeCard}>
              <Text style={styles.narrativeHeader}>🎙️ 지니의 회고</Text>
              <Text style={styles.narrativeText}>{narrative}</Text>
            </View>
          )}

          {/* Story Chapters */}
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>📚 Story Chapters (서사 챕터)</Text>
            {chapters.map((ch) => (
              <View style={styles.chapterCard} key={ch.id}>
                <View style={styles.chapterHeader}>
                  <View style={styles.chapterNumberBadge}>
                    <Text style={styles.chapterNumberText}>Chapter {ch.chapter_number}</Text>
                  </View>
                  <Text style={styles.chapterTheme}>{ch.theme}</Text>
                </View>
                <Text style={styles.chapterTitle}>{ch.title}</Text>
                <Text style={styles.chapterSummary}>{ch.summary}</Text>
              </View>
            ))}
          </View>

          {/* Life Milestones Timeline */}
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>🌟 Shared Life Timeline (주요 마일스톤)</Text>
            {timeline.length > 0 ? (
              timeline.map((ev, idx) => (
                <View style={styles.timelineItem} key={ev.id || idx}>
                  <View style={styles.timelineDot} />
                  <View style={styles.timelineBody}>
                    <Text style={styles.timelineTitle}>{ev.title}</Text>
                    <Text style={styles.timelineSummary}>{ev.summary}</Text>
                    <Text style={styles.timelineDate}>
                      {new Date(ev.occurred_at).toLocaleDateString('ko-KR')}
                    </Text>
                  </View>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>첫 번째 공동 마일스톤이 곧 시작됩니다.</Text>
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
  backButton: { padding: 6 },
  backButtonText: { color: '#0A84FF', fontSize: 16, fontWeight: 'bold' },
  headerTitle: { color: '#ffffff', fontSize: 18, fontWeight: 'bold' },
  refreshButton: { padding: 6 },
  refreshButtonText: { color: '#0A84FF', fontSize: 14, fontWeight: '600' },

  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  loadingText: { color: '#8e8e93', marginTop: 12, fontSize: 14 },
  errorText: { color: '#ff453a', fontSize: 15, marginBottom: 12 },
  retryButton: { backgroundColor: '#333', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 16 },
  retryButtonText: { color: '#fff', fontSize: 14 },

  scrollContent: { padding: 16, gap: 20 },
  heroCard: { backgroundColor: 'rgba(28, 28, 30, 0.9)', borderRadius: 20, padding: 20, borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.15)' },
  heroSub: { color: '#64D2FF', fontSize: 11, fontWeight: 'bold', letterSpacing: 1 },
  heroTitle: { color: '#ffffff', fontSize: 22, fontWeight: 'bold', marginVertical: 6 },
  heroDescription: { color: '#8e8e93', fontSize: 13, lineHeight: 18, marginBottom: 14 },
  narrativeButton: { backgroundColor: '#0A84FF', paddingVertical: 10, borderRadius: 14, alignItems: 'center' },
  narrativeButtonText: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' },

  narrativeCard: { backgroundColor: 'rgba(44, 44, 46, 0.85)', borderRadius: 18, padding: 16, borderWidth: 1, borderColor: '#FF9500' },
  narrativeHeader: { color: '#FF9500', fontSize: 14, fontWeight: 'bold', marginBottom: 8 },
  narrativeText: { color: '#ffffff', fontSize: 13, lineHeight: 20 },

  sectionContainer: { gap: 12 },
  sectionTitle: { color: '#ffffff', fontSize: 17, fontWeight: 'bold' },
  chapterCard: { backgroundColor: 'rgba(28, 28, 30, 0.85)', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.1)' },
  chapterHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  chapterNumberBadge: { backgroundColor: 'rgba(10, 132, 255, 0.25)', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8 },
  chapterNumberText: { color: '#64D2FF', fontSize: 11, fontWeight: 'bold' },
  chapterTheme: { color: '#8e8e93', fontSize: 11 },
  chapterTitle: { color: '#ffffff', fontSize: 16, fontWeight: 'bold', marginBottom: 4 },
  chapterSummary: { color: '#8e8e93', fontSize: 12, lineHeight: 17 },

  timelineItem: { flexDirection: 'row', gap: 12, alignItems: 'flex-start', marginBottom: 12 },
  timelineDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#30D158', marginTop: 5 },
  timelineBody: { flex: 1 },
  timelineTitle: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' },
  timelineSummary: { color: '#8e8e93', fontSize: 12, marginTop: 2, lineHeight: 16 },
  timelineDate: { color: '#636366', fontSize: 10, marginTop: 4 },
  emptyText: { color: '#8e8e93', fontSize: 13, fontStyle: 'italic' }
});
