"""EP01 컷 5: 팀장이 걸어가다 멈칫 → 갑자기 확 돌아봄(뒤통수 → 1장 번짐 → 돌아본 얼굴 + 안경 번쩍 + 휙!). 크레딧 0.
usage: python3 ep01b/build_c5.py ep01b/c5-boss-turn.mp4
그림: c5-boss-back.png(뒤통수) · c5-boss-turn.png(돌아봄)
"""
import subprocess, sys, tempfile, wave
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 810, 24, 44100
A = cv2.resize(cv2.imread('ep01b/c5-boss-back.png'), (W, H), interpolation=cv2.INTER_AREA)
B = cv2.resize(cv2.imread('ep01b/c5-boss-turn.png'), (W, H), interpolation=cv2.INTER_AREA)
HEAD = (545, 118)        # 머리 가운데 (1080x810)
GLASS = (553, 125)       # 안경 번쩍 자리
TURN, END = 16, 48       # 0.67초 뒤통수 → 확 → 2초


def sfx(fr, text, x, y, size, ang, t):
    sc = 1.35 if t < 2 else (1.1 if t < 4 else 1.0)
    f = ImageFont.truetype('tools/fonts/sfx-BlackHanSans.ttf', int(size * sc))
    im = Image.new('RGBA', (int(f.getlength(text)) + 60, int(size * sc * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((30, 10), text, font=f, fill=(255, 255, 255, 255), stroke_width=int(size * sc * 0.09), stroke_fill=(20, 15, 20, 255))
    a = np.asarray(im.rotate(ang, expand=True, resample=Image.BICUBIC)).astype(np.float32)
    h, w = a.shape[:2]; x0, y0 = int(x - w / 2), int(y - h / 2); al = a[..., 3:4] / 255
    fr[y0:y0 + h, x0:x0 + w] = (fr[y0:y0 + h, x0:x0 + w] * (1 - al) + a[..., 2::-1] * al).astype(np.uint8)
    return fr


def smear(t):
    """돌아보는 순간 1장: 머리 쪽만 가로로 번지고 속도선."""
    o = cv2.addWeighted(A, 0.5, B, 0.5, 0)
    k = np.zeros((1, 41), np.float32); k[0] = 1 / 41
    bl = cv2.filter2D(o, -1, k); m = np.zeros((H, W), np.float32)
    cv2.ellipse(m, HEAD, (90, 70), 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), 12)[..., None]
    o = (o * (1 - m) + bl * m).astype(np.uint8)
    rng = np.random.default_rng(t)
    for _ in range(9):  # 머리 옆 가로 속도선
        y = int(HEAD[1] + rng.uniform(-60, 60)); x = int(HEAD[0] + rng.uniform(40, 90))
        cv2.line(o, (x, y), (x + int(rng.uniform(60, 140)), y), (255, 255, 255), int(rng.uniform(2, 5)), cv2.LINE_AA)
    return o


def glint(fr, t):
    """안경 반짝: 십자 별 커졌다 작아짐."""
    s = [0.6, 1.0, 1.0, 0.8, 0.5, 0.3][t] if t < 6 else 0
    if s <= 0: return fr
    cx, cy = GLASS; L, w = int(46 * s), max(2, int(5 * s))
    for dx, dy in [(1, 0), (0, 1)]:
        pts = np.array([(cx - dx * L, cy - dy * L), (cx + dy * w, cy + dx * w), (cx + dx * L, cy + dy * L), (cx - dy * w, cy - dx * w)], np.int32)
        cv2.fillPoly(fr, [pts], (255, 255, 255), cv2.LINE_AA)
    cv2.circle(fr, (cx, cy), max(2, int(7 * s)), (255, 255, 255), -1, cv2.LINE_AA)
    return fr


frames = []
for f in range(END):
    if f < TURN: fr = A.copy()
    elif f < TURN + 2: fr = smear(f)
    else:
        t = f - TURN - 2; fr = B.copy()
        if t < 3:  # 확 도는 충격: 화면 살짝 흔들
            fr = cv2.warpAffine(fr, np.float32([[1, 0, [6, -5, 3][t]], [0, 1, [-4, 3, 0][t]]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        fr = glint(fr, t)
        fr = sfx(fr, '휙!', 760, 200, 110, 12, t)
    frames.append(fr)

# 소리: 휙(바람 가르는 노이즈) + 반짝(띵)
audio = np.zeros(int(END / FPS * SR) + SR, np.float32); rng = np.random.default_rng(5)
n = int(0.22 * SR); t = np.arange(n) / SR
whoosh = rng.normal(0, 1, n).astype(np.float32)
whoosh = np.convolve(whoosh, np.ones(12) / 12, 'same') * np.sin(np.pi * t / t[-1]) ** 2 * 0.9
i = int((TURN - 1) / FPS * SR); audio[i:i + n] += whoosh
n = int(0.5 * SR); t = np.arange(n) / SR
ting = (np.sin(2 * np.pi * 2600 * t) + 0.5 * np.sin(2 * np.pi * 3900 * t)) * np.exp(-t * 9) * 0.25
i = int((TURN + 2) / FPS * SR); audio[i:i + n] += ting
audio = np.clip(audio, -1, 1)

tmp = tempfile.mkdtemp()
with wave.open(f'{tmp}/a.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((audio * 32767).astype(np.int16).tobytes())
for k, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
out = sys.argv[1] if len(sys.argv) > 1 else 'ep01b/c5-boss-turn.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, round(END / FPS, 1), 's')
