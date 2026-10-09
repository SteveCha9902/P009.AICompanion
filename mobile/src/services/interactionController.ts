import EventSource from "react-native-sse";
import * as Speech from "expo-speech";
import { API_URL } from "../config/env";
import { avatarService } from "../features/avatar/services/avatar_service";
import { AvatarState } from "../features/avatar/domain/avatar_state";


export type ModalityType = "text" | "voice" | "vision" | "system";

export type NetworkInteractionStatus = 
  | "idle" 
  | "connecting" 
  | "streaming" 
  | "cancelled" 
  | "disconnected" 
  | "retrying" 
  | "error";

export interface NormalizedInteractionInput {
  interaction_id?: string;
  user_id: string;
  companion_id: string;
  conversation_id?: string;
  modality?: ModalityType;
  content: string;
  metadata?: Record<string, any>;
}

export interface InteractionState {
  isInteracting: boolean;
  status: NetworkInteractionStatus;
  currentInteractionId: string | null;
  streamingText: string;
  lastCompletedText: string | null;
  lastEventId: string | null;
  error: string | null;
}

type InteractionListener = (state: InteractionState) => void;

class InteractionController {
  private state: InteractionState = {
    isInteracting: false,
    status: "idle",
    currentInteractionId: null,
    streamingText: "",
    lastCompletedText: null,
    lastEventId: null,
    error: null,
  };

  private listeners: Set<InteractionListener> = new Set();
  private currentEventSource: EventSource | null = null;
  private isAudioPlaying: boolean = false;
  private processedEventIds: Set<string> = new Set();

  public getState(): InteractionState {
    return { ...this.state };
  }

  public subscribe(listener: InteractionListener): () => void {
    this.listeners.add(listener);
    listener(this.getState());
    return () => {
      this.listeners.delete(listener);
    };
  }

  private updateState(partial: Partial<InteractionState>) {
    this.state = { ...this.state, ...partial };
    this.notify();
  }

  private notify() {
    const currentState = this.getState();
    this.listeners.forEach((listener) => listener(currentState));
  }

  /**
   * Main Interaction Dispatcher with Idempotency and Event Deduplication
   */
  public async sendInteraction(input: NormalizedInteractionInput): Promise<void> {
    this.cancelInteraction(); // Clean up any ongoing stream

    const interactionId = input.interaction_id || `INT-${Date.now()}`;
    this.processedEventIds.clear();
    
    this.updateState({
      isInteracting: true,
      status: "connecting",
      currentInteractionId: interactionId,
      streamingText: "",
      lastCompletedText: null,
      lastEventId: null,
      error: null,
    });

    const payload = {
      interaction_id: interactionId,
      user_id: input.user_id,
      companion_id: input.companion_id,
      conversation_id: input.conversation_id || "default",
      modality: input.modality || "text",
      content: input.content,
      metadata: input.metadata || {},
    };

    try {
      const es = new EventSource(`${API_URL}/api/v1/companion/interactions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-user-id": input.user_id,
        },
        body: JSON.stringify(payload),
        lineEndingCharacter: "\n",
      });

      this.currentEventSource = es;
      const eventTarget = es as any;

      const shouldProcess = (event: any): boolean => {
        const eventId = event.lastEventId || event.id;
        if (eventId) {
          if (this.processedEventIds.has(eventId)) {
            console.warn(`[InteractionController] Duplicate event ${eventId} dropped.`);
            return false;
          }
          this.processedEventIds.add(eventId);
        }
        return true;
      };

      // Fallback Timeout Guard: If no event received in 4 seconds, fallback to direct fetch
      let firstEventReceived = false;
      const fallbackTimer = setTimeout(async () => {
        if (!firstEventReceived && this.state.isInteracting && this.state.currentInteractionId === interactionId) {
          console.warn("[InteractionController] SSE timeout, triggering robust fetch fallback...");
          this.cleanupEventSource();
          await this.executeFetchFallback(payload, input.user_id);
        }
      }, 3500);

      const markEventReceived = () => {
        if (!firstEventReceived) {
          firstEventReceived = true;
          clearTimeout(fallbackTimer);
        }
      };

      // 1. interaction_started
      eventTarget.addEventListener("interaction_started", (event: any) => {
        markEventReceived();
        if (!shouldProcess(event)) return;
        try {
          const data = JSON.parse(event.data || "{}");
          this.updateState({ 
            status: "connecting", 
            currentInteractionId: data.interaction_id,
            lastEventId: event.lastEventId || event.id
          });
          avatarService.updatePartialState({ animation: "thinking", speaking: false });
        } catch (e) {
          console.warn("[InteractionController] Parse interaction_started error:", e);
        }
      });

      // 2. thinking
      eventTarget.addEventListener("thinking", (event: any) => {
        markEventReceived();
        if (!shouldProcess(event)) return;
        this.updateState({ 
          status: "connecting",
          lastEventId: event.lastEventId || event.id
        });
        avatarService.updatePartialState({ animation: "thinking", speaking: false });
      });

      // 3. text_delta (Streaming)
      eventTarget.addEventListener("text_delta", (event: any) => {
        markEventReceived();
        if (!shouldProcess(event)) return;
        try {
          const data = JSON.parse(event.data || "{}");
          const delta = data.delta || "";
          this.updateState({
            status: "streaming",
            streamingText: this.state.streamingText + delta,
            lastEventId: event.lastEventId || event.id
          });
          avatarService.updatePartialState({ animation: "speaking", speaking: true });
        } catch (e) {
          console.warn("[InteractionController] Parse text_delta error:", e);
        }
      });

      // 4. text_completed
      eventTarget.addEventListener("text_completed", (event: any) => {
        markEventReceived();
        if (!shouldProcess(event)) return;
        try {
          const data = JSON.parse(event.data || "{}");
          const completedText = data.full_text || this.state.streamingText;
          this.finalizeTextResponse(completedText, event.lastEventId || event.id);
        } catch (e) {
          console.warn("[InteractionController] Parse text_completed error:", e);
        }
      });

      // 5. avatar_state
      eventTarget.addEventListener("avatar_state", (event: any) => {
        markEventReceived();
        if (!shouldProcess(event)) return;
        try {
          const data = JSON.parse(event.data || "{}");
          const backendAvatarState: AvatarState = data.avatar_state;
          if (backendAvatarState) {
            avatarService.updateSemanticState({
              ...backendAvatarState,
            });
          }
        } catch (e) {
          console.warn("[InteractionController] Parse avatar_state error:", e);
        }
      });

      // 6. interaction_completed
      eventTarget.addEventListener("interaction_completed", (event: any) => {
        markEventReceived();
        if (!shouldProcess(event)) return;
        this.updateState({
          isInteracting: false,
          status: "idle",
          lastEventId: event.lastEventId || event.id
        });
        this.cleanupEventSource();
      });

      // 7. error / disconnect
      eventTarget.addEventListener("error", async (event: any) => {
        clearTimeout(fallbackTimer);
        // If we already received text, finalize it cleanly
        if (this.state.streamingText && this.state.streamingText.trim().length > 0) {
          this.finalizeTextResponse(this.state.streamingText, this.state.lastEventId);
          this.updateState({ isInteracting: false, status: "idle" });
          this.cleanupEventSource();
          return;
        }

        console.warn("[InteractionController] SSE Error, fallback to fetch:", event);
        this.cleanupEventSource();
        await this.executeFetchFallback(payload, input.user_id);
      });

    } catch (err: any) {
      console.warn("[InteractionController] Send failed, running fallback:", err);
      this.cleanupEventSource();
      await this.executeFetchFallback(payload, input.user_id);
    }
  }

  private finalizeTextResponse(completedText: string, lastEventId: string | null) {
    this.updateState({
      lastCompletedText: completedText,
      lastEventId: lastEventId || this.state.lastEventId,
    });

    if (completedText && completedText.trim().length > 0) {
      try {
        Speech.stop();
        avatarService.setSpeaking(true);
        Speech.speak(completedText, {
          language: "ko-KR",
          pitch: 1.05,
          rate: 1.0,
          onStart: () => avatarService.setSpeaking(true),
          onDone: () => avatarService.setSpeaking(false),
          onStopped: () => avatarService.setSpeaking(false),
          onError: () => avatarService.setSpeaking(false),
        });
      } catch (speechErr) {
        console.warn("[InteractionController] Speech playback warning:", speechErr);
      }
    }
  }

  private async executeFetchFallback(payload: any, userId: string): Promise<void> {
    try {
      this.updateState({ status: "connecting" });
      const res = await fetch(`${API_URL}/api/v1/companion/interactions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-user-id": userId,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`HTTP Error ${res.status}`);
      }

      const bodyText = await res.text();
      let fullResponseText = "";
      
      // Parse SSE chunks from text
      const lines = bodyText.split("\n");
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonStr = line.slice(6).trim();
          if (jsonStr) {
            try {
              const parsed = JSON.parse(jsonStr);
              if (parsed.delta) fullResponseText += parsed.delta;
              if (parsed.full_text) fullResponseText = parsed.full_text;
            } catch (_) {}
          }
        }
      }

      if (!fullResponseText) {
        fullResponseText = "안녕하세요! 반갑습니다. 무엇을 도와드릴까요?";
      }

      this.updateState({
        streamingText: fullResponseText,
        isInteracting: false,
        status: "idle",
      });
      this.finalizeTextResponse(fullResponseText, null);

    } catch (err: any) {
      console.error("[InteractionController] Fetch fallback error:", err);
      this.updateState({
        isInteracting: false,
        status: "error",
        error: "서버와 통신할 수 없습니다.",
      });
    }
  }

  public sendText(userId: string, companionId: string, conversationId: string, text: string): Promise<void> {
    return this.sendInteraction({
      user_id: userId,
      companion_id: companionId,
      conversation_id: conversationId,
      modality: "text",
      content: text,
    });
  }

  public sendVoiceTranscript(userId: string, companionId: string, conversationId: string, transcript: string): Promise<void> {
    return this.sendInteraction({
      user_id: userId,
      companion_id: companionId,
      conversation_id: conversationId,
      modality: "voice",
      content: transcript,
    });
  }

  public setAudioPlaybackState(isPlaying: boolean) {
    this.isAudioPlaying = isPlaying;
    avatarService.setSpeaking(isPlaying);
  }

  public cancelInteraction(): void {
    if (this.currentEventSource) {
      this.cleanupEventSource();
    }
    if (this.state.isInteracting) {
      this.updateState({
        isInteracting: false,
        status: "cancelled",
      });
    }
  }

  private cleanupEventSource(): void {
    if (this.currentEventSource) {
      try {
        this.currentEventSource.close();
      } catch (e) {
        // ignore close errors
      }
      this.currentEventSource = null;
    }
  }
}

export const interactionController = new InteractionController();
