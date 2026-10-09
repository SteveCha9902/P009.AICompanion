import React from 'react';
import { StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ConversationView } from '../features/conversation/presentation/ConversationView';

const TEMP_USER_ID = "test_user_1";
const COMPANION_ID = "default_companion";

/**
 * [LEGACY / DEDICATED CONVERSATION SCREEN]
 * Wraps the unified ConversationView component.
 * Main conversational runtime is hosted in CompanionScreen.
 */
export function ConversationScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <ConversationView userId={TEMP_USER_ID} companionId={COMPANION_ID} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212' },
});
