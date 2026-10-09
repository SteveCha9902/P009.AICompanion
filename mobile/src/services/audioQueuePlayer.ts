/**
 * Audio Queue Player for Continuous Streaming TTS (Expo SDK 57)
 * - Strict FIFO sequencing for streamed audio chunks
 * - Zero-overlap, seamless gapless playback transition
 * - Lifecycle controls: enqueue, play, pause, stop, flush, clear, onComplete
 */

import { createAudioPlayer, setAudioModeAsync } from "expo-audio";
import * as FileSystem from "expo-file-system/legacy";
import * as Speech from "expo-speech";

export interface AudioQueueItem {
  id: string;
  sequenceIndex: number;
  audioBase64?: string;
  audioUri?: string;
  text?: string;
  isLast?: boolean;
}

export type QueueCompleteCallback = () => void;
export type QueueChunkCallback = (item: AudioQueueItem) => void;

export class AudioQueuePlayer {
  private queue: AudioQueueItem[] = [];
  private isPlaying: boolean = false;
  private isPaused: boolean = false;
  private currentPlayingItem: AudioQueueItem | null = null;
  private currentPlayer: any = null;
  private statusPollingTimer: any = null;
  private isProcessing: boolean = false;
  private tempFiles: string[] = [];

  private completeListeners: Set<QueueCompleteCallback> = new Set();
  private chunkListeners: Set<QueueChunkCallback> = new Set();

  public onComplete(cb: QueueCompleteCallback): () => void {
    this.completeListeners.add(cb);
    return () => this.completeListeners.delete(cb);
  }

  public onChunkStart(cb: QueueChunkCallback): () => void {
    this.chunkListeners.add(cb);
    return () => this.chunkListeners.delete(cb);
  }

  public getQueueLength(): number {
    return this.queue.length;
  }

  public getIsPlaying(): boolean {
    return this.isPlaying;
  }

  /**
   * Enqueues an audio chunk in strict sequenceIndex order and starts playback if idle.
   */
  public async enqueue(item: AudioQueueItem): Promise<void> {
    if (!item) return;

    // Insert in strict chronological sequence order
    const insertIdx = this.queue.findIndex((q) => q.sequenceIndex > item.sequenceIndex);
    if (insertIdx === -1) {
      this.queue.push(item);
    } else {
      this.queue.splice(insertIdx, 0, item);
    }

    console.log(`[AudioQueuePlayer] Enqueued chunk #${item.sequenceIndex} (Queue size: ${this.queue.length})`);

    if (!this.isPlaying && !this.isPaused) {
      await this.play();
    }
  }

  public async play(): Promise<void> {
    if (this.isProcessing) return;
    this.isPaused = false;

    if (this.queue.length === 0 && !this.currentPlayingItem) {
      this.isPlaying = false;
      return;
    }

    this.isPlaying = true;
    await this.playNext();
  }

  public pause(): void {
    this.isPaused = true;
    if (this.currentPlayer) {
      try {
        this.currentPlayer.pause?.();
      } catch (_) {}
    }
  }

  public async stop(): Promise<void> {
    this.isPlaying = false;
    this.isPaused = false;
    this.isProcessing = false;
    this.clearTimers();

    await this.cleanupCurrentPlayer();
    this.currentPlayingItem = null;
    this.queue = [];

    this.cleanupTempFiles();
  }

  public clear(): void {
    this.queue = [];
  }

  public async flush(): Promise<void> {
    if (this.queue.length > 0 && !this.isPlaying) {
      await this.play();
    }
  }

  private clearTimers(): void {
    if (this.statusPollingTimer) {
      clearInterval(this.statusPollingTimer);
      this.statusPollingTimer = null;
    }
  }

  private async cleanupCurrentPlayer(): Promise<void> {
    this.clearTimers();
    if (this.currentPlayer) {
      try {
        this.currentPlayer.pause?.();
        this.currentPlayer.remove?.();
      } catch (_) {}
      this.currentPlayer = null;
    }
    try {
      Speech.stop();
    } catch (_) {}
  }

  private async playNext(): Promise<void> {
    if (this.isPaused || this.isProcessing) return;

    if (this.queue.length === 0) {
      this.isPlaying = false;
      this.currentPlayingItem = null;
      console.log("[AudioQueuePlayer] 🏁 All queued chunks finished playing.");
      this.completeListeners.forEach((cb) => cb());
      this.cleanupTempFiles();
      return;
    }

    this.isProcessing = true;
    const item = this.queue.shift()!;
    this.currentPlayingItem = item;

    console.log(`[AudioQueuePlayer] ▶️ Playing chunk #${item.sequenceIndex} (${item.text?.substring(0, 20) || "audio"}...)`);
    this.chunkListeners.forEach((cb) => cb(item));

    await this.cleanupCurrentPlayer();

    try {
      // 1. Base64 Audio Playback via Native AudioPlayer
      if (item.audioBase64 && item.audioBase64.length > 50) {
        const tempPath = `${FileSystem.cacheDirectory}queue_chunk_${Date.now()}_${item.sequenceIndex}.mp3`;
        this.tempFiles.push(tempPath);

        await FileSystem.writeAsStringAsync(tempPath, item.audioBase64, {
          encoding: FileSystem.EncodingType.Base64,
        });

        await setAudioModeAsync({
          allowsRecording: false,
          playsInSilentMode: true,
        });

        const player = createAudioPlayer(tempPath);
        this.currentPlayer = player;

        let hasHandledCompletion = false;
        const markComplete = () => {
          if (hasHandledCompletion) return;
          hasHandledCompletion = true;
          this.isProcessing = false;
          this.playNext();
        };

        // Event listener completion
        try {
          (player as any).addListener?.("playbackStatusUpdate", (status: any) => {
            if (status.didJustFinish) {
              markComplete();
            }
          });
        } catch (_) {}

        // Fallback polling for status completion (ensuring no deadlocks)
        this.statusPollingTimer = setInterval(() => {
          if (!this.currentPlayer) {
            this.clearTimers();
            return;
          }
          try {
            const status = this.currentPlayer.currentStatus;
            if (
              status &&
              (status.didJustFinish ||
                (status.currentTime > 0 && status.currentTime >= status.duration && status.duration > 0))
            ) {
              this.clearTimers();
              markComplete();
            }
          } catch (_) {}
        }, 150);

        player.play();
        this.isProcessing = false;
        return;
      }

      // 2. Audio URI Direct Playback
      if (item.audioUri) {
        const player = createAudioPlayer(item.audioUri);
        this.currentPlayer = player;

        let hasHandledCompletion = false;
        const markComplete = () => {
          if (hasHandledCompletion) return;
          hasHandledCompletion = true;
          this.isProcessing = false;
          this.playNext();
        };

        try {
          (player as any).addListener?.("playbackStatusUpdate", (status: any) => {
            if (status.didJustFinish) markComplete();
          });
        } catch (_) {}

        player.play();
        this.isProcessing = false;
        return;
      }

      // 3. Fallback to Speech if only text is present
      if (item.text) {
        Speech.speak(item.text, {
          language: "ko-KR",
          pitch: 1.05,
          rate: 1.0,
          onDone: () => {
            this.isProcessing = false;
            this.playNext();
          },
          onError: () => {
            this.isProcessing = false;
            this.playNext();
          },
        });
        return;
      }

      // If item is empty, skip to next
      this.isProcessing = false;
      this.playNext();
    } catch (err) {
      console.warn(`[AudioQueuePlayer] Error playing chunk #${item.sequenceIndex}:`, err);
      this.isProcessing = false;
      this.playNext();
    }
  }

  private cleanupTempFiles(): void {
    const filesToDelete = [...this.tempFiles];
    this.tempFiles = [];
    for (const path of filesToDelete) {
      FileSystem.deleteAsync(path, { idempotent: true }).catch(() => {});
    }
  }
}

export const audioQueuePlayer = new AudioQueuePlayer();
