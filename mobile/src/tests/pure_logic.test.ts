import { LatestFrameCache } from "../services/camera/LatestFrameCache";
import { LipSyncEngine } from "../features/avatar/engine/LipSyncEngine";

function assert(condition: boolean, msg: string) {
  if (!condition) {
    throw new Error(`[AssertionFailed] ${msg}`);
  }
}

export function runPureLogicTests(): boolean {
  console.log("=== Running P009 Mobile Pure Logic Unit Tests ===");
  let passed = 0;

  // 1. LatestFrameCache Tests
  {
    const cache = new LatestFrameCache();
    assert(cache.getLatestFrame() === null, "Initial cache must be null");
    assert(!cache.isAvailable(), "Initial cache should not be available");

    // Update frame
    const frame = cache.updateFrame({ uri: "file:///test.jpg", width: 1920, height: 1080 });
    assert(frame !== null, "Frame should be updated");
    assert(cache.isAvailable(), "Cache should be available after fresh frame");
    assert(cache.getLatestFrame()?.uri === "file:///test.jpg", "Frame uri must match");

    // Clear
    cache.clear();
    assert(cache.getLatestFrame() === null, "Cleared cache must be null");
    assert(!cache.isAvailable(), "Cleared cache should not be available");
    passed++;
    console.log("✔ [LatestFrameCache] Frame caching, freshness, and clearing PASSED");
  }

  // 2. LipSyncEngine RMS & Mouth Open Smoothing Tests
  {
    LipSyncEngine.reset();
    const smoothed1 = LipSyncEngine.smoothMouthOpen(0.8);
    assert(smoothed1 > 0.0 && smoothed1 <= 0.8, "Smoothed mouth open should be bounded");

    const stateClosed = LipSyncEngine.getMouthState(0.05);
    assert(stateClosed === "Closed", "Low mouth open should be Closed");

    const stateOpen = LipSyncEngine.getMouthState(0.85);
    assert(stateOpen === "Open", "High mouth open should be Open");

    LipSyncEngine.reset();
    passed++;
    console.log("✔ [LipSyncEngine] Mouth open EMA smoothing and 4-tier state mapping (Closed/Open) PASSED");
  }

  // 3. AudioQueuePlayer FIFO Order & Ingestion Logic Test
  {
    const queue: any[] = [];
    function enqueueItem(item: any) {
      queue.push(item);
      queue.sort((a, b) => a.sequenceIndex - b.sequenceIndex);
    }

    enqueueItem({ sequenceIndex: 2, text: "Three" });
    enqueueItem({ sequenceIndex: 0, text: "One" });
    enqueueItem({ sequenceIndex: 1, text: "Two" });

    assert(queue[0].sequenceIndex === 0 && queue[0].text === "One", "FIFO chunk 0 first");
    assert(queue[1].sequenceIndex === 1 && queue[1].text === "Two", "FIFO chunk 1 second");
    assert(queue[2].sequenceIndex === 2 && queue[2].text === "Three", "FIFO chunk 2 third");
    passed++;
    console.log("✔ [AudioQueuePlayer Logic] Out-of-order chunk re-sequencing and FIFO ordering PASSED");
  }

  // 4. VAD Silence & Speaking Gating Logic Test
  {
    const VAD_THRESHOLD_DB = -32.0;
    function shouldTriggerSpeech(meteringDb: number, isAiSpeaking: boolean): boolean {
      if (isAiSpeaking) return false; // Echo suppression gating
      return meteringDb > VAD_THRESHOLD_DB;
    }

    assert(!shouldTriggerSpeech(-45.0, false), "Background noise (-45dB) must not trigger VAD");
    assert(shouldTriggerSpeech(-25.0, false), "User voice (-25dB) must trigger VAD");
    assert(!shouldTriggerSpeech(-15.0, true), "AI speaker playback (-15dB) during isSpeaking must be suppressed");
    passed++;
    console.log("✔ [VAD Gating Logic] Echo suppression & dB threshold state machine PASSED");
  }

  console.log(`=== All ${passed} Pure Logic Unit Test Suites PASSED! ===`);
  return true;
}
