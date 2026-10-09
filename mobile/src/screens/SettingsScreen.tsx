import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Platform
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as Speech from 'expo-speech';
import { useCharacterStore } from '../state/useCharacterStore';
import { characterApi, CharacterSummary, CharacterPresentation, CharacterDetail } from '../features/character/services/characterApi';

const USER_ID = 'default_user';

interface VoicePreset {
  id: string;
  name: string;
  desc: string;
  recommendedFor: string;
  pitch: number;
  rate: number;
}

const VOICE_PRESETS: VoicePreset[] = [
  {
    id: 'ko-KR-SunHiNeural',
    name: '선희 (SunHi)',
    desc: '포근하고 다정한 한국어 여성 음성',
    recommendedFor: 'default_companion',
    pitch: 0.0,
    rate: 0.98,
  },
  {
    id: 'ko-KR-JiMinNeural',
    name: '지민 (JiMin)',
    desc: '밝고 애교 넘치는 발랄한 딸 음성',
    recommendedFor: 'c_mani',
    pitch: 1.15,
    rate: 1.05,
  },
  {
    id: 'ko-KR-SeoHyeonNeural',
    name: '서현 (SeoHyeon)',
    desc: '솔직하고 트렌디한 절친 음성',
    recommendedFor: 'c_hana',
    pitch: 1.0,
    rate: 1.0,
  },
  {
    id: 'ko-KR-YuJinNeural',
    name: '유진 (YuJin)',
    desc: '명랑하고 깔끔한 대화형 음성',
    recommendedFor: '',
    pitch: 1.05,
    rate: 1.02,
  },
  {
    id: 'ko-KR-InJoonNeural',
    name: '인준 (InJoon)',
    desc: '부드럽고 따뜻한 남성 음성',
    recommendedFor: '',
    pitch: 0.95,
    rate: 0.98,
  },
  {
    id: 'ko-KR-BongJinNeural',
    name: '봉진 (BongJin)',
    desc: '듬직하고 차분한 남성 음성',
    recommendedFor: '',
    pitch: 0.90,
    rate: 0.95,
  },
  {
    id: 'shimmer',
    name: 'Shimmer (OpenAI)',
    desc: '따뜻하고 선명한 글로벌 HD 음성',
    recommendedFor: '',
    pitch: 1.0,
    rate: 1.0,
  },
  {
    id: 'nova',
    name: 'Nova (OpenAI)',
    desc: '활기차고 에너제틱한 글로벌 HD 음성',
    recommendedFor: '',
    pitch: 1.0,
    rate: 1.0,
  },
];

const PREVIEW_PHRASES: Record<string, string> = {
  default_companion: '여보, 오늘 하루도 수고 많았어요. 당신 곁에 항상 제가 있을게요.',
  c_mani: '아빠! 마니 목소리 어때요? 마니는 아빠랑 이야기하는 게 세상에서 제일 좋아요! 😊',
  c_hana: '안녕! 내 목소리 마음에 들어? 오늘도 재미있는 이야기 많이 나누자! ✨',
};

export function SettingsScreen() {
  const { characterList, activeCharacterId, fetchCharacters, switchCharacter } = useCharacterStore();

  const [selectedCompanionId, setSelectedCompanionId] = useState<string>('default_companion');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isPlayingPreview, setIsPlayingPreview] = useState<boolean>(false);

  // Character presentation & detail state
  const [presentation, setPresentation] = useState<CharacterPresentation | null>(null);
  const [detail, setDetail] = useState<CharacterDetail | null>(null);

  // Editable fields
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>('ko-KR-SunHiNeural');
  const [speakingRate, setSpeakingRate] = useState<number>(1.0);
  const [pitchOffset, setPitchOffset] = useState<number>(0.0);
  const [voiceWarmth, setVoiceWarmth] = useState<number>(85);
  const [voiceEnergy, setVoiceEnergy] = useState<number>(80);

  // Personality DNA
  const [personalityDna, setPersonalityDna] = useState<{
    warmth: number;
    humor: number;
    curiosity: number;
    empathy: number;
    playfulness: number;
    formality: number;
  }>({
    warmth: 85,
    humor: 75,
    curiosity: 80,
    empathy: 85,
    playfulness: 80,
    formality: 20,
  });

  // Communication style
  const [commTone, setCommTone] = useState<string>('friendly');
  const [commVerbosity, setCommVerbosity] = useState<string>('balanced');

  useEffect(() => {
    fetchCharacters(USER_ID);
  }, []);

  useEffect(() => {
    if (activeCharacterId && !selectedCompanionId) {
      setSelectedCompanionId(activeCharacterId);
    }
  }, [activeCharacterId]);

  useEffect(() => {
    if (selectedCompanionId) {
      loadCharacterSettings(selectedCompanionId);
    }
  }, [selectedCompanionId]);

  const loadCharacterSettings = async (companionId: string) => {
    try {
      setIsLoading(true);
      Speech.stop();
      setIsPlayingPreview(false);

      const [presData, detailData] = await Promise.all([
        characterApi.getPresentation(companionId, USER_ID).catch(() => null),
        characterApi.getCharacterDetail(companionId, USER_ID).catch(() => null),
      ]);

      if (presData) {
        setPresentation(presData);
        setSelectedVoiceId(presData.voice.voice_id || 'ko-KR-SunHiNeural');
        setSpeakingRate(presData.voice.speaking_rate || 1.0);
        setPitchOffset(presData.voice.pitch_offset || 0.0);
        setVoiceWarmth(Math.round((presData.voice.warmth || 0.85) * 100));
        setVoiceEnergy(Math.round((presData.voice.energy || 0.80) * 100));
      } else {
        // Fallbacks based on character
        if (companionId === 'c_mani') {
          setSelectedVoiceId('ko-KR-JiMinNeural');
          setSpeakingRate(1.05);
          setPitchOffset(2.0);
        } else if (companionId === 'c_hana') {
          setSelectedVoiceId('ko-KR-SeoHyeonNeural');
          setSpeakingRate(1.0);
          setPitchOffset(0.0);
        } else {
          setSelectedVoiceId('ko-KR-SunHiNeural');
          setSpeakingRate(0.98);
          setPitchOffset(0.0);
        }
      }

      if (detailData) {
        setDetail(detailData);
        if (detailData.dna) {
          setPersonalityDna({
            warmth: Math.round(detailData.dna.warmth * 100),
            humor: Math.round(detailData.dna.humor * 100),
            curiosity: Math.round(detailData.dna.curiosity * 100),
            empathy: Math.round(detailData.dna.empathy * 100),
            playfulness: Math.round(detailData.dna.playfulness * 100),
            formality: Math.round(detailData.dna.formality * 100),
          });
        }
      }
    } catch (e) {
      console.error('[SettingsScreen] Failed to load character settings:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectCharacterTab = (companionId: string) => {
    setSelectedCompanionId(companionId);
  };

  const handleSetActiveCharacter = async () => {
    if (selectedCompanionId === activeCharacterId) return;
    try {
      setIsSaving(true);
      const success = await switchCharacter(selectedCompanionId, USER_ID);
      if (success) {
        Alert.alert('캐릭터 전환 완료', `${getCharacterDisplayName(selectedCompanionId)} 캐릭터로 전환되었습니다.`);
      }
    } catch (e: any) {
      Alert.alert('전환 실패', e.message || '캐릭터 전환 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleVoicePreview = () => {
    Speech.stop();

    const phrase =
      PREVIEW_PHRASES[selectedCompanionId] ||
      `${getCharacterDisplayName(selectedCompanionId)}입니다. 목소리 설정을 변경해 보세요!`;

    setIsPlayingPreview(true);

    // Calculate preview pitch and rate
    let speechPitch = 1.0;
    if (selectedCompanionId === 'c_mani' || selectedVoiceId.includes('JiMin')) {
      speechPitch = 1.15;
    } else if (pitchOffset > 0) {
      speechPitch = Math.min(1.3, 1.0 + pitchOffset * 0.05);
    } else if (pitchOffset < 0) {
      speechPitch = Math.max(0.7, 1.0 + pitchOffset * 0.05);
    }

    const speechRate = Math.max(0.7, Math.min(1.3, speakingRate));

    Speech.speak(phrase, {
      language: 'ko-KR',
      pitch: speechPitch,
      rate: speechRate,
      onDone: () => setIsPlayingPreview(false),
      onError: () => setIsPlayingPreview(false),
    });
  };

  const handleSaveAll = async () => {
    try {
      setIsSaving(true);
      Speech.stop();
      setIsPlayingPreview(false);

      // 1. Update Presentation (Voice + Speech config)
      await characterApi.updatePresentation(
        selectedCompanionId,
        {
          voice: {
            voice_id: selectedVoiceId,
            speaking_rate: speakingRate,
            pitch_offset: pitchOffset,
            warmth: voiceWarmth / 100,
            energy: voiceEnergy / 100,
            empathy: personalityDna.empathy / 100,
          },
        },
        USER_ID
      );

      // 2. Update Character DNA
      await characterApi.updateCharacter(
        selectedCompanionId,
        {
          dna: {
            warmth: personalityDna.warmth / 100,
            humor: personalityDna.humor / 100,
            curiosity: personalityDna.curiosity / 100,
            empathy: personalityDna.empathy / 100,
            playfulness: personalityDna.playfulness / 100,
            formality: personalityDna.formality / 100,
            optimism: 0.95,
          },
        },
        USER_ID
      );

      Alert.alert('저장 완료', `${getCharacterDisplayName(selectedCompanionId)}의 목소리 및 성격 설정이 저장되었습니다.`);
      await loadCharacterSettings(selectedCompanionId);
    } catch (e: any) {
      console.error('[SettingsScreen] Save error:', e);
      Alert.alert('저장 실패', e.message || '설정을 저장하지 못했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetToDefaults = () => {
    if (selectedCompanionId === 'c_mani') {
      setSelectedVoiceId('ko-KR-JiMinNeural');
      setSpeakingRate(1.05);
      setPitchOffset(2.0);
      setVoiceWarmth(95);
      setVoiceEnergy(90);
      setPersonalityDna({
        warmth: 98,
        humor: 85,
        curiosity: 95,
        empathy: 92,
        playfulness: 98,
        formality: 10,
      });
      setCommTone('playful');
    } else if (selectedCompanionId === 'c_hana') {
      setSelectedVoiceId('ko-KR-SeoHyeonNeural');
      setSpeakingRate(1.0);
      setPitchOffset(0.0);
      setVoiceWarmth(85);
      setVoiceEnergy(85);
      setPersonalityDna({
        warmth: 85,
        humor: 80,
        curiosity: 90,
        empathy: 85,
        playfulness: 85,
        formality: 20,
      });
      setCommTone('friendly');
    } else {
      setSelectedVoiceId('ko-KR-SunHiNeural');
      setSpeakingRate(0.98);
      setPitchOffset(0.0);
      setVoiceWarmth(95);
      setVoiceEnergy(70);
      setPersonalityDna({
        warmth: 98,
        humor: 75,
        curiosity: 85,
        empathy: 95,
        playfulness: 65,
        formality: 30,
      });
      setCommTone('empathetic');
    }
  };

  const adjustDna = (trait: keyof typeof personalityDna, amount: number) => {
    setPersonalityDna((prev) => ({
      ...prev,
      [trait]: Math.max(0, Math.min(100, prev[trait] + amount)),
    }));
  };

  const getCharacterDisplayName = (companionId: string): string => {
    if (companionId === 'c_mani' || companionId.includes('mani')) return 'Mani (마니)';
    if (companionId === 'c_hana' || companionId.includes('hana')) return 'Hana (하나)';
    return 'Genie (지니)';
  };

  const getCharacterRoleBadge = (companionId: string): string => {
    if (companionId === 'c_mani' || companionId.includes('mani')) return '🎀 사랑스러운 딸 (16세)';
    if (companionId === 'c_hana' || companionId.includes('hana')) return '🎨 솔직한 절친 (24세)';
    return '🌸 다정한 아내 (Wife)';
  };

  // Standard characters for selector
  const characterTabs = [
    { id: 'default_companion', name: 'Genie (지니)', role: '아내', emoji: '🌸' },
    { id: 'c_mani', name: 'Mani (마니)', role: '딸', emoji: '🎀' },
    { id: 'c_hana', name: 'Hana (하나)', role: '친구', emoji: '🎨' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      {/* Top Fixed Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>캐릭터 & 목소리 개별 설정</Text>
        <Text style={styles.headerSubtitle}>지니, 마니, 하나 각 캐릭터의 목소리와 성격을 개별 셋팅합니다.</Text>
      </View>

      {/* Character Selector Segment Tabs */}
      <View style={styles.characterSegmentContainer}>
        {characterTabs.map((char) => {
          const isSelected = selectedCompanionId === char.id;
          const isActive = activeCharacterId === char.id || (char.id === 'default_companion' && !activeCharacterId);
          return (
            <TouchableOpacity
              key={char.id}
              style={[
                styles.characterTab,
                isSelected && styles.characterTabSelected,
              ]}
              onPress={() => handleSelectCharacterTab(char.id)}
            >
              <Text style={styles.characterTabEmoji}>{char.emoji}</Text>
              <Text style={[styles.characterTabName, isSelected && styles.characterTabNameSelected]}>
                {char.name}
              </Text>
              <View style={styles.characterTabMeta}>
                <Text style={styles.characterTabRole}>{char.role}</Text>
                {isActive && (
                  <View style={styles.activePill}>
                    <Text style={styles.activePillText}>사용중</Text>
                  </View>
                )}
              </View>
            </TouchableOpacity>
          );
        })}
      </View>

      {isLoading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>캐릭터 설정을 불러오는 중...</Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Character Identity Banner */}
          <View style={styles.charBanner}>
            <View style={styles.charBannerHeader}>
              <View>
                <Text style={styles.charBannerName}>{getCharacterDisplayName(selectedCompanionId)}</Text>
                <Text style={styles.charBannerRole}>{getCharacterRoleBadge(selectedCompanionId)}</Text>
              </View>
              {activeCharacterId !== selectedCompanionId && (
                <TouchableOpacity
                  style={styles.activateBtn}
                  onPress={handleSetActiveCharacter}
                  disabled={isSaving}
                >
                  <Text style={styles.activateBtnText}>⚡ 이 캐릭터 사용하기</Text>
                </TouchableOpacity>
              )}
            </View>
            <Text style={styles.charBannerDesc}>
              {selectedCompanionId === 'c_mani'
                ? '아빠(엄마)를 세상에서 제일 사랑하는 애교 많고 발랄한 딸 마니의 개별 설정입니다.'
                : selectedCompanionId === 'c_hana'
                ? '트렌디하고 솔직하며 예술적 영감을 주는 둘도 없는 절친 하나의 개별 설정입니다.'
                : '언제나 곁에서 깊은 공감과 온기를 전해주는 사랑스러운 아내 지니의 개별 설정입니다.'}
            </Text>
          </View>

          {/* 1. Voice Settings Section */}
          <View style={styles.section}>
            <View style={styles.sectionHeaderRow}>
              <Text style={styles.sectionTitle}>🎙️ 개별 음성 & 보이스 모델</Text>
              <TouchableOpacity
                style={[styles.previewBtn, isPlayingPreview && styles.previewBtnActive]}
                onPress={handleVoicePreview}
              >
                <Text style={styles.previewBtnText}>
                  {isPlayingPreview ? '🔊 재생 중...' : '▶ 목소리 미리듣기'}
                </Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.subLabel}>한국어 뉴럴 & HD 보이스 모델 선택</Text>
            <View style={styles.voiceList}>
              {VOICE_PRESETS.map((v) => {
                const isChecked = selectedVoiceId === v.id;
                const isRecommended = v.recommendedFor === selectedCompanionId;
                return (
                  <TouchableOpacity
                    key={v.id}
                    style={[styles.voiceItem, isChecked && styles.voiceItemActive]}
                    onPress={() => {
                      setSelectedVoiceId(v.id);
                      if (v.rate) setSpeakingRate(v.rate);
                      if (v.pitch !== undefined) setPitchOffset(v.pitch);
                    }}
                  >
                    <View style={styles.voiceItemLeft}>
                      <View style={[styles.radioCircle, isChecked && styles.radioCircleActive]} />
                      <View style={styles.voiceItemTextCol}>
                        <View style={styles.voiceTitleRow}>
                          <Text style={[styles.voiceItemName, isChecked && styles.voiceItemNameActive]}>
                            {v.name}
                          </Text>
                          {isRecommended && (
                            <View style={styles.recBadge}>
                              <Text style={styles.recBadgeText}>추천</Text>
                            </View>
                          )}
                        </View>
                        <Text style={styles.voiceItemDesc}>{v.desc}</Text>
                      </View>
                    </View>
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* Voice Fine Tuning Controls */}
            <Text style={[styles.subLabel, { marginTop: 18 }]}>목소리 정밀 튜닝 (말하기 속도 & 톤)</Text>

            {/* Speaking Rate */}
            <View style={styles.controlRow}>
              <View>
                <Text style={styles.controlLabel}>말하기 속도 (Speech Rate)</Text>
                <Text style={styles.controlSub}>{speakingRate.toFixed(2)}x</Text>
              </View>
              <View style={styles.stepperContainer}>
                <TouchableOpacity
                  style={styles.stepperBtn}
                  onPress={() => setSpeakingRate((prev) => Math.max(0.7, +(prev - 0.05).toFixed(2)))}
                >
                  <Text style={styles.stepperBtnText}>-</Text>
                </TouchableOpacity>
                <View style={styles.rateQuickChips}>
                  {[0.9, 1.0, 1.1].map((r) => (
                    <TouchableOpacity
                      key={r}
                      style={[styles.quickChip, Math.abs(speakingRate - r) < 0.02 && styles.quickChipActive]}
                      onPress={() => setSpeakingRate(r)}
                    >
                      <Text style={styles.quickChipText}>{r}x</Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <TouchableOpacity
                  style={styles.stepperBtn}
                  onPress={() => setSpeakingRate((prev) => Math.min(1.3, +(prev + 0.05).toFixed(2)))}
                >
                  <Text style={styles.stepperBtnText}>+</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Pitch Offset */}
            <View style={styles.controlRow}>
              <View>
                <Text style={styles.controlLabel}>음높이 / 피치 (Pitch Offset)</Text>
                <Text style={styles.controlSub}>{pitchOffset >= 0 ? `+${pitchOffset.toFixed(1)}Hz` : `${pitchOffset.toFixed(1)}Hz`}</Text>
              </View>
              <View style={styles.stepperContainer}>
                <TouchableOpacity
                  style={styles.stepperBtn}
                  onPress={() => setPitchOffset((prev) => Math.max(-10.0, +(prev - 0.5).toFixed(1)))}
                >
                  <Text style={styles.stepperBtnText}>-</Text>
                </TouchableOpacity>
                <View style={styles.rateQuickChips}>
                  {[-2.0, 0.0, 2.0].map((p) => (
                    <TouchableOpacity
                      key={p}
                      style={[styles.quickChip, Math.abs(pitchOffset - p) < 0.1 && styles.quickChipActive]}
                      onPress={() => setPitchOffset(p)}
                    >
                      <Text style={styles.quickChipText}>{p >= 0 ? `+${p}` : p}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <TouchableOpacity
                  style={styles.stepperBtn}
                  onPress={() => setPitchOffset((prev) => Math.min(10.0, +(prev + 0.5).toFixed(1)))}
                >
                  <Text style={styles.stepperBtnText}>+</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Voice Warmth & Energy */}
            <View style={styles.controlRow}>
              <View>
                <Text style={styles.controlLabel}>목소리 다정함 (Warmth)</Text>
                <Text style={styles.controlSub}>{voiceWarmth}%</Text>
              </View>
              <View style={styles.stepperContainer}>
                <TouchableOpacity style={styles.stepperBtn} onPress={() => setVoiceWarmth((p) => Math.max(0, p - 5))}>
                  <Text style={styles.stepperBtnText}>-</Text>
                </TouchableOpacity>
                <Text style={styles.stepperValue}>{voiceWarmth}%</Text>
                <TouchableOpacity style={styles.stepperBtn} onPress={() => setVoiceWarmth((p) => Math.min(100, p + 5))}>
                  <Text style={styles.stepperBtnText}>+</Text>
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.controlRow}>
              <View>
                <Text style={styles.controlLabel}>생동감 & 에너지 (Energy)</Text>
                <Text style={styles.controlSub}>{voiceEnergy}%</Text>
              </View>
              <View style={styles.stepperContainer}>
                <TouchableOpacity style={styles.stepperBtn} onPress={() => setVoiceEnergy((p) => Math.max(0, p - 5))}>
                  <Text style={styles.stepperBtnText}>-</Text>
                </TouchableOpacity>
                <Text style={styles.stepperValue}>{voiceEnergy}%</Text>
                <TouchableOpacity style={styles.stepperBtn} onPress={() => setVoiceEnergy((p) => Math.min(100, p + 5))}>
                  <Text style={styles.stepperBtnText}>+</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>

          {/* 2. Personality & Cognitive DNA Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🧠 성격 및 인지 DNA (Personality Traits)</Text>
            <Text style={styles.subLabel}>이 캐릭터만의 고유한 성격 지수를 조절합니다 (0~100)</Text>

            {/* Traits */}
            {[
              { key: 'warmth' as const, label: '다정함 (Warmth)', icon: '❤️' },
              { key: 'empathy' as const, label: '공감능력 (Empathy)', icon: '🤝' },
              { key: 'playfulness' as const, label: '발랄함 / 애교 (Playfulness)', icon: '✨' },
              { key: 'curiosity' as const, label: '호기심 (Curiosity)', icon: '🔍' },
              { key: 'humor' as const, label: '유머 감각 (Humor)', icon: '😄' },
              { key: 'formality' as const, label: '격식 / 예의 (Formality)', icon: '👔' },
            ].map((t) => (
              <View key={t.key} style={styles.traitRow}>
                <View style={styles.traitLabelCol}>
                  <Text style={styles.traitIcon}>{t.icon}</Text>
                  <Text style={styles.traitLabel}>{t.label}</Text>
                </View>
                <View style={styles.stepperContainer}>
                  <TouchableOpacity style={styles.stepperBtn} onPress={() => adjustDna(t.key, -5)}>
                    <Text style={styles.stepperBtnText}>-</Text>
                  </TouchableOpacity>
                  <Text style={styles.stepperValue}>{personalityDna[t.key]}</Text>
                  <TouchableOpacity style={styles.stepperBtn} onPress={() => adjustDna(t.key, 5)}>
                    <Text style={styles.stepperBtnText}>+</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>

          {/* 3. Communication Style Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>💬 대화 스타일 & 어조</Text>

            <Text style={styles.subLabel}>선호 대화 톤</Text>
            <View style={styles.chipRow}>
              {[
                { id: 'friendly', label: '다정한 (Friendly)' },
                { id: 'empathetic', label: '공감하는 (Empathetic)' },
                { id: 'playful', label: '장난스러운 (Playful)' },
                { id: 'polite', label: '정중한 (Polite)' },
              ].map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.styleChip, commTone === item.id && styles.styleChipActive]}
                  onPress={() => setCommTone(item.id)}
                >
                  <Text style={[styles.styleChipText, commTone === item.id && styles.styleChipTextActive]}>
                    {item.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={[styles.subLabel, { marginTop: 14 }]}>답변 길이 / 호흡</Text>
            <View style={styles.chipRow}>
              {[
                { id: 'concise', label: '간결하게 (1~2문장)' },
                { id: 'balanced', label: '균형있게 (2~3문장)' },
                { id: 'detailed', label: '자세하게 (풍부한 대화)' },
              ].map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.styleChip, commVerbosity === item.id && styles.styleChipActive]}
                  onPress={() => setCommVerbosity(item.id)}
                >
                  <Text style={[styles.styleChipText, commVerbosity === item.id && styles.styleChipTextActive]}>
                    {item.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Action Buttons */}
          <View style={styles.actionContainer}>
            <TouchableOpacity
              style={styles.saveButton}
              onPress={handleSaveAll}
              disabled={isSaving}
            >
              {isSaving ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text style={styles.saveButtonText}>💾 {getCharacterDisplayName(selectedCompanionId)} 설정 저장하기</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.resetButton}
              onPress={handleResetToDefaults}
              disabled={isSaving}
            >
              <Text style={styles.resetButtonText}>🔄 {getCharacterDisplayName(selectedCompanionId)} 기본값으로 복원</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F12',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 10,
    backgroundColor: '#16161D',
    borderBottomWidth: 1,
    borderBottomColor: '#252530',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
    letterSpacing: -0.3,
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#8E8E9F',
    marginTop: 3,
  },
  characterSegmentContainer: {
    flexDirection: 'row',
    backgroundColor: '#16161D',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#252530',
    gap: 8,
  },
  characterTab: {
    flex: 1,
    backgroundColor: '#1F1F2B',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 8,
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: 'transparent',
  },
  characterTabSelected: {
    backgroundColor: '#1A2942',
    borderColor: '#007AFF',
  },
  characterTabEmoji: {
    fontSize: 22,
    marginBottom: 4,
  },
  characterTabName: {
    fontSize: 13,
    fontWeight: '600',
    color: '#A0A0B5',
  },
  characterTabNameSelected: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  characterTabMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 4,
  },
  characterTabRole: {
    fontSize: 11,
    color: '#707085',
  },
  activePill: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 5,
    paddingVertical: 1.5,
    borderRadius: 6,
  },
  activePillText: {
    color: '#FFFFFF',
    fontSize: 9,
    fontWeight: '700',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    color: '#8E8E9F',
    fontSize: 14,
    marginTop: 12,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  charBanner: {
    backgroundColor: '#1A1A26',
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#2D2D3F',
  },
  charBannerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  charBannerName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  charBannerRole: {
    fontSize: 13,
    color: '#007AFF',
    fontWeight: '600',
    marginTop: 2,
  },
  charBannerDesc: {
    fontSize: 12.5,
    color: '#A0A0B5',
    lineHeight: 18,
  },
  activateBtn: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  activateBtnText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
  },
  section: {
    backgroundColor: '#16161F',
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#232330',
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  subLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#8E8E9F',
    marginBottom: 8,
  },
  previewBtn: {
    backgroundColor: '#2A3B5C',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  previewBtnActive: {
    backgroundColor: '#007AFF',
  },
  previewBtnText: {
    color: '#64D2FF',
    fontSize: 12,
    fontWeight: '600',
  },
  voiceList: {
    gap: 8,
  },
  voiceItem: {
    backgroundColor: '#1E1E2C',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#2B2B3D',
  },
  voiceItemActive: {
    backgroundColor: '#192842',
    borderColor: '#007AFF',
  },
  voiceItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  radioCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#555566',
  },
  radioCircleActive: {
    borderColor: '#007AFF',
    backgroundColor: '#007AFF',
  },
  voiceItemTextCol: {
    flex: 1,
  },
  voiceTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  voiceItemName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#E0E0EC',
  },
  voiceItemNameActive: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  recBadge: {
    backgroundColor: '#007AFF33',
    paddingHorizontal: 6,
    paddingVertical: 1,
    borderRadius: 4,
    borderWidth: 0.5,
    borderColor: '#007AFF88',
  },
  recBadgeText: {
    color: '#64D2FF',
    fontSize: 10,
    fontWeight: '700',
  },
  voiceItemDesc: {
    fontSize: 11.5,
    color: '#8E8E9F',
    marginTop: 2,
  },
  controlRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 0.5,
    borderBottomColor: '#252535',
  },
  controlLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#E0E0EC',
  },
  controlSub: {
    fontSize: 11,
    color: '#007AFF',
    marginTop: 2,
  },
  stepperContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stepperBtn: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#272738',
    justifyContent: 'center',
    alignItems: 'center',
  },
  stepperBtnText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  stepperValue: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
    minWidth: 36,
    textAlign: 'center',
  },
  rateQuickChips: {
    flexDirection: 'row',
    gap: 4,
  },
  quickChip: {
    backgroundColor: '#232333',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 6,
  },
  quickChipActive: {
    backgroundColor: '#007AFF',
  },
  quickChipText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '600',
  },
  traitRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 0.5,
    borderBottomColor: '#252535',
  },
  traitLabelCol: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  traitIcon: {
    fontSize: 16,
  },
  traitLabel: {
    fontSize: 13,
    color: '#E0E0EC',
    fontWeight: '500',
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  styleChip: {
    backgroundColor: '#1E1E2C',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#2B2B3D',
  },
  styleChipActive: {
    backgroundColor: '#192842',
    borderColor: '#007AFF',
  },
  styleChipText: {
    color: '#A0A0B5',
    fontSize: 12,
    fontWeight: '600',
  },
  styleChipTextActive: {
    color: '#FFFFFF',
  },
  actionContainer: {
    marginTop: 8,
    gap: 10,
  },
  saveButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  resetButton: {
    backgroundColor: '#20202E',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#2D2D40',
  },
  resetButtonText: {
    color: '#8E8E9F',
    fontSize: 13,
    fontWeight: '600',
  },
});
