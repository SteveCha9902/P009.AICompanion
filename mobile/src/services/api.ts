import EventSource from "react-native-sse";
import { API_URL } from "../config/env";
export { API_URL };

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      return data.status === 'ok';
    }
    return false;
  } catch (error) {
    console.error("Backend health check failed:", error);
    return false;
  }
}

export async function createConversation(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/conversations`, {
    method: 'POST',
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to create conversation');
  return response.json();
}

export async function getConversations(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/conversations`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch conversations');
  return response.json();
}

export async function getMessages(userId: string, conversationId: string) {
  const response = await fetch(`${API_URL}/api/v1/conversations/${conversationId}/messages`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch messages');
  return response.json();
}

export async function getPersona(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/personas/me`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch persona');
  return response.json();
}

export async function updatePersona(userId: string, updateData: any) {
  const response = await fetch(`${API_URL}/api/v1/personas/me`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'x-user-id': userId },
    body: JSON.stringify(updateData)
  });
  if (!response.ok) throw new Error('Failed to update persona');
  return response.json();
}

export async function applyPersonaPreset(userId: string, presetName: string) {
  const response = await fetch(`${API_URL}/api/v1/personas/me/preset/${presetName}`, {
    method: 'POST',
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to apply preset');
  return response.json();
}

export async function getMemories(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/memories`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch memories');
  return response.json();
}

export async function deleteMemory(userId: string, memoryId: string) {
  const response = await fetch(`${API_URL}/api/v1/memories/${memoryId}`, {
    method: 'DELETE',
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to delete memory');
  return response.json();
}

export async function getEmotionState(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/emotions/current`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch emotion state');
  return response.json();
}

export async function getEmotionHistory(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/emotions/history`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch emotion history');
  return response.json();
}

export async function getRelationshipState(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/relationships/current`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch relationship state');
  return response.json();
}

export async function getRelationshipHistory(userId: string) {
  const response = await fetch(`${API_URL}/api/v1/relationships/history`, {
    headers: { 'x-user-id': userId }
  });
  if (!response.ok) throw new Error('Failed to fetch relationship history');
  return response.json();
}

export function streamMessage(
  userId: string,
  conversationId: string,
  content: string,
  onMessage: (text: string) => void,
  onDone: () => void,
  onError: (err: any) => void
) {
  const es = new EventSource(`${API_URL}/api/v1/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-user-id': userId
    },
    body: JSON.stringify({ content }),
    lineEndingCharacter: '\n'
  });

  es.addEventListener("message", (event) => {
    if (!event.data) return;
    if (event.data === "[DONE]") {
      es.close();
      onDone();
    } else if (event.data.startsWith("[ERROR]")) {
      es.close();
      onError(new Error(event.data));
    } else {
      onMessage(event.data);
    }
  });

  es.addEventListener("error", (event) => {
    es.close();
    onError(event);
  });

  return es;
}
