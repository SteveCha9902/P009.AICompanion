import { Platform, NativeModules } from 'react-native';

export type AppEnvironment = 'development' | 'preview' | 'production';

export const CURRENT_ENV: AppEnvironment = 
  (process.env.EXPO_PUBLIC_ENV as AppEnvironment) || 'development';

/**
 * Mobile Environment Configuration
 * Predictable Base URL resolution:
 * 1. Explicit EXPO_PUBLIC_API_URL (e.g. Physical Device LAN IP: http://192.168.55.140:8000 or Production Domain)
 * 2. React Native scriptURL Host (automatically extracts developer PC IP in Expo Go on real devices)
 * 3. Environment / Platform defaults:
 *    - Android: http://192.168.55.140:8000 (LAN)
 *    - iOS Simulator / Default: http://localhost:8000
 */
export function getApiBaseUrl(): string {
  if (process.env.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL.replace(/\/+$/, '');
  }

  if (CURRENT_ENV === 'production') {
    return 'https://api.p009.companion.ai';
  }

  // Auto-detect PC IP from NativeModules SourceCode (available in Expo Go / React Native dev mode)
  const scriptURL: string = NativeModules?.SourceCode?.scriptURL || '';
  if (scriptURL) {
    const address = scriptURL.split('://')[1]?.split('/')[0]?.split(':')[0];
    if (address && address !== 'localhost' && address !== '127.0.0.1') {
      return `http://${address}:8000`;
    }
  }

  if (Platform.OS === 'android') {
    // Default PC LAN IP for physical Android device
    return 'http://192.168.10.82:8000';
  }

  return 'http://localhost:8000';
}

export const API_URL = getApiBaseUrl();


