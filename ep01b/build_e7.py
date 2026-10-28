"""EP01 끝: 은서 타닥타닥(또각또각 멀어지며 사라짐) → 모니터 메모장 凸 연타 → 끝. 크레딧 0.
usage: python3 ep01b/build_e7.py  → ep01b/e7-gyul-type.mp4 · ep01b/e8-notepad.mp4
"""
import subprocess, tempfile, wave
import numpy as np
import cv2

FPS, W, H, SR = 24, 1080, 810, 44100
load = lambda p: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
typing, step = load('sfx/ep01/typing-norm.wav'), load('sfx/ep01/heel-step.wav')


def video(p):
    cap = cv2.VideoCapture(p); f = cap.get(cv2.CAP_PROP_FPS) or 24; out = []
    while True:
        ok, fr = cap.read()
        if not ok: return out, f
        out.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))


def write(frames, a, out):
    tmp = tempfile.mkdtemp()
    for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
    b = np.zeros(int(len(frames) / FPS * SR), np.float32); b[:min(len(b), len(a))] = a[:len(b)]
    with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(b, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
    print(out, round(len(frames) / FPS, 2), 's')


# 은서 타닥타닥 1.4초 + 또각또각 멀어짐 (점점 작게 → 사라짐)
SEC = 1.4; gv, gf = video('ep01b/video/c00-gyul-type-look-h3.mp4')
frames = [gv[min(len(gv) - 1, int((0.3 + (k - k % 2) / FPS) * gf))] for k in range(int(SEC * FPS))]
# 화난 얼굴(혁 10/28: 너무 평온) — 얼굴만 프레임마다 위치 맞춰 덮음 · 손은 H3 그대로
base = cv2.resize(cv2.imread('ep01b/e7-type-base.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
angry = cv2.resize(cv2.imread('ep01b/e7-type-angry.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
FX, FY = 540, 300; fm = np.zeros((H, W), np.float32); cv2.ellipse(fm, (FX, FY - 15), (150, 140), 0, 0, 360, 1, -1); fm = cv2.GaussianBlur(fm, (0, 0), 10)[..., None]
g = lambda im: cv2.cvtColor(im[FY - 160:FY + 160, FX - 200:FX + 200].astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
out = []
for fr in frames:
    (dx, dy), _ = cv2.phaseCorrelate(g(base), g(fr.astype(np.float32)))
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    a2 = cv2.warpAffine(angry, M, (W, H), borderMode=cv2.BORDER_REPLICATE); m2 = cv2.warpAffine(fm, M, (W, H))[..., None]
    out.append(np.clip(fr * (1 - m2) + a2 * m2, 0, 255).astype(np.uint8))
frames = out
a = np.tile(typing, 2)[:int(SEC * SR)] * 0.5
for i, t in enumerate([0.05, 0.45, 0.85]): j = int(t * SR); a[j:j + len(step)] += step[:len(a) - j] * (0.22 - i * 0.07)
write(frames, a, 'ep01b/e7-gyul-type.mp4')

# 메모장 凸 연타 (tools/notepad_screen.py → cel_look) + 빠른 타닥타닥 · 끝 멈춤
subprocess.run(['python3', 'tools/notepad_screen.py', 'ep01b/e8-notepad-raw.mp4'], check=True)
subprocess.run(['python3', 'tools/cel_look.py', 'ep01b/e8-notepad-raw.mp4', 'ep01b/e8-notepad-cel.mp4', '--ref', 'ep01b/c00-gyul-work.png', '--amount', '0.6'], check=True)
nv, _ = video('ep01b/e8-notepad-cel.mp4'); n = len(nv); type_end = n - 30
a = np.tile(typing, 6)[:int(n / FPS * SR)].copy() * 0.55; a[int(type_end / FPS * SR):] = 0
write(nv, a, 'ep01b/e8-notepad.mp4')
