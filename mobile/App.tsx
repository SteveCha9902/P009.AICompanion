import React from 'react';
import { LogBox } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { RootNavigator } from './src/navigation/RootNavigator';

// Selectively suppress non-critical conversation stream toasts in development
if (__DEV__) {
  LogBox.ignoreLogs([
    '[RealtimeChannel]',
    '[VoiceController]',
    '[VisionController]',
    'Unsupported FormDataPart',
    'Max reconnect attempts',
  ]);
}

export default function App() {
  return (
    <SafeAreaProvider>
      <RootNavigator />
    </SafeAreaProvider>
  );
}
