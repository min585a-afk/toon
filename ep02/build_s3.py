"""EP02 장면 3: 1화 컴퓨터 앞 장면(은서 타닥 → 눈만 위로, ep01b/video/c00-gyul-type-look-h3.mp4) + 왼쪽 앞 최버터 뒷모습(편집 1cr, 대리만 프레임마다 덮음). 크레딧 0.
usage: python3 ep02/build_s3.py → ep02/s3-butter-back.mp4
"""
import subprocess, tempfile, wave
import numpy as np, cv2
FPS, W, H, SR = 24, 1080, 810, 44100
TYPE, LOOK = 1.6, 0.9                                          # 은서 혼자 타닥 → 최버터가 왼쪽에서 다가옴(0.8~1.6초) → 눈 위로(영상 끝 0.9초)
IN0, IN1 = 0.75, 1.55                                          # 다가오는 구간 (혁 10/29: 일하는 은서에게 최버터가 오는 연결)
cap = cv2.VideoCapture('ep01b/video/c00-gyul-type-look-h3.mp4'); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32))
base = cv2.resize(cv2.imread('ep02/s3-base.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
edit = cv2.resize(cv2.imread('ep02/s3-butter-back2.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)   # 혁 10/29: 더 위 · 왼쪽 30% 만 (편집 2번째 1cr)
m = (cv2.imread('ep02/s3-butter-back2-mask.png', 0) > 127).astype(np.uint8)                                          # GrabCut 으로 대리만 오림
M = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2)[..., None]
n = int((TYPE + LOOK) * FPS); v0 = len(v) / vf - LOOK - TYPE
tmp = tempfile.mkdtemp()
for k in range(n):
    fr = v[min(len(v) - 1, int((v0 + (k - k % 2) / FPS) * vf))]
    t = (k - k % 2) / FPS; p = np.clip((t - IN0) / (IN1 - IN0), 0, 1); p = 1 - (1 - p) ** 2.2          # 다가와서 멈춤(ease-out)
    dx = -W * 0.4 * (1 - p); dy = -10 * abs(np.sin(p * np.pi * 3)) * (1 - p)                          # 걸음 살짝 들썩
    A = np.float32([[1, 0, dx], [0, 1, dy]]); e2 = cv2.warpAffine(edit, A, (W, H)); m2 = cv2.warpAffine(M, A, (W, H))[..., None] if M.ndim == 3 else cv2.warpAffine(M, A, (W, H))
    m2 = m2.reshape(H, W, 1)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(fr * (1 - m2) + e2 * m2, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
typing = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/typing-norm.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(n / FPS * SR), np.float32); L = int(TYPE * SR); a[:L] = np.tile(typing, 3)[:L] * 0.45; a[L - 800:L] *= np.linspace(1, 0, 800)
step = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/heel-step.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
for i, t in enumerate(np.arange(0.35, IN1 + 0.01, 0.3)):
    j = int(t * SR); a[j:j + len(step)] += step[:len(a) - j] * (0.12 + 0.1 * i)
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s3-butter-back.mp4'], check=True)
print('ep02/s3-butter-back.mp4', round(n / FPS, 2), 's')
