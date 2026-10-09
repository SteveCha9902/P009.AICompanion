import { API_URL } from './api';

export async function getPresenceState(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/presence`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch presence state');
  return response.json();
}

export async function sendHeartbeat(userId: string, isForeground: boolean) {
  const response = await fetch(`${API_URL}/api/v1/presence/heartbeat`, {
    method: 'POST',
    headers: {
      'x-user-id': userId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ is_foreground: isForeground })
  });
  if (!response.ok) throw new Error('Failed to send heartbeat');
  return response.json();
}

export async function getProactiveSettings(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/proactive/settings`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch proactive settings');
  return response.json();
}

export async function updateProactiveSettings(userId: string, settings: any) {
  const response = await fetch(`${API_URL}/api/v1/proactive/settings`, {
    method: 'PUT',
    headers: {
      'x-user-id': userId,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
  });
  if (!response.ok) throw new Error('Failed to update proactive settings');
  return response.json();
}

export async function getProactiveHistory(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/proactive/history`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch proactive history');
  return response.json();
}
