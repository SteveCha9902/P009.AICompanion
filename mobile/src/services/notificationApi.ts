import { API_URL } from './api';

export async function registerPushToken(userId: string, token: string) {
  const response = await fetch(`${API_URL}/api/v1/notifications/token`, {
    method: 'POST',
    headers: {
      'x-user-id': userId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ token })
  });
  if (!response.ok) throw new Error('Failed to register push token');
  return response.json();
}

export async function getNotificationSettings(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/notifications/settings`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch notification settings');
  return response.json();
}

export async function updateNotificationSettings(userId: string, settings: any) {
  const response = await fetch(`${API_URL}/api/v1/notifications/settings`, {
    method: 'PUT',
    headers: {
      'x-user-id': userId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
  });
  if (!response.ok) throw new Error('Failed to update notification settings');
  return response.json();
}
