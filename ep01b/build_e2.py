"""EP01 뒷부분 장면 2: 강서늘 뒤돌아 통로로 걸어 나감 (H3 앞 2.4초 · 12fps) + 또각또각 멀어짐 — '잘 부탁해요~' 자리 (목소리 나중). 크레딧 0.
usage: python3 ep01b/build_e2.py  → ep01b/e2-boss-leave.mp4
"""
import subprocess, tempfile, wave
import numpy as np
import cv2

FPS, W, H, SR, SEC = 24, 1080, 810, 44100, 2.4
cap = cv2.VideoCapture('ep01b/video/e2-boss-leave-h3.mp4'); f = cap.get(cv2.CAP_PROP_FPS) or 24; v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
n = int(SEC * FPS); frames = [v[min(len(v) - 1, int((k - k % 2) / FPS * f))] for k in range(n)]
step = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/heel-step.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(SEC * SR), np.float32)
for i, t in enumerate(np.arange(0.1, SEC - 0.1, 0.4)):
    j = int(t * SR); a[j:j + len(step)] += step[:len(a) - j] * 0.45 * (1 - i / 7)      # 멀어지며 작아짐
tmp = tempfile.mkdtemp()
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep01b/e2-boss-leave.mp4'], check=True)
print('ep01b/e2-boss-leave.mp4', SEC, 's')
