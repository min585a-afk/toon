"""EP01 두 얼굴 인트로 — 회사 앞 출근 인파 → 빌딩 위로 틸트 업 → 제목 '두 얼굴' (TWO FACES) (해외 드라마 오프닝처럼) → 팀장 걸어옴. 크레딧 0.
usage: python3 ep01b/build_intro.py ep01b/intro.mp4
"""
import os, math, subprocess, sys, tempfile, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS, OW, OH, SR = 24, 1080, 810, 44100
_t = cv2.imread('bg/office-building-tall.png'); TALL = cv2.resize(_t, (OW, int(_t.shape[0] * OW / _t.shape[1])), interpolation=cv2.INTER_AREA)
TOFF = TALL.shape[0] - OH
rng0 = np.random.default_rng(11); MOB = []
for i in range(14):
    d = 1 if i % 2 == 0 else -1; y = rng0.uniform(560, 760); sc = 1.0 + (y - 560) / 200 * 0.9
    MOB.append((rng0.uniform(-100, OW + 100), y, sc, d * rng0.uniform(5, 9) * sc, rng0.integers(0, 3)))
TONES = [(205, 170, 185), (190, 160, 175), (215, 185, 200)]


def mob_frame(f, cam=TOFF):
    base = TALL.copy(); lay = base.copy()
    for x0, y, sc, v, tone in sorted(MOB, key=lambda m: m[1]):
        x = (x0 + v * (f - f % 3)) % (OW + 240) - 120; bob = 6 * sc * abs(math.sin((f - f % 3) * 0.55 + x0))
        hr, bw, bh = 26 * sc, 34 * sc, 92 * sc; y2 = y + TOFF; cy = int(y2 - bh - bob); col = TONES[tone]
        cv2.ellipse(lay, (int(x), int(y2)), (int(bw * 0.9), int(8 * sc)), 0, 0, 360, (120, 110, 140), -1, cv2.LINE_AA)
        cv2.rectangle(lay, (int(x - bw / 2), cy + int(bw / 2)), (int(x + bw / 2), int(y2 - bw / 2 - bob)), col, -1, cv2.LINE_AA)
        cv2.circle(lay, (int(x), cy + int(bw / 2)), int(bw / 2), col, -1, cv2.LINE_AA)
        cv2.circle(lay, (int(x), int(y2 - bw / 2 - bob)), int(bw / 2), col, -1, cv2.LINE_AA)
        cv2.circle(lay, (int(x), int(cy - hr * 0.9)), int(hr), col, -1, cv2.LINE_AA)
    return cv2.addWeighted(lay, 0.7, base, 0.3, 0)[int(cam):int(cam) + OH]


def title(fr, a):
    """제목 C: 나눔명조 흰 글씨 + 영어 부제. 얇은 테두리만 (그림자 없음, 혁 10/27). a=0~1 페이드."""
    im = Image.fromarray(fr[..., ::-1]).convert('RGBA')
    f1 = ImageFont.truetype('tools/fonts/title-NanumMyeongjo-800.ttf', 140); f2 = ImageFont.truetype('tools/fonts/ga1-800.ttf', 30)
    cx, cy = OW / 2, OH * 0.43
    def spaced(d, y, text, font, gap, **kw):
        ws = [d.textlength(c, font=font) for c in text]; x = cx - (sum(ws) + gap * (len(text) - 1)) / 2
        for c, w in zip(text, ws): d.text((x, y), c, font=font, anchor='lm', **kw); x += w + gap
    d = ImageDraw.Draw(im)
    spaced(d, cy, '두 얼굴', f1, 6, fill=(255, 255, 255, int(255 * a)), stroke_width=3, stroke_fill=(50, 30, 90, int(255 * a)))
    spaced(d, cy + 105, 'TWO  FACES', f2, 12, fill=(255, 238, 205, int(255 * a)), stroke_width=3, stroke_fill=(50, 30, 90, int(255 * a)))
    return np.asarray(im.convert('RGB'))[..., ::-1].copy()


frames = []
for f in range(31): frames.append(mob_frame(f))                         # 출근 인파 1.3초
for k in range(34):                                                     # 틸트 업 1.4초
    t = (k - k % 2) / 33; e = t * t * (3 - 2 * t); frames.append(mob_frame(31 + k, TOFF * (1 - e)))
top = mob_frame(65, 0)
for k in range(44):                                                     # 제목 1.8초 (0.9초 부드럽게 페이드 인)
    t = min(1, k / 22); frames.append(title(top, t * t * (3 - 2 * t)))
# 컷 → 팀장 걸어옴: H3 영상(ep01b/video/c0-boss-walk-h3.mp4)이 있으면 그걸 초당 8장으로 끊어서 3초, 없으면 정지 그림 1.6초
VID = 'ep01b/video/c0-boss-walk-h3.mp4'
if os.path.exists(VID):
    cap = cv2.VideoCapture(VID); vf = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        vf.append(cv2.resize(fr, (OW, OH), interpolation=cv2.INTER_AREA))
    step = len(vf) / (cap.get(cv2.CAP_PROP_FPS) or 24) * FPS / len(vf)  # 원본 fps → 24
    for k in range(72):  # 3초: 멀리서 가까이까지
        frames.append(vf[min(len(vf) - 1, int((k - k % 3) / step))])
else:
    W0 = cv2.imread('ep01b/c0-boss-walk.png')
    for k in range(38): frames.append(cv2.resize(W0, (OW, OH), interpolation=cv2.INTER_AREA))
# 소리: 출근 발소리 · 제목 '딩~' · 구두 또각또각
dur = len(frames) / FPS; au = np.zeros(int(dur * SR) + SR, np.float32); rng = np.random.default_rng(3)
def add(fr, s): i = int(fr / FPS * SR); au[i:i + len(s)] += s[:len(au) - i]
def tap(l):
    n = int(0.04 * SR); t = np.arange(n) / SR; return (rng.normal(0, 1, n) * np.exp(-t * 160) * l).astype(np.float32)
def chime():
    n = int(1.6 * SR); t = np.arange(n) / SR
    return (sum(np.sin(2 * np.pi * f * t) * a for f, a in [(880, .5), (1320, .3), (1760, .15)]) * np.exp(-t * 2.2) * 0.35).astype(np.float32)
def heel():
    n = int(0.06 * SR); t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 1800 * t) * 0.6 + rng.normal(0, 1, n) * 0.4) * np.exp(-t * 120) * 0.5).astype(np.float32)
for f in range(0, 60, 6): add(f + rng.uniform(0, 2), tap(0.08 * (1 - f / 70)))
add(65, chime())
for f in range(109, len(frames), 9): add(f, heel())
au = np.clip(au, -1, 1)
tmp = tempfile.mkdtemp()
with wave.open(f'{tmp}/a.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((au * 32767).astype(np.int16).tobytes())
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 92])
out = sys.argv[1] if len(sys.argv) > 1 else 'ep01b/intro.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, round(dur, 1), 's')
