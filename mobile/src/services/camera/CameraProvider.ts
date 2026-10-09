export type CameraPermissionStatus = 'UNKNOWN' | 'GRANTED' | 'DENIED' | 'RESTRICTED';

export interface CameraFrame {
  timestamp: number;
  data: any; // Image/buffer data
}

export interface UserPresenceState {
  isPresent: boolean;
  isLooking: boolean;
  distance: number; // estimated distance
}

export interface CameraProvider {
  initialize(): Promise<boolean>;
  getPermissionStatus(): CameraPermissionStatus;
  startCapture(): void;
  stopCapture(): void;
  captureFrame(): Promise<any | null>;
  getCurrentUserState(): UserPresenceState;
  setCameraRef?(ref: any): void;
}

export class RealCameraProvider implements CameraProvider {
  private permission: CameraPermissionStatus = 'GRANTED';
  private capturing: boolean = false;
  private cameraRef: any = null;

  setCameraRef(ref: any) {
    this.cameraRef = ref;
  }

  async initialize(): Promise<boolean> {
    this.permission = 'GRANTED';
    return true;
  }

  getPermissionStatus(): CameraPermissionStatus {
    return this.permission;
  }

  startCapture(): void {
    this.capturing = true;
    console.log("[RealCameraProvider] Real front camera capture started.");
  }

  stopCapture(): void {
    this.capturing = false;
    console.log("[RealCameraProvider] Real camera capture stopped.");
  }

  async captureFrame(): Promise<any | null> {
    if (!this.capturing) return null;

    if (this.cameraRef && typeof this.cameraRef.takePictureAsync === 'function') {
      try {
        const photo = await this.cameraRef.takePictureAsync({
          quality: 0.5,
          base64: true,
          skipProcessing: true,
          shutterSound: false,
        });
        return photo;
      } catch (err) {
        console.warn("[RealCameraProvider] Frame capture failed:", err);
      }
    }

    // Fallback: null if ref not ready (prevents React Native FormData Blob crash)
    return null;
  }

  getCurrentUserState(): UserPresenceState {
    return {
      isPresent: true,
      isLooking: true,
      distance: 0.5,
    };
  }
}

export class StubCameraProvider extends RealCameraProvider {}

