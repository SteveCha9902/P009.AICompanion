/**
 * Persistent Real-Time Conversation Channel (STEP 13)
 * Bi-directional WebSocket Client for P009 (S25 Ultra) <-> Backend / P015.
 * Features:
 * - Persistent zero-handshake streaming for voice turns and real-time chunked TTS
 * - Resilient auto-reconnect with exponential backoff & heartbeat ping/pong
 * - Interruption (Barge-in) instant cancellation
 * - Transparent fallback to HTTP Multipart POST when WebSocket is unavailable
 */

import { API_URL } from "../config/env";
import { AudioQueueItem, audioQueuePlayer } from "./audioQueuePlayer";

export type RealtimeChannelState = "disconnected" | "connecting" | "connected" | "reconnecting" | "error";

export interface RealtimeEventHandlers {
  onStateChange?: (state: RealtimeChannelState) => void;
  onTranscript?: (transcript: string, isFinal: boolean) => void;
  onResponseChunk?: (delta: string, sequenceIndex: number, avatarState?: any) => void;
  onAudioChunk?: (item: AudioQueueItem) => void;
  onResponseEnd?: (fullText: string, durationMs: number) => void;
  onInterrupted?: () => void;
  onError?: (errMessage: string) => void;
}

export class RealtimeChannel {
  private ws: WebSocket | null = null;
  private state: RealtimeChannelState = "disconnected";
  private sessionId: string = `session-${Date.now()}`;
  private userId: string = "default_user";
  private companionId: string = "default_companion";
  private conversationId: string = "default";
  private connectStartTime: number = 0;

  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectTimer: any = null;
  private pingInterval: any = null;
  private handlers: RealtimeEventHandlers = {};

  constructor(handlers: RealtimeEventHandlers = {}) {
    this.handlers = handlers;
  }

  public setHandlers(handlers: RealtimeEventHandlers) {
    this.handlers = { ...this.handlers, ...handlers };
  }

  public getState(): RealtimeChannelState {
    return this.state;
  }

  public isAvailable(): boolean {
    return this.state === "connected" && this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public getSessionId(): string {
    return this.sessionId;
  }

  /**
   * Connects to the Persistent Real-Time WebSocket endpoint
   */
  public connect(userId: string = "default_user", companionId: string = "default_companion", conversationId: string = "default"): void {
    this.userId = userId;
    this.companionId = companionId;
    this.conversationId = conversationId;

    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      console.log(`[RealtimeChannel][${Date.now()}] ℹ️ connect() skipped: socket already ${this.ws.readyState === WebSocket.OPEN ? "OPEN" : "CONNECTING"}`);
      return;
    }

    this.clearTimers();
    this.connectStartTime = Date.now();
    this.setState(this.reconnectAttempts > 0 ? "reconnecting" : "connecting");

    // Convert HTTP(S) URL to WS(S) URL
    const wsUrl = API_URL.replace(/^http:\/\//, "ws://").replace(/^https:\/\//, "wss://") + "/api/v1/voice/live-ws";
    console.log(`[RealtimeChannel][${Date.now()}] 🔌 connect() started: ${wsUrl} (Attempt #${this.reconnectAttempts + 1})...`);

    try {
      const socket = new WebSocket(wsUrl);
      this.ws = socket;

      socket.onopen = () => {
        const elapsed = Date.now() - this.connectStartTime;
        console.log(`[RealtimeChannel][${Date.now()}] 🟢 ws.onopen fired (elapsed: ${elapsed}ms)`);
        this.reconnectAttempts = 0;
        this.setState("connected");

        // Send session.start handshake
        console.log(`[RealtimeChannel][${Date.now()}] 📤 session.start sent (sessionId: ${this.sessionId})`);
        this.sendRaw({
          event: "session.start",
          session_id: this.sessionId,
          user_id: this.userId,
          companion_id: this.companionId,
          conversation_id: this.conversationId,
        });

        // Start heartbeat ping
        this.startHeartbeat();
      };

      socket.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      socket.onerror = (err) => {
        const msg = (err as any)?.message || "Socket error";
        console.log(`[RealtimeChannel][${Date.now()}] ❌ ws.onerror: ${msg}`);
        this.setState("error");
        this.handlers.onError?.("WebSocket connection notice");
      };

      socket.onclose = (event: any) => {
        console.log(`[RealtimeChannel][${Date.now()}] 🔌 ws.onclose (code: ${event?.code}, reason: ${event?.reason || "None"}, wasClean: ${event?.wasClean})`);
        this.cleanupSocket();
        this.setState("disconnected");
        this.scheduleReconnect();
      };
    } catch (e) {
      console.log(`[RealtimeChannel][${Date.now()}] ❌ Connection initiation exception:`, (e as any)?.message || e);
      this.setState("error");
      this.scheduleReconnect();
    }
  }

  private handleMessage(rawData: any) {
    try {
      const msg = typeof rawData === "string" ? JSON.parse(rawData) : rawData;
      const event = msg.event;

      if (event === "session.ready") {
        const elapsed = Date.now() - this.connectStartTime;
        console.log(`[RealtimeChannel][${Date.now()}] ⚡ session.ready received (handshake elapsed: ${elapsed}ms, session_id: ${msg.session_id})`);
      } else if (event === "transcript.final") {
        console.log(`[RealtimeChannel] 🎙️ Transcript: "${msg.transcript}"`);
        this.handlers.onTranscript?.(msg.transcript, true);
      } else if (event === "response.chunk") {
        this.handlers.onResponseChunk?.(msg.delta, msg.sequence_index, msg.avatar_state);
      } else if (event === "audio.chunk") {
        console.log(`[RealtimeChannel] 🔊 Received Audio Chunk #${msg.sequence_index} (${msg.text || "audio"})`);
        const item: AudioQueueItem = {
          id: `ws-chunk-${Date.now()}-${msg.sequence_index}`,
          sequenceIndex: msg.sequence_index || 0,
          audioBase64: msg.audio_base64,
          text: msg.text,
          isLast: msg.isLast,
        };
        // Enqueue into gapless AudioQueuePlayer
        audioQueuePlayer.enqueue(item);
        this.handlers.onAudioChunk?.(item);
      } else if (event === "response.end") {
        console.log(`[RealtimeChannel] 🏁 Turn response finished (${msg.duration_ms}ms)`);
        this.handlers.onResponseEnd?.(msg.full_text || "", msg.duration_ms || 0);
      } else if (event === "interrupted") {
        console.log("[RealtimeChannel] ✋ Server acknowledged interruption.");
        this.handlers.onInterrupted?.();
      } else if (event === "error") {
        console.log("[RealtimeChannel] ℹ️ Server event notice:", msg.message);
        this.handlers.onError?.(msg.message || "Server error");
      }
    } catch (err) {
      console.log("[RealtimeChannel] Message parse note:", (err as any)?.message || err);
    }
  }

  /**
   * Sends voice audio turn over persistent WebSocket with optional camera frame
   */
  public sendAudio(audioBase64: string, imageBase64?: string, cameraTimestampMs?: number): boolean {
    if (!this.isAvailable()) {
      console.log("[RealtimeChannel] ℹ️ Channel not connected. Using HTTP Fallback.");
      return false;
    }

    this.sendRaw({
      event: "audio.send",
      audio_base64: audioBase64,
      image_base64: imageBase64 || undefined,
      camera_timestamp_ms: cameraTimestampMs || undefined,
    });
    return true;
  }

  /**
   * Sends immediate Barge-in interruption cancellation
   */
  public sendInterruption(): void {
    if (this.isAvailable()) {
      this.sendRaw({ event: "interruption" });
    }
  }

  private sendRaw(payload: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    }
  }

  private startHeartbeat(): void {
    if (this.pingInterval) clearInterval(this.pingInterval);
    this.pingInterval = setInterval(() => {
      if (this.isAvailable()) {
        this.sendRaw({ event: "ping", timestamp: Date.now() });
      }
    }, 15000);
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log(`[RealtimeChannel][${Date.now()}] ℹ️ Max reconnect attempts reached. Active with HTTP Fallback.`);
      return;
    }

    const delayMs = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), 10000);
    this.reconnectAttempts += 1;
    console.log(`[RealtimeChannel][${Date.now()}] 🔁 Reconnect attempt #${this.reconnectAttempts} (delay: ${delayMs}ms)...`);

    this.reconnectTimer = setTimeout(() => {
      this.connect(this.userId, this.companionId, this.conversationId);
    }, delayMs);
  }

  private cleanupSocket(): void {
    this.clearTimers();
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onerror = null;
      this.ws.onclose = null;
      try {
        this.ws.close();
      } catch (_) {}
      this.ws = null;
    }
  }

  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private setState(nextState: RealtimeChannelState): void {
    const oldState = this.state;
    this.state = nextState;
    console.log(`[RealtimeChannel][${Date.now()}] 🔄 State transition: ${oldState} -> ${nextState}`);
    this.handlers.onStateChange?.(this.state);
  }

  public disconnect(): void {
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
    this.cleanupSocket();
    this.setState("disconnected");
    console.log("[RealtimeChannel] Explicitly disconnected.");
  }
}

export const realtimeChannel = new RealtimeChannel();
