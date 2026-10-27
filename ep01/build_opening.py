"""EP01 오프닝: 회사 입구(반투명 동글 실루엣 출근 인파) → 빌딩 위로 틸트 업 → 컷 → 장면 1 타닥타닥 → 컷 → 장면 2 채팅 타자 (줌 없음). 크레딧 0.
usage: python3 ep01/build_opening.py ep01/opening.mp4
"""
import math, os, subprocess, sys, tempfile, wave
import numpy as np
import cv2
sys.path.insert(0, 'tools')
import chat_screen as cs

FPS, OW, OH, SR = 24, 1080, 810, 44100
CLOCK = (517, 135, 118)  # 장면 1(2336x1744)에서 시계 가운데 · 반지름
img = cv2.imread('ep01/cut01-work-v9.png')            # 시계 클로즈업용 (바늘 다시 그림)
CUT1 = cv2.imread('ep01/cut01-work-v11.png')          # 장면 1 (나른한 하품)
H, W = img.shape[:2]


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
# 1) 회사 입구 2.2초: 반투명 동글 실루엣 사람들이 오가며 출근 (옛날 애니 엑스트라)
_t = cv2.imread('bg/office-building-tall.png'); TALL = cv2.resize(_t, (OW, int(_t.shape[0] * OW / _t.shape[1])), interpolation=cv2.INTER_AREA)
TOFF = TALL.shape[0] - OH  # 아래 화면(입구)이 시작하는 y
rng0 = np.random.default_rng(11)
MOB = []  # (시작 x, y(발), 크기, 속도 px/프레임, 색 톤)
for i in range(14):
    d = 1 if i % 2 == 0 else -1
    y = rng0.uniform(560, 760); sc = 1.0 + (y - 560) / 200 * 0.9
    MOB.append((rng0.uniform(-100, OW + 100), y, sc, d * rng0.uniform(5, 9) * sc, rng0.integers(0, 3)))
TONES = [(205, 170, 185), (190, 160, 175), (215, 185, 200)]  # BGR 라벤더 톤


def mob_frame(f, cam=None):
    """cam = 화면 위쪽 y (TOFF = 입구, 0 = 빌딩 꼭대기)."""
    cam = TOFF if cam is None else int(cam)
    base = TALL.copy(); lay = base.copy()
    for x0, y, sc, v, tone in sorted(MOB, key=lambda m: m[1]):
        x = (x0 + v * (f - f % 3)) % (OW + 240) - 120
        bob = 6 * sc * abs(math.sin((f - f % 3) * 0.55 + x0))
        hr, bw, bh = 26 * sc, 34 * sc, 92 * sc
        y = y + TOFF; cy = int(y - bh - bob); col = TONES[tone]
        cv2.ellipse(lay, (int(x), int(y)), (int(bw * 0.9), int(8 * sc)), 0, 0, 360, (120, 110, 140), -1, cv2.LINE_AA)  # 그림자
        cv2.rectangle(lay, (int(x - bw / 2), cy + int(bw / 2)), (int(x + bw / 2), int(y - bw / 2 - bob)), col, -1, cv2.LINE_AA)
        cv2.circle(lay, (int(x), cy + int(bw / 2)), int(bw / 2), col, -1, cv2.LINE_AA)
        cv2.circle(lay, (int(x), int(y - bw / 2 - bob)), int(bw / 2), col, -1, cv2.LINE_AA)
        cv2.circle(lay, (int(x), int(cy - hr * 0.9)), int(hr), col, -1, cv2.LINE_AA)
    return cv2.addWeighted(lay, 0.7, base, 0.3, 0)[cam:cam + OH]


# 입구 1.3초 → 빌딩 위로 틸트 업 1.4초(12fps 로 끊김, 천천히 출발·멈춤) → 꼭대기 0.4초
for f in range(31): frames.append(mob_frame(f))
for k in range(34):
    t = (k - k % 2) / 33; e = t * t * (3 - 2 * t)
    frames.append(mob_frame(31 + k, TOFF * (1 - e)))
for k in range(10): frames.append(mob_frame(65 + k, 0))
# 2) 컷 → 장면 1 (그림 속 시계 그대로 10:00)
img2 = CUT1
# 3) 장면 1 전체 (타자 소리) → 컷 → 채팅 화면 (줌 효과 없음, 혁 10/27)
for f in range(48): frames.append(view(1.0))  # 장면 1 = 2초
type_start = 75 + 10
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
hold(chat(shown, caret=False), 36)  # 마지막 메시지 1.5초 멈춤 (읽을 시간)

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
# 출근길 발소리 (가볍게)
for f in range(0, 60, 6): add(f + rng.uniform(0, 2), click(0.08 * (1 - f / 70)))
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
