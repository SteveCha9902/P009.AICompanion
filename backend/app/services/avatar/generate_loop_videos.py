import os
import cv2
import numpy as np
import imageio

def create_seamless_loop_videos():
    base_dir = r"d:\99.Repos\00.AntiGGG\P009.AICompanion"
    assets_dir = os.path.join(base_dir, "assets", "avatar_characters")
    output_dir = os.path.join(base_dir, "mobile", "assets", "avatar")
    os.makedirs(output_dir, exist_ok=True)

    img_neutral = cv2.imread(os.path.join(assets_dir, "genie_v2_neutral.jpg"))
    img_smile = cv2.imread(os.path.join(assets_dir, "genie_v2_smile.jpg"))
    img_thinking = cv2.imread(os.path.join(assets_dir, "genie_v2_thinking.jpg"))
    img_speaking = cv2.imread(os.path.join(assets_dir, "genie_v2_speaking.jpg"))
    img_listening = cv2.imread(os.path.join(assets_dir, "genie_v2_listening.jpg"))

    # Convert BGR to RGB for imageio
    def to_rgb(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    rgb_neutral = to_rgb(img_neutral)
    rgb_smile = to_rgb(img_smile)
    rgb_thinking = to_rgb(img_thinking)
    rgb_speaking = to_rgb(img_speaking)
    rgb_listening = to_rgb(img_listening)

    h, w, _ = rgb_neutral.shape
    fps = 30

    # 1. IDLE Loop (3.0s, 90 frames) - Subtle breathing & micro-sway
    idle_frames = []
    total_frames = 90
    for i in range(total_frames):
        t = i / total_frames
        # Smooth sinusoidal cycle
        phase = np.sin(2 * np.pi * t)
        scale = 1.0 + 0.015 * phase
        ty = int(3 * np.sin(2 * np.pi * t))
        tx = int(1.5 * np.cos(2 * np.pi * t))

        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0.2 * phase, scale)
        M[0, 2] += tx
        M[1, 2] += ty
        warped = cv2.warpAffine(rgb_neutral, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        idle_frames.append(warped)

    imageio.mimsave(os.path.join(output_dir, "idle.mp4"), idle_frames, fps=fps, quality=8)
    print("[CREATED] idle.mp4")

    # 2. SPEAKING Loop (2.0s, 60 frames) - Natural speech articulation & head nod
    speaking_frames = []
    total_frames = 60
    for i in range(total_frames):
        t = i / total_frames
        # Dual rhythm for natural speaking cadence
        alpha = 0.5 * (1 + np.sin(4 * np.pi * t))
        ty = int(4 * np.sin(2 * np.pi * t))
        
        # Blend speaking and neutral
        blended = cv2.addWeighted(rgb_speaking, alpha, rgb_neutral, 1 - alpha, 0)
        
        # Subtle head motion
        scale = 1.0 + 0.01 * np.sin(2 * np.pi * t)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0.3 * np.sin(2 * np.pi * t), scale)
        M[1, 2] += ty
        warped = cv2.warpAffine(blended, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        speaking_frames.append(warped)

    imageio.mimsave(os.path.join(output_dir, "speaking.mp4"), speaking_frames, fps=fps, quality=8)
    print("[CREATED] speaking.mp4")

    # 3. THINKING Loop (3.0s, 90 frames) - Pondering & slight tilt
    thinking_frames = []
    total_frames = 90
    for i in range(total_frames):
        t = i / total_frames
        alpha = 0.5 * (1 + np.sin(2 * np.pi * t))
        blended = cv2.addWeighted(rgb_thinking, alpha, rgb_neutral, 1 - alpha, 0)
        scale = 1.0 + 0.012 * np.sin(2 * np.pi * t)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), -0.4 * np.sin(2 * np.pi * t), scale)
        warped = cv2.warpAffine(blended, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        thinking_frames.append(warped)

    imageio.mimsave(os.path.join(output_dir, "thinking.mp4"), thinking_frames, fps=fps, quality=8)
    print("[CREATED] thinking.mp4")

    # 4. SMILE Loop (2.5s, 75 frames) - Warm reacting smile
    smile_frames = []
    total_frames = 75
    for i in range(total_frames):
        t = i / total_frames
        alpha = 0.5 * (1 + np.sin(2 * np.pi * t))
        blended = cv2.addWeighted(rgb_smile, alpha, rgb_neutral, 1 - alpha, 0)
        scale = 1.0 + 0.01 * np.sin(2 * np.pi * t)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0.2 * np.sin(2 * np.pi * t), scale)
        warped = cv2.warpAffine(blended, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        smile_frames.append(warped)

    imageio.mimsave(os.path.join(output_dir, "smile.mp4"), smile_frames, fps=fps, quality=8)
    print("[CREATED] smile.mp4")

if __name__ == "__main__":
    create_seamless_loop_videos()
