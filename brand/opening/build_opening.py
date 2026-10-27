"""시리즈 공통 오프닝 (매 화 같은 영상) — 빌딩 아래쪽 → 위로 틸트 업 → 꼭대기에서 멈춤(제목 자리). 크레딧 0(H3 영상은 한 번만 만듦).
화 제목은 여기 그리지 않고 위에 얹음: python3 tools/title_card.py brand/opening/opening.mp4 out.mp4 "제목" "ENGLISH" --start TITLE_AT --dur 2.0
usage: python3 brand/opening/build_opening.py   → brand/opening/opening.mp4 (제목 시작 초를 출력)
"""
import subprocess, sys, tempfile, wave
import numpy as np
import cv2

FPS, OW, OH, SR = 24, 1080, 810, 44100
CROWD = 'brand/opening/entrance-crowd-h3.mp4'
cap = cv2.VideoCapture(CROWD); src_fps = cap.get(cv2.CAP_PROP_FPS) or 24; vf = []
while True:
    ok, fr = cap.read()
    if not ok: break
    vf.append(cv2.resize(fr, (OW, OH), interpolation=cv2.INTER_AREA))
_t = cv2.imread('bg/office-building-tall.png'); TALL = cv2.resize(_t, (OW, int(_t.shape[0] * OW / _t.shape[1])), interpolation=cv2.INTER_AREA)
TOFF = TALL.shape[0] - OH

frames = []
Y0 = int(TOFF * 0.55)                                                   # 빌딩 아래쪽(입구 지붕 걸침)에서 시작 (혁 10/27: 출근 인파 컷은 뺌)
for k in range(12): frames.append(TALL[Y0:Y0 + OH])                     # 0.5초 멈춤
for k in range(34):                                                     # 틸트 업 1.4초 (12fps, 천천히 출발·멈춤)
    t = (k - k % 2) / 33; e = t * t * (3 - 2 * t); y = int(Y0 * (1 - e)); frames.append(TALL[y:y + OH])
TITLE_AT = len(frames) / FPS
for k in range(48): frames.append(TALL[0:OH])                           # 꼭대기 2.0초 = 제목 자리

# 소리: 틸트 끝 '딩~' 만 (배경음은 이어붙일 때 brand/bgm/ 에서 깔음)
dur = len(frames) / FPS; au = np.zeros(int(dur * SR) + SR, np.float32); rng = np.random.default_rng(3)
def add(at, s): i = int(at * SR); au[i:i + len(s)] += s[:len(au) - i]
def tap(l):
    n = int(0.04 * SR); t = np.arange(n) / SR; return (rng.normal(0, 1, n) * np.exp(-t * 160) * l).astype(np.float32)
n = int(1.6 * SR); t = np.arange(n) / SR
add(TITLE_AT, ((np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 2.5) * 0.18).astype(np.float32))
au = np.clip(au, -1, 1)

tmp = tempfile.mkdtemp()
with wave.open(f'{tmp}/a.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((au * 32767).astype(np.int16).tobytes())
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
out = 'brand/opening/opening.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, round(dur, 1), 's · TITLE_AT', round(TITLE_AT, 2))
