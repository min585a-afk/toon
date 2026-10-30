"""EP02 장면 3: 1화 컴퓨터 앞 장면(은서 타닥 → 눈만 위로, ep01b/video/c00-gyul-type-look-h3.mp4) + 왼쪽 앞 최버터 뒷모습(편집 1cr, 대리만 프레임마다 덮음). 크레딧 0.
usage: python3 ep02/build_s3.py → ep02/s3-butter-back.mp4
"""
import subprocess, tempfile, wave
import numpy as np, cv2, sys
sys.path.insert(0, 'tools'); from recolor_outfit import to_black
FPS, W, H, SR = 24, 1080, 810, 44100
TYPE, LOOK = 1.6, 1.6                                          # 은서 혼자 타닥 → 최버터가 왼쪽에서 다가옴(0.8~1.6초) → 눈 위로(영상 끝 0.9초 + 마지막 그림 0.7초 · 혁 10/30 "은서 씨~?" 끝까지)
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
# 혁 10/29: 2화 빨간 리본 — 편집본(1cr)에서 리본만 떼서 은서 머리 움직임 따라 붙임
RIB = cv2.resize(cv2.imread('ep02/s3-ribbon-aligned.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
RM = cv2.GaussianBlur(cv2.resize(cv2.imread('ep02/s3-ribbon-mask.png', 0), (W, H)).astype(np.float32) / 255, (0, 0), 1.5)[..., None]
HB = (430, 760, 90, 360)                                       # 머리 추적 영역 x0 x1 y0 y1
gray = lambda im: cv2.cvtColor(im[HB[2]:HB[3], HB[0]:HB[1]].astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
G0 = gray(base)
n = int((TYPE + LOOK) * FPS); v0 = len(v) / vf - LOOK - TYPE
tmp = tempfile.mkdtemp()
for k in range(n):
    fr = to_black(v[min(len(v) - 1, int((v0 + (k - k % 2) / FPS) * vf))], y_min=0.35, x_range=(0.3, 0.85), face=(0.53, 0.34, 0.14, 0.14))   # 2화 복장: 검정 가디건
    (hx, hy), _ = cv2.phaseCorrelate(G0, gray(fr)); A2 = np.float32([[1, 0, hx], [0, 1, hy]])
    rm = cv2.warpAffine(RM, A2, (W, H)).reshape(H, W, 1); fr = fr * (1 - rm) + cv2.warpAffine(RIB, A2, (W, H)) * rm
    t = (k - k % 2) / FPS; p = np.clip((t - IN0) / (IN1 - IN0), 0, 1); p = 1 - (1 - p) ** 2.2          # 다가와서 멈춤(ease-out)
    dx = -W * 0.4 * (1 - p); dy = -10 * abs(np.sin(p * np.pi * 3)) * (1 - p)                          # 걸음 살짝 들썩
    A = np.float32([[1, 0, dx], [0, 1, dy]]); e2 = cv2.warpAffine(edit, A, (W, H)); m2 = cv2.warpAffine(M, A, (W, H))[..., None] if M.ndim == 3 else cv2.warpAffine(M, A, (W, H))
    m2 = m2.reshape(H, W, 1)
    o = np.clip(fr * (1 - m2) + e2 * m2, 0, 255).astype(np.uint8)
    if t > TYPE + 0.6:                                             # 영상 끝나고 멈춘 동안 천천히 다가감 (혁 10/30: 멈춘 티 안 나게)
        z = 1 + 0.035 * min(1, (t - TYPE - 0.6) / (LOOK - 0.6)) ** 0.8
        o = cv2.warpAffine(o, cv2.getRotationMatrix2D((W * 0.55, H * 0.4), 0, z), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', o, [cv2.IMWRITE_JPEG_QUALITY, 93])
typing = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/typing-norm.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(n / FPS * SR), np.float32); L = int(TYPE * SR); a[:L] = np.tile(typing, 3)[:L] * 0.25; a[L - 800:L] *= np.linspace(1, 0, 800)   # 10/30 혁: 키보드 너무 큼 (0.45 → 0.25)
step = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/heel-step.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
for i, t in enumerate(np.arange(0.35, IN1 + 0.01, 0.3)):
    j = int(t * SR); a[j:j + len(step)] += step[:len(a) - j] * (0.12 + 0.1 * i)
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s3-butter-back.mp4'], check=True)
print('ep02/s3-butter-back.mp4', round(n / FPS, 2), 's')
