/**
 * Voice Controller (Expo SDK 57 / Gemini Live Continuous Hands-Free & Whisper STT Engine)
 * - Records microphone audio via AudioModule.AudioRecorder with flattened platform options
 * - Real-time adaptive VAD (Voice Activity Detection) using metering levels & 800ms silence detection
 * - High-Quality Neural TTS (Microsoft Edge Neural Voice MP3) playback via AudioPlayer
 * - Seamless hands-free loop for Gemini Live continuous conversation
 */

import {
  AudioModule,
  createAudioPlayer,
  requestRecordingPermissionsAsync,
  getRecordingPermissionsAsync,
  setAudioModeAsync,
} from "expo-audio";
import * as FileSystem from "expo-file-system/legacy";
import * as Speech from "expo-speech";
import { Platform } from "react-native";
import { API_URL } from "../config/env";
import { avatarService } from "../features/avatar/services/avatar_service";

import { audioQueuePlayer } from "./audioQueuePlayer";
import { latestFrameCache } from "./camera/LatestFrameCache";
import { realtimeChannel } from "./realtimeChannel";

export type VoiceState = 
  | "idle" 
  | "listening" 
  | "transcribing" 
  | "thinking" 
  | "speaking" 
  | "interrupted" 
  | "error";

type VoiceStateListener = (state: VoiceState, isLive: boolean) => void;
type VoiceMessageListener = (userText: string, assistantText: string) => void;

class VoiceController {
  private state: VoiceState = "idle";
  private isLiveMode: boolean = false;
  private currentSessionId: string | null = null;
  private currentUserId: string = "default_user";
  private currentCompanionId: string = "default_companion";
  private currentConversationId: string = "default";
  private recorder: any = null;
  private listeners: Set<VoiceStateListener> = new Set();
  private messageListeners: Set<VoiceMessageListener> = new Set();
  private isSpeaking: boolean = false;
  private autoStopTimer: any = null;
  private vadInterval: any = null;
  private loopTimer: any = null;
  private lastSpokenText: string = "";
  private lastSpokenTimestamp: number = 0;

  // VAD state tracking
  private hasDetectedSpeech: boolean = false;
  private silenceStartTime: number = 0;

  constructor() {
    // Connect audio queue completion to Live loop resumption
    audioQueuePlayer.onComplete(() => {
      this.handlePlaybackComplete();
    });

    // Setup Realtime WebSocket event listeners
    realtimeChannel.setHandlers({
      onTranscript: (transcript: string) => {
        this.notifyMessages(transcript, "");
      },
      onResponseEnd: (fullText: string) => {
        this.notifyMessages("", fullText);
      },
    });
  }

  public getState(): VoiceState {
    return this.state;
  }

  public getIsLiveMode(): boolean {
    return this.isLiveMode;
  }

  public subscribe(listener: VoiceStateListener): () => void {
    this.listeners.add(listener);
    listener(this.state, this.isLiveMode);
    return () => {
      this.listeners.delete(listener);
    };
  }

  public subscribeMessages(listener: VoiceMessageListener): () => void {
    this.messageListeners.add(listener);
    return () => {
      this.messageListeners.delete(listener);
    };
  }

  private notifyMessages(userText: string, assistantText: string) {
    this.messageListeners.forEach((l) => l(userText, assistantText));
  }

  private setState(nextState: VoiceState) {
    this.state = nextState;
    this.listeners.forEach((l) => l(this.state, this.isLiveMode));

    // Synchronize Avatar Conversation State directly with Voice Pipeline
    switch (nextState) {
      case "listening":
        avatarService.setConversationState("LISTENING");
        break;
      case "transcribing":
      case "thinking":
        avatarService.setConversationState("THINKING");
        break;
      case "speaking":
        avatarService.setConversationState("SPEAKING");
        break;
      case "interrupted":
        avatarService.setConversationState("INTERRUPTED");
        break;
      case "error":
        avatarService.setConversationState("ERROR");
        break;
      case "idle":
      default:
        avatarService.setConversationState("IDLE");
        break;
    }
  }

  public async toggleLiveMode(userId: string, companionId: string, conversationId: string): Promise<boolean> {
    if (this.isLiveMode) {
      await this.stopLiveMode();
      return false;
    } else {
      return await this.startLiveMode(userId, companionId, conversationId);
    }
  }

  public async startLiveMode(userId: string, companionId: string, conversationId: string): Promise<boolean> {
    this.isLiveMode = true;
    console.log("[VoiceController] ⚡ Gemini Live Hands-Free Mode ACTIVATED.");
    return await this.startListening(userId, companionId, conversationId);
  }

  public async stopLiveMode(): Promise<void> {
    this.isLiveMode = false;
    this.clearTimers();
    await this.interrupt();
    this.setState("idle");
    console.log("[VoiceController] ⚡ Gemini Live Mode DEACTIVATED.");
  }

  private clearTimers() {
    if (this.loopTimer) {
      clearTimeout(this.loopTimer);
      this.loopTimer = null;
    }
    if (this.autoStopTimer) {
      clearTimeout(this.autoStopTimer);
      this.autoStopTimer = null;
    }
    if (this.vadInterval) {
      clearInterval(this.vadInterval);
      this.vadInterval = null;
    }
  }

  public async startListening(userId: string, companionId: string, conversationId: string): Promise<boolean> {
    this.currentUserId = userId || "default_user";
    this.currentCompanionId = companionId || "default_companion";
    this.currentConversationId = conversationId || "default";

    // 1. Interrupt any active playback or recording
    if (this.isSpeaking || this.state === "speaking") {
      await this.interrupt();
    }

    this.clearTimers();
    this.hasDetectedSpeech = false;
    this.silenceStartTime = 0;

    // Connect / warm up persistent real-time channel
    realtimeChannel.connect(this.currentUserId, this.currentCompanionId, this.currentConversationId);

    try {
      // 2. Microphone Permissions
      let perm = await getRecordingPermissionsAsync();
      if (!perm.granted) {
        perm = await requestRecordingPermissionsAsync();
      }

      if (!perm.granted) {
        console.warn("[VoiceController] Microphone permission denied.");
        this.setState("error");
        setTimeout(() => this.setState("idle"), 2500);
        return false;
      }

      // 3. Set Audio Mode for Recording
      await setAudioModeAsync({
        allowsRecording: true,
        playsInSilentMode: true,
      });

      // Cleanup previous recorder if any
      if (this.recorder) {
        try {
          await this.recorder.stop();
        } catch (_) {}
        this.recorder = null;
      }

      // 4. Create AudioRecorder instance
      if (AudioModule && AudioModule.AudioRecorder) {
        const platformOptions = Platform.select({
          android: {
            extension: ".m4a",
            sampleRate: 44100,
            numberOfChannels: 1,
            bitRate: 128000,
            isMeteringEnabled: true,
            outputFormat: "mpeg4",
            audioEncoder: "aac",
          },
          ios: {
            extension: ".m4a",
            sampleRate: 44100,
            numberOfChannels: 1,
            bitRate: 128000,
            isMeteringEnabled: true,
            outputFormat: "aac ",
            audioQuality: 127,
            linearPCMBitDepth: 16,
            linearPCMIsBigEndian: false,
            linearPCMIsFloat: false,
          },
          default: {
            extension: ".m4a",
            sampleRate: 44100,
            numberOfChannels: 1,
            bitRate: 128000,
            isMeteringEnabled: true,
          },
        });

        this.recorder = new AudioModule.AudioRecorder(platformOptions as any);
        await this.recorder.prepareToRecordAsync();
        this.recorder.record();
        console.log("[VoiceController] Audio recording started. LiveMode:", this.isLiveMode);

        // 5. Start Adaptive VAD (Voice Activity Detection) Polling every 150ms
        this.vadInterval = setInterval(() => {
          if (this.state !== "listening" || !this.recorder) return;
          try {
            const status = this.recorder.getStatus?.();
            if (status && typeof status.metering === "number") {
              const db = status.metering; // dB level: typically -160 to 0
              
              // Speech onset threshold (above -34 dB)
              if (db > -34) {
                if (!this.hasDetectedSpeech) {
                  this.hasDetectedSpeech = true;
                  console.log(`[VoiceController VAD] Speech detected (metering: ${db.toFixed(1)} dB)`);
                }
                this.silenceStartTime = 0; // reset silence counter while speaking
              } else if (this.hasDetectedSpeech) {
                // Speech was detected, now below threshold (-38 dB)
                if (db < -38) {
                  if (this.silenceStartTime === 0) {
                    this.silenceStartTime = Date.now();
                  } else if (Date.now() - this.silenceStartTime > 800) {
                    // 800ms silence detected after speech -> User finished utterance!
                    console.log(`[VoiceController VAD] Utterance complete (800ms silence). Submitting immediately!`);
                    this.clearTimers();
                    this.stopListeningAndSend();
                  }
                } else {
                  this.silenceStartTime = 0;
                }
              }
            }
          } catch (_) {}
        }, 150);

      } else {
        console.warn("[VoiceController] AudioModule.AudioRecorder not available.");
      }

      this.setState("listening");
      avatarService.setSpeaking(false);

      // Safety Maximum Timeout (6s in Live mode, 8s in Manual mode)
      const maxTimeoutMs = this.isLiveMode ? 6000 : 8000;
      this.autoStopTimer = setTimeout(() => {
        if (this.state === "listening") {
          console.log(`[VoiceController] Max recording safety limit reached (${maxTimeoutMs}ms). Processing...`);
          this.stopListeningAndSend();
        }
      }, maxTimeoutMs);

      // Async initialize voice session on backend
      if (!this.currentSessionId) {
        fetch(`${API_URL}/api/v1/voice/sessions`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-user-id": this.currentUserId,
          },
          body: JSON.stringify({
            user_id: this.currentUserId,
            companion_id: this.currentCompanionId,
            conversation_id: this.currentConversationId,
          }),
        })
          .then((res) => res.json())
          .then((data) => {
            if (data && data.session_id) {
              this.currentSessionId = data.session_id;
            }
          })
          .catch((err) => {
            console.debug("[VoiceController] Session create non-blocking fallback:", err);
          });
      }
      return true;
    } catch (e) {
      console.warn("[VoiceController] startListening error:", e);
      this.recorder = null;
      this.clearTimers();
      this.setState("error");
      setTimeout(() => this.setState("idle"), 2500);
      return false;
    }
  }

  /**
   * Compatibility wrapper for text speech playback
   */
  public async speakText(text: string): Promise<void> {
    await this.playVoiceResponse("", text);
  }

  /**
   * Play high-quality neural voice audio (MP3 Base64) with native AudioPlayer,
   * falling back to expo-speech if needed.
   */
  public async playVoiceResponse(audioBase64: string, textReply: string): Promise<void> {
    const trimmed = textReply?.trim();
    const now = Date.now();

    // Deduplication guard (prevent repeating same text within 3 seconds)
    if (trimmed && this.lastSpokenText === trimmed && now - this.lastSpokenTimestamp < 3000) {
      console.log("[VoiceController] Suppressing duplicate speech for:", trimmed);
      if (this.isLiveMode) {
        this.scheduleLiveRelisten(400);
      }
      return;
    }

    if (trimmed) {
      this.lastSpokenText = trimmed;
      this.lastSpokenTimestamp = now;
    }

    // Interrupt any previous playback
    await this.stopCurrentAudio();

    this.setState("speaking");
    this.isSpeaking = true;
    avatarService.setSpeaking(true);

    // Enqueue chunk into AudioQueuePlayer for gapless playback
    await audioQueuePlayer.enqueue({
      id: `chunk-${Date.now()}`,
      sequenceIndex: 0,
      audioBase64: audioBase64,
      text: trimmed,
      isLast: true,
    });
  }

  private handlePlaybackComplete() {
    this.isSpeaking = false;
    avatarService.setSpeaking(false);
    this.setState("idle");

    // ⚡ Gemini Live Mode: Automatically resume listening loop!
    if (this.isLiveMode) {
      this.scheduleLiveRelisten(350);
    }
  }

  private async stopCurrentAudio(): Promise<void> {
    await audioQueuePlayer.stop();
  }


  private scheduleLiveRelisten(delayMs: number = 350) {
    if (!this.isLiveMode) return;
    if (this.loopTimer) clearTimeout(this.loopTimer);

    this.loopTimer = setTimeout(() => {
      if (this.isLiveMode && (this.state === "idle" || this.state === "interrupted")) {
        console.log("[VoiceController] ⚡ Live Mode: Auto-resuming listening loop...");
        this.startListening(this.currentUserId, this.currentCompanionId, this.currentConversationId);
      }
    }, delayMs);
  }

  public async stopListeningAndSend(): Promise<void> {
    const t_utterance_end = Date.now();
    this.clearTimers();

    if (this.state !== "listening") return;

    this.setState("transcribing");

    try {
      let uri: string | null = null;

      if (this.recorder) {
        try {
          await this.recorder.stop();
        } catch (_) {}
        uri = this.recorder.uri;
        this.recorder = null;
      }

      if (!uri) {
        console.warn("[VoiceController] No recorded audio URI found.");
        this.setState("idle");
        if (this.isLiveMode) {
          this.scheduleLiveRelisten(500);
        }
        return;
      }

      const targetSessionId = this.currentSessionId || `voice-${Date.now()}`;
      this.setState("thinking");
      avatarService.updatePartialState({ animation: "thinking" });

      const t_upload_start = Date.now();
      console.log(`[VoiceController][LATENCY] Upload Start -> /voice/sessions/${targetSessionId}/audio`);

      // Multimodal Binding: Check for fresh camera frame
      const cachedFrame = latestFrameCache.getLatestFrame();
      const uploadParams: Record<string, string> = {
        user_id: this.currentUserId,
        companion_id: this.currentCompanionId,
        conversation_id: this.currentConversationId,
      };

      if (cachedFrame && cachedFrame.base64 && cachedFrame.status === "ready") {
        uploadParams.image_base64 = cachedFrame.base64;
        uploadParams.camera_timestamp_ms = String(cachedFrame.timestamp);
        const timeDiffMs = Math.abs(t_utterance_end - cachedFrame.timestamp);
        console.log(`[VoiceController] 📸 One-Shot Multimodal: Bound Frame #${cachedFrame.frameId} (Time diff: ${timeDiffMs}ms)`);
      } else {
        console.log("[VoiceController] 🎙️ Audio-only mode (No fresh camera frame or camera unavailable)");
      }

      // 1. Dual-Path: Use Persistent Realtime Channel if connected
      const channelState = realtimeChannel.getState();
      const channelAvailable = realtimeChannel.isAvailable();
      console.log(`[VoiceController][${Date.now()}] stopListeningAndSend -> RealtimeChannel state: '${channelState}', isAvailable: ${channelAvailable}`);

      if (channelAvailable) {
        console.log(`[VoiceController][PATH] WS (state='${channelState}', isAvailable=true)`);
        try {
          const audioBase64 = await FileSystem.readAsStringAsync(uri, {
            encoding: FileSystem.EncodingType.Base64,
          });

          console.log(`[VoiceController] ⚡ Sending Voice Turn via Persistent Realtime Channel (${audioBase64.length} chars)`);
          const sent = realtimeChannel.sendAudio(
            audioBase64,
            cachedFrame?.base64,
            cachedFrame?.timestamp
          );

          if (sent) {
            // Realtime audio stream chunks will be received and played gaplessly via AudioQueuePlayer!
            return;
          }
        } catch (wsSendErr) {
          console.warn("[VoiceController] Realtime send failed, falling back to HTTP:", wsSendErr);
        }
      }

      // 2. HTTP Fallback: Native Multipart File Upload with FormData safety fallback
      console.log(`[VoiceController][PATH] HTTP-FALLBACK (reason=realtimeChannel.state is '${channelState}', isAvailable=${channelAvailable}) -> /voice/sessions/${targetSessionId}/audio`);
      let rawBody: string | null = null;
      let statusCode = 0;

      try {
        const uploadResult = await FileSystem.uploadAsync(
          `${API_URL}/api/v1/voice/sessions/${targetSessionId}/audio`,
          uri,
          {
            httpMethod: "POST",
            uploadType: FileSystem.FileSystemUploadType.MULTIPART,
            fieldName: "file",
            mimeType: "audio/m4a",
            parameters: uploadParams,
          }
        );
        statusCode = uploadResult.status;
        rawBody = uploadResult.body;
      } catch (fsErr) {
        // Fallback: standard FormData fetch
        const formData = new FormData();
        formData.append("file", {
          uri: uri,
          name: "audio.m4a",
          type: "audio/m4a",
        } as any);

        Object.entries(uploadParams).forEach(([k, v]) => {
          if (v !== undefined && v !== null) {
            formData.append(k, String(v));
          }
        });

        const res = await fetch(`${API_URL}/api/v1/voice/sessions/${targetSessionId}/audio`, {
          method: "POST",
          body: formData,
        });
        statusCode = res.status;
        rawBody = await res.text();
      }

      const t_receive = Date.now();
      const upload_roundtrip_ms = t_receive - t_upload_start;
      console.log(`[VoiceController][LATENCY] Response Received (${upload_roundtrip_ms}ms roundtrip)`);

      if (statusCode < 200 || statusCode >= 300 || !rawBody) {
        throw new Error(`Voice upload failed with status ${statusCode}: ${rawBody}`);
      }

      const data = JSON.parse(rawBody);
      const userTranscript = data.transcript || "";
      const assistantReply = data.response_text || "";
      const audioBase64 = data.audio_base64 || "";

      if (userTranscript || assistantReply) {
        this.notifyMessages(userTranscript, assistantReply);
      }

      // Configure Audio Mode for Playback
      await setAudioModeAsync({
        allowsRecording: false,
        playsInSilentMode: true,
      });

      // Play high-quality neural voice response
      if (audioBase64 || assistantReply) {
        await this.playVoiceResponse(audioBase64, assistantReply);
        const t_playback_start = Date.now();
        const total_ttfa_ms = t_playback_start - t_utterance_end;
        console.log(
          `[VoiceController][LATENCY-SUMMARY] ⚡ TTFA (Speech End -> Audio Start): ${total_ttfa_ms}ms ` +
          `(Roundtrip: ${upload_roundtrip_ms}ms, Client Prep: ${t_playback_start - t_receive}ms)`
        );
      } else {
        this.setState("idle");
        avatarService.setSpeaking(false);
        if (this.isLiveMode) {
          this.scheduleLiveRelisten(400);
        }
      }
    } catch (err: any) {
      console.log("[VoiceController] ℹ️ stopListeningAndSend notice (Auto-Recovering):", err?.message || err);
      this.isSpeaking = false;
      avatarService.setSpeaking(false);
      this.setState("error");
      setTimeout(() => {
        if (this.state === "error") {
          this.setState("idle");
          if (this.isLiveMode) {
            this.scheduleLiveRelisten(600);
          }
        }
      }, 2000);
    }
  }

  /**
   * State-Aware Barge-in: AI Speaking -> User Voice Detected -> Stop TTS -> Flush Queue -> New Turn
   */
  public async handleBargeIn(): Promise<void> {
    if (this.state !== "speaking" && !audioQueuePlayer.getIsPlaying() && !this.isSpeaking) {
      return;
    }

    console.log("[VoiceController] 🛑 BARGE-IN DETECTED: User interrupted AI speech! Stopping audio immediately.");
    this.clearTimers();

    // 1. Immediately stop audio playback & flush queue
    await audioQueuePlayer.stop();
    this.isSpeaking = false;
    avatarService.setSpeaking(false);
    this.setState("interrupted");

    // 2. Notify remote backend to cancel pending LLM/TTS streams
    realtimeChannel.sendInterruption();
    if (this.currentSessionId) {
      fetch(`${API_URL}/api/v1/voice/sessions/${this.currentSessionId}/interrupt`, {
        method: "POST",
      }).catch((e) => console.warn("[VoiceController] Remote interrupt non-blocking:", e));
    }

    // 3. Immediately transition to listening for the new user utterance (New Turn)
    setTimeout(() => {
      console.log("[VoiceController] 🎙️ Transitioning to new user turn after interruption...");
      this.startListening(this.currentUserId, this.currentCompanionId, this.currentConversationId);
    }, 100);
  }

  public async interrupt(): Promise<void> {
    this.clearTimers();

    if (this.recorder) {
      try {
        await this.recorder.stop();
      } catch (e) {}
      this.recorder = null;
    }

    await this.stopCurrentAudio();

    this.isSpeaking = false;
    avatarService.setSpeaking(false);
    this.setState("interrupted");

    if (this.currentSessionId) {
      try {
        await fetch(`${API_URL}/api/v1/voice/sessions/${this.currentSessionId}/interrupt`, {
          method: "POST",
        });
      } catch (e) {
        console.warn("[VoiceController] Remote interrupt failed:", e);
      }
    }
  }

  public cleanup(): void {
    this.isLiveMode = false;
    this.interrupt();
    this.setState("idle");
  }
}

export const voiceController = new VoiceController();

