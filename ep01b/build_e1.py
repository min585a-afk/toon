"""EP01 뒷부분 장면 1: 은서는 그대로 멈춰 있고, 뒤에서 꽃이 여러 군데 피어나며 퍼져 사무실 → 꽃밭으로 전환 + 금빛 반짝 (혁 10/28). 크레딧 0.
그림: e1-gyul-angel-papers.png(사무실, 시작) · e1-flowers-plate.png(꽃밭 배경만) · e1-gyul-cut2.png(은서만, 모니터 없이 온전)
usage: python3 ep01b/build_e1.py  → ep01b/e1-angel-bloom.mp4
"""
import math, subprocess, sys, tempfile
import numpy as np
import cv2
sys.path.insert(0, 'ep01b')

FPS, W, H = 24, 1080, 810
HOLD0, BLOOM, HOLD1 = 0.4, 1.25, 1.1                   # 사무실 멈춤 · 꽃 퍼지는 시간 · 꽃밭 멈춤
sz = lambda im: cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
office, plate = sz(cv2.imread('ep01b/e1-gyul-angel-papers.png')), sz(cv2.imread('ep01b/e1-flowers-plate.png'))
cut = cv2.resize(cv2.imread('ep01b/e1-gyul-cut2.png', cv2.IMREAD_UNCHANGED), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
girl, ga = cut[..., :3], cut[..., 3:4] / 255
target = plate * (1 - ga) + girl * ga                  # 꽃밭 + 은서 (모니터 없음)
ga1 = cv2.resize(cv2.imread('ep01b/e1-gyul-cut.png', cv2.IMREAD_UNCHANGED), (W, H), interpolation=cv2.INTER_AREA)[..., 3:4].astype(np.float32) / 255  # 사무실 장면에서 보이는 은서(모니터에 가린 채)

# 꽃 피어나는 자리 (은서 뒤 · 둘레), 순서대로 터짐 (초)
SEEDS = [(430, 260, 0.00), (650, 250, 0.08), (300, 470, 0.18), (790, 470, 0.25), (170, 200, 0.33), (930, 180, 0.38),
         (120, 600, 0.45), (960, 640, 0.50), (520, 80, 0.55), (250, 760, 0.62), (820, 770, 0.66), (60, 380, 0.70), (1030, 380, 0.74)]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(5); ang = np.arctan2


def bloom_mask(t):
    """t초: 자리마다 꽃잎 모양(5갈래로 울퉁불퉁)으로 커지는 원 → 합치면 화면 전체."""
    m = np.zeros((H, W), np.float32)
    for x, y, st in SEEDS:
        r = (t - st) / (BLOOM - st + 1e-6)
        if r <= 0: continue
        R = 40 + r ** 1.3 * 900
        th = np.arctan2(yy - y, xx - x); d = np.hypot(xx - x, yy - y)
        edge = R * (1 + 0.12 * np.cos(5 * th + x))         # 꽃잎 모양 가장자리
        m = np.maximum(m, np.clip((edge - d) / 18, 0, 1))
    return m[..., None]


def star(o, x, y, L):
    if L < 3: return o
    lay = np.zeros((H, W), np.float32); w = max(2, L // 6)
    for (dx, dy), ln in [((1, 0), L * 0.7), ((0, 1), L)]:
        p = np.array([(x - dx * ln, y - dy * ln), (x + dy * w, y + dx * w), (x + dx * ln, y + dy * ln), (x - dy * w, y - dx * w)], np.int32)
        cv2.fillPoly(lay, [p], 1.0, cv2.LINE_AA)
    g = np.clip(cv2.GaussianBlur(lay, (0, 0), L * 0.35) * 2.2, 0, 1)[..., None]; c = lay[..., None]
    o = o + g * np.array([90, 190, 255], np.float32) * 0.8
    return o * (1 - c) + 255 * c


def flash(o, x, y, s):
    """꽃 터지는 자리 순간 반짝 (흰 빛)."""
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * s * s))[..., None]
    return o + 255 * g * 0.28


STARS = [(200, 140, 44, 0), (880, 120, 40, 1), (140, 520, 34, 2), (960, 560, 42, 0), (560, 60, 30, 1), (330, 700, 32, 2), (800, 690, 36, 1)]
tmp = tempfile.mkdtemp(); n = int((HOLD0 + BLOOM + HOLD1) * FPS)
for k in range(n):
    kk = k - k % 2; t = kk / FPS - HOLD0                 # 12fps
    if t < 0: o = office.copy()
    else:
        m = bloom_mask(min(t, BLOOM)); o = office * (1 - m) + target * m
        for x, y, st in SEEDS:                           # 터지는 순간 반짝
            dt = t - st
            if 0 <= dt < 0.17: o = flash(o, x, y, 60 + dt * 300)
        a = np.maximum(ga1, ga * m)                       # 모니터 뒤 가려진 부분은 꽃이 닿을 때 드러남
        o = o * (1 - a) + girl * a                       # 은서는 그대로 멈춰 있음
    if t > BLOOM * 0.6:                                  # 꽃밭 되면 금빛 별 깜빡
        for x, y, L, ph in STARS:
            s = [1.0, 0.55, 0.2][((kk // 2) + ph) % 3]; o = star(o, x, y, int(L * s))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(o, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep01b/e1-angel-bloom.mp4'], check=True)
print('ep01b/e1-angel-bloom.mp4', round(n / FPS, 2), 's')
