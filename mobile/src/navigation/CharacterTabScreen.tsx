import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { CharacterGalleryScreen } from '../features/character/screens/CharacterGalleryScreen';
import { CharacterCreationWizardScreen } from '../features/character/screens/CharacterCreationWizardScreen';
import { CharacterProfileScreen } from '../features/character/screens/CharacterProfileScreen';
import { useCharacterStore } from '../state/useCharacterStore';

export function CharacterTabScreen({ navigation }: any) {
  const [currentView, setCurrentView] = useState<'gallery' | 'wizard' | 'profile'>('gallery');
  const refreshCharacters = useCharacterStore((state) => state.refreshCharacters);

  return (
    <View style={styles.container}>
      {currentView === 'gallery' && (
        <CharacterGalleryScreen
          navigation={navigation}
          onOpenWizard={() => setCurrentView('wizard')}
          onSelectCharacter={() => {
            // Optional: navigate directly to CompanionScreen
            if (navigation) navigation.navigate('Companion');
          }}
        />
      )}

      {currentView === 'wizard' && (
        <CharacterCreationWizardScreen
          navigation={{
            goBack: () => setCurrentView('gallery')
          }}
          onCreated={() => {
            refreshCharacters();
            setCurrentView('gallery');
          }}
        />
      )}

      {currentView === 'profile' && (
        <CharacterProfileScreen
          navigation={{
            goBack: () => setCurrentView('gallery')
          }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' }
});
