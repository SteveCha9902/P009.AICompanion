import * as SecureStore from 'expo-secure-store';

export async function saveSecureItem(key: string, value: string) {
  await SecureStore.setItemAsync(key, value);
}

export async function getSecureItem(key: string): Promise<string | null> {
  return await SecureStore.getItemAsync(key);
}

export async function deleteSecureItem(key: string) {
  await SecureStore.deleteItemAsync(key);
}
