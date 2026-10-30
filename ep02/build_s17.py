"""EP02 장면 17: 최버터 굳음 — H3 영상(눈 흰 점 된 뒤부터, ep02/video/s17-butter-frozen-h3.mp4) + 90년대 애니 우울 효과(파랗게 가라앉음 · 위에서 세로 그늘 줄 '쭈욱') + 뿌우우~ 소리. 크레딧 0.
usage: python3 ep02/build_s17.py → ep02/s17-butter-frozen.mp4
"""
import subprocess, tempfile, wave
import numpy as np, cv2
FPS, W, H, SR = 24, 1080, 810, 44100
V0, SEC = 2.55, 2.6                                             # 혁 10/29: 눈 흰 점 되기 전은 빼고 바로
cap = cv2.VideoCapture('ep02/video/s17-butter-frozen-h3.mp4'); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32))
rng = np.random.default_rng(3); xs = np.sort(rng.uniform(0.08, 0.92, 22)) * W; ws = rng.uniform(5, 13, 22); ls = rng.uniform(0.25, 0.55, 22)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
tmp = tempfile.mkdtemp(); n = int(SEC * FPS)
for k in range(n):
    t = (k - k % 2) / FPS; p = min(1.0, t / 0.5)                  # 0.5초 동안 가라앉음
    fr = v[min(len(v) - 1, int((V0 + t) * vf))].copy()
    g = fr.mean(2, keepdims=True); fr = fr * (1 - 0.45 * p) + g * 0.45 * p           # 색 빠짐
    fr = fr * (1 - 0.22 * p) + np.float32([120, 60, 40]) * 0.22 * p                    # 푸르스름하게 (BGR)
    lines = np.zeros((H, W), np.float32)
    for x, w, L in zip(xs, ws, ls):                                                    # 위에서 내려오는 세로 그늘 줄
        Ly = H * L * min(1.0, t / 0.6)
        m = (np.abs(xx - x) < w) & (yy < Ly); lines[m] = np.maximum(lines[m], (1 - yy[m] / max(Ly, 1)) ** 0.7)
    lines = cv2.GaussianBlur(lines, (0, 0), 1.2)[..., None]
    fr = fr * (1 - 0.55 * lines) + np.float32([70, 30, 40]) * 0.55 * lines             # 보랏빛 어두운 줄
    vig = np.clip(np.hypot((xx - W / 2) / (W * 0.6), (yy - H / 2) / (H * 0.6)), 0, 1)[..., None] ** 2
    fr = fr * (1 - 0.35 * p * vig)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(fr, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
gl = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/anime/gloom-syn.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(SEC * SR), np.float32); a[:min(len(a), len(gl))] += gl[:len(a)] * 0.7
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s17-butter-frozen.mp4'], check=True)
print('ep02/s17-butter-frozen.mp4', SEC, 's')

import shutil; shutil.rmtree(tmp, ignore_errors=True)   # 임시 프레임 지움 (10/30 디스크 꽉 참)
