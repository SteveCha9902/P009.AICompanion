import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert
} from 'react-native';
import { characterCreationApi, CharacterPreviewPayload, CharacterPreviewData } from '../services/characterCreationApi';

export const CharacterCreationWizardScreen: React.FC<{ navigation?: any; onCreated?: () => void }> = ({
  navigation,
  onCreated
}) => {
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [previewData, setPreviewData] = useState<CharacterPreviewData | null>(null);

  // Form State
  const [formData, setFormData] = useState<CharacterPreviewPayload>({
    name: '마니',
    role_title: '사랑스러운 딸',
    tagline: '툴툴거리지만 아빠를 제일 좋아하는 중2 딸',
    template_id: 'lovely_daughter',
    relationship_type: 'family',
    mbti: 'ESFP',
    personality_keywords: ['bright', 'playful', 'shyness', 'affectionate'],
    interests: ['노래', 'BLACKPINK', '미술', '그림 그리기', '미술학원'],
    speaking_style: 'daughter_teen_natural',
    speech_profile: { tone: 'bright', formality: 'casual', emoji_usage: 'moderate' },
    voice_id: 'shimmer',
    avatar_preset: 'lovely_daughter_2d',
    behavior_rules: [
      '상대방의 말을 먼저 이해하려고 한다',
      '아빠에게는 부끄러움으로 툴툴거리지만 속으로는 깊이 사랑한다',
      '자신의 정체성을 임의로 변경하지 않는다'
    ],
    origin_story: '아빠를 매우 사랑하지만 부끄러움이 많은 중학교 2학년 딸.'
  });

  const handleNext = async () => {
    if (step === 7) {
      // Step 8: Fetch Preview
      setLoading(true);
      try {
        const preview = await characterCreationApi.previewCharacter(formData);
        setPreviewData(preview);
        setStep(8);
      } catch (err: any) {
        Alert.alert('미리보기 오류', err.message || '캐릭터 DNA 컴파일에 실패했습니다.');
      } finally {
        setLoading(false);
      }
    } else if (step < 8) {
      setStep(step + 1);
    }
  };

  const handlePrev = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleCreate = async () => {
    setLoading(true);
    try {
      const res = await characterCreationApi.createCharacter(formData);
      Alert.alert('생성 완료', `${res.name} 캐릭터가 성공적으로 생성되었습니다!`, [
        {
          text: '확인',
          onPress: () => {
            if (onCreated) onCreated();
            if (navigation) navigation.goBack();
          }
        }
      ]);
    } catch (err: any) {
      Alert.alert('생성 실패', err.message || '캐릭터 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Character Creation Studio</Text>
        <Text style={styles.stepIndicator}>Step {step} / 8</Text>
      </View>

      <ScrollView style={styles.body} contentContainerStyle={styles.bodyContent}>
        {step === 1 && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>1. 기본 정체성 (Basic Identity)</Text>
            <Text style={styles.label}>캐릭터 이름</Text>
            <TextInput
              style={styles.input}
              value={formData.name}
              onChangeText={(txt) => setFormData({ ...formData, name: txt })}
              placeholder="예: 마니"
            />
            <Text style={styles.label}>역할 타이틀</Text>
            <TextInput
              style={styles.input}
              value={formData.role_title}
              onChangeText={(txt) => setFormData({ ...formData, role_title: txt })}
              placeholder="예: 사랑스러운 딸"
            />
            <Text style={styles.label}>한 줄 소개 (Tagline)</Text>
            <TextInput
              style={styles.input}
              value={formData.tagline}
              onChangeText={(txt) => setFormData({ ...formData, tagline: txt })}
              placeholder="예: 툴툴거리지만 아빠를 제일 좋아하는 중2 딸"
            />
          </View>
        )}

        {step === 2 && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>2. 성격 및 MBTI (Personality)</Text>
            <Text style={styles.label}>아키타입 템플릿</Text>
            <TextInput
              style={styles.input}
              value={formData.template_id}
              onChangeText={(txt) => setFormData({ ...formData, template_id: txt })}
            />
            <Text style={styles.label}>MBTI</Text>
            <TextInput
              style={styles.input}
              value={formData.mbti}
              onChangeText={(txt) => setFormData({ ...formData, mbti: txt })}
            />
          </View>
        )}

        {step === 3 && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>3. 관계 설정 (Relationship)</Text>
            <Text style={styles.label}>관계 유형</Text>
            <TextInput
              style={styles.input}
              value={formData.relationship_type}
              onChangeText={(txt) => setFormData({ ...formData, relationship_type: txt })}
              placeholder="family, friend, romantic, mentor"
            />
          </View>
        )}

        {step === 4 && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>4. 관심사 및 취미 (Interests)</Text>
            <Text style={styles.label}>관심사 목록 (쉼표 구분)</Text>
            <TextInput
              style={styles.input}
              value={formData.interests?.join(', ')}
              onChangeText={(txt) =>
                setFormData({
                  ...formData,
                  interests: txt.split(',').map((s) => s.trim())
                })
              }
              placeholder="노래, BLACKPINK, 미술, 그림"
            />
          </View>
        )}

        {step === 5 && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>5. 말투 및 음성 (Speech & Voice)</Text>
            <Text style={styles.label}>음성 ID (Voice ID)</Text>
            <TextInput
              style={styles.input}
              value={formData.voice_id}
              onChangeText={(txt) => setFormData({ ...formData, voice_id: txt })}
              placeholder="shimmer, nova, alloy"
            />
            <Text style={styles.label}>말투 스타일</Text>
            <TextInput
              style={styles.input}
              value={formData.speaking_style}
              onChangeText={(txt) => setFormData({ ...formData, speaking_style: txt })}
            />
          </View>
        )}

        {step === 6 && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>6. 아바타 비주얼 (Avatar)</Text>
            <Text style={styles.label}>아바타 프리셋</Text>
            <TextInput
              style={styles.input}
              value={formData.avatar_preset}
              onChangeText={(txt) => setFormData({ ...formData, avatar_preset: txt })}
              placeholder="lovely_daughter_2d, warm_wife_2d"
            />
          </View>
        )}

        {step === 7 && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>7. 행동 규칙 (Behavior Rules)</Text>
            <Text style={styles.label}>행동 지침 (줄바꿈 구분)</Text>
            <TextInput
              style={[styles.input, styles.multilineInput]}
              multiline
              numberOfLines={4}
              value={formData.behavior_rules?.join('\n')}
              onChangeText={(txt) =>
                setFormData({
                  ...formData,
                  behavior_rules: txt.split('\n').filter((s) => s.trim().length > 0)
                })
              }
            />
          </View>
        )}

        {step === 8 && previewData && (
          <View style={styles.stepContainer}>
            <Text style={styles.sectionTitle}>8. 캐릭터 DNA 미리보기 (Preview)</Text>
            <View style={styles.previewCard}>
              <Text style={styles.previewName}>
                {previewData.name} ({previewData.role_title})
              </Text>
              <Text style={styles.previewTagline}>"{previewData.tagline}"</Text>
              <Text style={styles.previewDetail}>MBTI: {previewData.mbti}</Text>
              <Text style={styles.previewDetail}>Voice: {previewData.voice.voice_id} (OpenAI)</Text>
              <Text style={styles.previewDetail}>Avatar: {previewData.avatar.avatar_preset}</Text>
              <Text style={styles.previewDetail}>
                관심사: {previewData.interests?.join(', ')}
              </Text>
            </View>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        {step > 1 && (
          <TouchableOpacity style={[styles.button, styles.prevButton]} onPress={handlePrev}>
            <Text style={styles.prevButtonText}>이전</Text>
          </TouchableOpacity>
        )}
        {step < 8 ? (
          <TouchableOpacity style={[styles.button, styles.nextButton]} onPress={handleNext}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.nextButtonText}>{step === 7 ? '미리보기' : '다음'}</Text>
            )}
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={[styles.button, styles.createButton]} onPress={handleCreate}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.createButtonText}>캐릭터 생성 완료</Text>
            )}
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  header: { padding: 16, paddingTop: 48, backgroundColor: '#1e293b', borderBottomWidth: 1, borderColor: '#334155' },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#f8fafc' },
  stepIndicator: { fontSize: 12, color: '#94a3b8', marginTop: 4 },
  body: { flex: 1 },
  bodyContent: { padding: 16 },
  stepContainer: { gap: 12 },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#38bdf8', marginBottom: 8 },
  label: { fontSize: 13, fontWeight: '500', color: '#cbd5e1' },
  input: {
    backgroundColor: '#1e293b',
    color: '#f8fafc',
    borderRadius: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: '#334155'
  },
  multilineInput: { height: 100, textAlignVertical: 'top' },
  previewCard: { backgroundColor: '#1e293b', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#38bdf8', gap: 8 },
  previewName: { fontSize: 18, fontWeight: 'bold', color: '#f8fafc' },
  previewTagline: { fontSize: 14, fontStyle: 'italic', color: '#cbd5e1', marginBottom: 8 },
  previewDetail: { fontSize: 13, color: '#94a3b8' },
  footer: { flexDirection: 'row', padding: 16, backgroundColor: '#1e293b', gap: 12 },
  button: { flex: 1, padding: 14, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  prevButton: { backgroundColor: '#334155' },
  prevButtonText: { color: '#cbd5e1', fontWeight: '600' },
  nextButton: { backgroundColor: '#2563eb' },
  nextButtonText: { color: '#ffffff', fontWeight: '600' },
  createButton: { backgroundColor: '#10b981' },
  createButtonText: { color: '#ffffff', fontWeight: 'bold' }
});
