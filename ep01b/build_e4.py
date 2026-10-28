"""EP01 뒷부분 장면 4: (은서 분노 컷 다음) 강서늘 멈춘 뒷모습 → 오른쪽으로 휙 돌아봄 (그림 4장: 뒷모습 → 반쯤 → 옆얼굴 → 돌아봄·안경 번쩍) → 멈춤. 크레딧 0.
usage: python3 ep01b/build_e4.py  → ep01b/e4-boss-turn.mp4
"""
import subprocess, tempfile, wave
import numpy as np
import cv2

FPS, W, H, SR = 24, 1080, 810, 44100
sz = lambda p: cv2.resize(cv2.imread(p), (W, H), interpolation=cv2.INTER_AREA)
cap = cv2.VideoCapture('ep01b/video/e2-boss-leave-h3.mp4'); f = cap.get(cv2.CAP_PROP_FPS) or 24; v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
walk = [v[min(len(v) - 1, int((1.5 + (k - k % 2) / FPS) * f))] for k in range(12)]          # 0.5초 걷다가
back, half, side, look = [sz(f'ep01b/e5-boss-far-{n}.png' if n == 'back' else f'ep01b/e5-boss-far-{n}-fix.png') for n in ['back', 'half', 'side', 'look']]
walk = []                                                                                   # 걷기는 장면 2 에 (사이에 은서 분노 컷)
frames = [back] * 8 + [half] * 1 + [side] * 1 + [look] * 26                                 # 멈춘 뒷모습 0.33초 → 휙 (2프레임) → 돌아봄 1.1초
TURN = len(walk) + 5
step = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/heel-step.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
glint = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/glint.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(len(frames) / FPS * SR) + SR, np.float32)
j = int(0.05 * SR); a[j:j + len(step)] += step[:len(a) - j] * 0.25                            # 마지막 또각 (멈칫)
j = int((TURN + 2) / FPS * SR); a[j:j + len(glint)] += glint[:len(a) - j] * 0.7               # 돌아본 순간 안경 번쩍
tmp = tempfile.mkdtemp()
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep01b/e4-boss-turn.mp4'], check=True)
print('ep01b/e4-boss-turn.mp4', round(len(frames) / FPS, 2), 's')
