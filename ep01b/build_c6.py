"""EP01 컷 6 (컷 2 에도 재사용): 0.1초 만에 천사 미소 — 흰 번쩍 1장 → 꽃이 하나씩 피어나며(빙글 커졌다 제자리) 반짝반짝
+ 금빛 반짝 + 꽃마다 한 음씩 올라가는 종소리. 크레딧 0.  그림: char/gyul/exp/01-angel-clean.png (꽃·반짝이 뺀 판)
usage: python3 ep01b/build_c6.py ep01b/c6-angel.mp4 [초]
"""
import math, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, 'tools'); import sfx_sound as ss

W, H, FPS = 1080, 810, 24
IMG = cv2.resize(cv2.imread('char/gyul/exp/01-angel-clean.png'), (W, H), interpolation=cv2.INTER_AREA)
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 1.6
# 꽃 (x, y, 반지름, 피는 프레임) — 얼굴 피해서 머리 둘레, 안쪽부터 바깥으로 차례로
FLOWERS = [(150, 275, 44, 2), (920, 350, 46, 4), (225, 545, 40, 6), (975, 210, 34, 8), (80, 400, 30, 10), (900, 620, 40, 12), (150, 630, 34, 14), (1040, 455, 26, 16)]
STARS = [(240, 165, 60, 0), (870, 175, 52, 1), (190, 455, 46, 2), (1005, 560, 56, 0), (320, 75, 38, 1), (820, 495, 42, 2), (60, 560, 38, 1), (990, 90, 38, 0)]
PINK, PINK2, INK, CORE = (215, 190, 255), (180, 140, 245), (120, 70, 170), (90, 200, 255)


def flower(fr, x, y, r, rot):
    if r < 3: return
    for i in range(5):  # 꽃잎 5장 (끝이 살짝 파인 벚꽃)
        a = rot + i * 2 * math.pi / 5; px, py = x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55
        cv2.ellipse(fr, (int(px), int(py)), (int(r * 0.55), int(r * 0.38)), math.degrees(a), 0, 360, PINK, -1, cv2.LINE_AA)
        cv2.ellipse(fr, (int(px), int(py)), (int(r * 0.55), int(r * 0.38)), math.degrees(a), 0, 360, INK, max(1, r // 18), cv2.LINE_AA)
    for i in range(5):  # 꽃잎 안쪽 진한 분홍
        a = rot + i * 2 * math.pi / 5
        cv2.ellipse(fr, (int(x + math.cos(a) * r * 0.32), int(y + math.sin(a) * r * 0.32)), (int(r * 0.22), int(r * 0.14)), math.degrees(a), 0, 360, PINK2, -1, cv2.LINE_AA)
    cv2.circle(fr, (int(x), int(y)), max(2, int(r * 0.16)), CORE, -1, cv2.LINE_AA)


def star(fr, x, y, L):
    """레퍼런스 같은 반짝: 세로로 긴 4갈래 별 + 따뜻한 금빛 번짐(글로우) + 흰 중심."""
    if L < 3: return
    lay = np.zeros(fr.shape[:2], np.float32); w = max(2, L // 6)
    for (dx, dy), ln in [((1, 0), L * 0.7), ((0, 1), L)]:  # 가로 짧게 · 세로 길게
        p = np.array([(x - dx * ln, y - dy * ln), (x + dy * w, y + dx * w), (x + dx * ln, y + dy * ln), (x - dy * w, y - dx * w)], np.int32)
        cv2.fillPoly(lay, [p], 1.0, cv2.LINE_AA)
    cv2.circle(lay, (x, y), max(2, L // 5), 1.0, -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(lay, (0, 0), L * 0.35) * 2.2 + cv2.GaussianBlur(lay, (0, 0), L * 0.1)
    g = np.clip(glow, 0, 1)[..., None]; c = np.clip(lay, 0, 1)[..., None]
    o = fr.astype(np.float32)
    o = o + g * np.array([90, 190, 255], np.float32) * 0.9      # 금빛 (BGR)
    o = o * (1 - c) + 255 * c                                   # 흰 중심
    fr[:] = np.clip(o, 0, 255).astype(np.uint8)


def sfx(fr, text, x, y, size, ang, t):
    sc = 1.35 if t < 2 else (1.1 if t < 4 else 1.0)
    f = ImageFont.truetype('tools/fonts/sfx-BlackHanSans.ttf', int(size * sc))
    im = Image.new('RGBA', (int(f.getlength(text)) + 60, int(size * sc * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((30, 10), text, font=f, fill=(255, 255, 255, 255), stroke_width=int(size * sc * 0.09), stroke_fill=(20, 15, 20, 255))
    a = np.asarray(im.rotate(ang, expand=True, resample=Image.BICUBIC)).astype(np.float32)
    h, w = a.shape[:2]; x0, y0 = int(x - w / 2), int(y - h / 2); al = a[..., 3:4] / 255
    fr[y0:y0 + h, x0:x0 + w] = (fr[y0:y0 + h, x0:x0 + w] * (1 - al) + a[..., 2::-1] * al).astype(np.uint8)
    return fr


BLOOM = [0.0, 0.35, 0.7, 1.15, 1.0]  # 피는 크기 (12fps 로 한 단계씩)
tmp = tempfile.mkdtemp(); n = int(secs * FPS)
for f in range(n):
    if f == 0: fr = np.full_like(IMG, 255)                      # 흰 번쩍 1장 (확 바뀜)
    else:
        fr = IMG.copy(); k = f - f % 2                          # 12fps
        for x, y, r, st in FLOWERS:
            s = (k - st) // 2
            if s < 0: continue
            sc = BLOOM[min(s, len(BLOOM) - 1)]
            flower(fr, x, y, int(r * sc), 0.5 * max(0, 4 - s) + x * 0.01)   # 빙글 돌며 피고 멈춤
            if s == 2 or s == 3: star(fr, x + int(r * 0.9), y - int(r * 0.9), int(r * 0.7))  # 필 때 반짝
        for x, y, L, ph in STARS:
            s = [1.0, 0.6, 0.25][((f - 1) // 3 + ph) % 3]
            star(fr, x, y, int(L * s))
    cv2.imwrite(f'{tmp}/{f:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
ss.save(f'{tmp}/a.wav', ss.mix([(0, ss.bloom([(st + 4) / FPS for *_, st in FLOWERS]))], secs))
out = sys.argv[1] if len(sys.argv) > 1 else 'ep01b/c6-angel.mp4'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, secs, 's')
