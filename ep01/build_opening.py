"""EP01 오프닝: 벽시계 9:59:57 클로즈업(째깍 → 10:00) → 컷 → 장면 1 타닥타닥 → 모니터로 → 장면 2 채팅 타자. 크레딧 0.
usage: python3 ep01/build_opening.py ep01/opening.mp4
"""
import math, os, subprocess, sys, tempfile, wave
import numpy as np
import cv2
sys.path.insert(0, 'tools')
import chat_screen as cs

FPS, OW, OH, SR = 24, 1080, 810, 44100
CLOCK = (517, 135, 118)  # 장면 1(2336x1744)에서 시계 가운데 · 반지름
img = cv2.imread('ep01/cut01-work-v9.png'); H, W = img.shape[:2]


def view(z):
    """z=0 시계 클로즈업 → z=1 전체."""
    cw0 = 520; cw = cw0 + (W - cw0) * z; ch = cw * 3 / 4
    cx = CLOCK[0] + (W / 2 - CLOCK[0]) * z; cy = CLOCK[1] + (H / 2 - CLOCK[1]) * z
    x0 = min(max(cx - cw / 2, 0), W - cw); y0 = min(max(cy - ch / 2, 0), H - ch)
    M = np.float32([[OW / cw, 0, -x0 * OW / cw], [0, OH / ch, -y0 * OH / ch]])
    return cv2.warpAffine(img2, M, (OW, OH), flags=cv2.INTER_AREA if z > 0.3 else cv2.INTER_CUBIC)


# 그림 속 시계 바늘을 지우고(인페인트) 직접 그림
_cx, _cy, _r = CLOCK
_hm = np.zeros((H, W), np.uint8); cv2.circle(_hm, (_cx, _cy), int(_r * 0.66), 255, -1)
_hm[_cy + 48:] = 0  # 아래 모니터 윗선은 건드리지 않음
_dark = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < 150
_hm = (_hm > 0) & _dark
_hm = cv2.dilate(_hm.astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
NOHANDS = cv2.inpaint(img, _hm, 6, cv2.INPAINT_TELEA)
INKC = (60, 45, 55)


def clock_at(hh, mm, ss):
    o = NOHANDS.copy(); cx, cy, r = CLOCK
    def hand(deg, length, width, col):
        a = math.radians(deg - 90)
        cv2.line(o, (cx, cy), (int(cx + math.cos(a) * length), int(cy + math.sin(a) * length)), col, width, cv2.LINE_AA)
    hand((hh % 12) * 30 + mm * 0.5, r * 0.45, 12, INKC)
    hand(mm * 6, r * 0.7, 8, INKC)
    hand(ss * 6, r * 0.78, 4, (60, 60, 220))
    cv2.circle(o, (cx, cy), 10, INKC, -1, cv2.LINE_AA); cv2.circle(o, (cx, cy), 5, (60, 60, 220), -1, cv2.LINE_AA)
    return o


frames, clicks, ticks = [], [], []
# 1) 시계 클로즈업 ~1.7초: 9:59:57 → 58 → 59 → 10:00 (분침 딸깍)
for k, (hh, mm, ss, n) in enumerate([(9, 59, 57, 10), (9, 59, 58, 10), (9, 59, 59, 10), (10, 0, 0, 12)]):
    ticks.append(len(frames)); img2 = clock_at(hh, mm, ss); fr = view(0.0)
    frames.extend([fr] * n)
# 2) 컷 → 장면 1 (그림 속 시계 그대로 10:00)
img2 = img
# 3) 장면 1 전체 1.2초 (타자 소리) → 모니터 쪽으로 빠르게 들어가며 채팅 화면으로
for f in range(40): frames.append(view(1.0))
MON = (390, 730)
for f in range(10):
    t = ((f - f % 2) / 9) ** 2; cw = W - (W - 900) * t; ch = cw * 3 / 4
    cx = W / 2 + (MON[0] - W / 2) * t; cy = H / 2 + (MON[1] - H / 2) * t
    x0 = min(max(cx - cw / 2, 0), W - cw); y0 = min(max(cy - ch / 2, 0), H - ch)
    M = np.float32([[OW / cw, 0, -x0 * OW / cw], [0, OH / ch, -y0 * OH / ch]])
    frames.append(cv2.warpAffine(img2, M, (OW, OH), flags=cv2.INTER_AREA))
type_start = 42 + 2
for f in range(type_start, len(frames), 3):
    if np.random.default_rng(f).random() < 0.8: clicks.append(f)
# 4) 장면 2 채팅 타자 (chat_screen 과 같은 타이밍) — 글자 하나마다 딸깍
def hold(im, k): frames.extend([im] * k)
def chat(shown, typing='', caret=True):
    o = cs.grain(cs.draw(shown, typing=typing, caret=caret), len(frames) // 3)
    return cv2.cvtColor(np.asarray(o.resize((OW, OH))), cv2.COLOR_RGB2BGR)
shown = cs.CHAT[:cs.TYPE_FROM]
hold(chat(shown), 12)
for item in cs.CHAT[cs.TYPE_FROM:]:
    for k in range(1, len(item[1]) + 1):
        if item[1][k - 1] != ' ': clicks.append(len(frames))
        hold(chat(shown, item[1][:k]), 3)
    hold(chat(shown, item[1]), 8)
    clicks.append(len(frames) - 4)  # 엔터
    shown = shown + [item]
    hold(chat(shown), 14)
hold(chat(shown, caret=False), 10)

# 소리: 째깍 · 타닥 (합성)
dur = len(frames) / FPS; audio = np.zeros(int(dur * SR) + SR, np.float32); rng = np.random.default_rng(7)
def add(at, snd):
    i = int(at / FPS * SR); audio[i:i + len(snd)] += snd[:len(audio) - i]
def click(loud=0.35):
    n = int(0.035 * SR); t = np.arange(n) / SR
    return (rng.normal(0, 1, n) * np.exp(-t * 180) * loud + np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 400) * loud * 0.4).astype(np.float32)
def tick():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 250) * 0.5).astype(np.float32)
for f in ticks: add(f, tick())
for f in clicks: add(f + rng.uniform(0, 1.5), click(rng.uniform(0.25, 0.45)))
audio = np.clip(audio, -1, 1)

tmp = tempfile.mkdtemp()
with wave.open(f'{tmp}/a.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((audio * 32767).astype(np.int16).tobytes())
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 92])
out = sys.argv[1] if len(sys.argv) > 1 else 'ep01/opening.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, round(dur, 1), 's')
