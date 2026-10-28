"""EP01 뒷부분 장면 1: 은서는 그대로 멈춰 있고, 뒤에서 꽃이 여러 군데 피어나며 퍼져 사무실 → 꽃밭으로 전환 + 금빛 반짝 (혁 10/28). 크레딧 0.
그림: e1-gyul-angel-papers.png(사무실, 시작) · e1-flowers-plate.png(꽃밭 배경만) · e1-gyul-cut2.png(은서만, 모니터 없이 온전)
usage: python3 ep01b/build_e1.py  → ep01b/e1-angel-bloom.mp4
"""
import math, subprocess, sys, tempfile
import numpy as np
import cv2
sys.path.insert(0, 'ep01b')

FPS, W, H = 24, 1080, 810
VOICE, V_AT = 'voice/ep01/c4-gyul-angel.wav', 0.15   # '그럴 리가요~!' (임시 목소리 · 바꾸면 입도 자동으로 맞음)
import subprocess as _sp
V_LEN = float(_sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VOICE], capture_output=True, text=True).stdout)
HOLD0, BLOOM, HOLD1 = V_AT + V_LEN + 0.15, 1.25, 1.1   # 사무실에서 대사 → 꽃                  # 사무실 멈춤 · 꽃 퍼지는 시간 · 꽃밭 멈춤
sz = lambda im: cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
office, plate = sz(cv2.imread('ep01b/e1-gyul-angel-papers.png')), sz(cv2.imread('ep01b/e1-flowers-plate.png'))
cut = cv2.resize(cv2.imread('ep01b/e1-gyul-cut2.png', cv2.IMREAD_UNCHANGED), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
girl, ga = cut[..., :3], cut[..., 3:4] / 255
# 꽃밭 색감 · 채도를 앞 장면(사무실 그림)에 맞춤 (혁 10/28: 우리 만화 필터 일관성)
def _match(im, ref, amt):
    a = cv2.cvtColor(np.clip(im, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32); r = cv2.cvtColor(ref.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    sm, ss, rm_, rs = a.reshape(-1, 3).mean(0), a.reshape(-1, 3).std(0) + 1e-6, r.reshape(-1, 3).mean(0), r.reshape(-1, 3).std(0)
    o = (a - sm) / ss * np.minimum(rs, ss) + rm_; o[..., 0] = a[..., 0] - sm[0] + (sm[0] * 0.6 + rm_[0] * 0.4); o = a * (1 - amt) + o * amt   # 대비는 안 올리고 밝기는 조금만
    return cv2.cvtColor(np.clip(o, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
plate = _match(plate, office, 0.45)
target = plate * (1 - ga) + girl * ga                  # 꽃밭 + 은서 (모니터 없음)
# 입: 다문 웃음(편집본) ↔ 벌린 웃음(원본), 목소리 크기대로 초당 8번
_o = cv2.imread('ep01b/e1-gyul-angel-papers.png'); _c = cv2.resize(cv2.imread('ep01b/talk/e1-smile-closed-raw.png'), (_o.shape[1], _o.shape[0]))
MX, MY = 1123, 735; _g = lambda im: cv2.cvtColor(im[MY - 150:MY + 150, MX - 200:MX + 200], cv2.COLOR_BGR2GRAY).astype(np.float32)
(_dx, _dy), _ = cv2.phaseCorrelate(_g(_o), _g(_c)); _c = cv2.warpAffine(_c, np.float32([[1, 0, -_dx], [0, 1, -_dy]]), (_o.shape[1], _o.shape[0]), borderMode=cv2.BORDER_REPLICATE)
_m = np.zeros(_o.shape[:2], np.float32); cv2.ellipse(_m, (MX, MY + 15), (115, 115), 0, 0, 360, 1, -1); _m = cv2.GaussianBlur(_m, (0, 0), 9)[..., None]   # 벌린 입 끝까지 덮음
office_closed = sz((_o * (1 - _m) + _c * _m).astype(np.uint8))
# 중간 입: 원본 벌린 입을 세로로 눌러서(같은 그림체) 35% · 65% → 다문 입 → 조금 → 반 → 활짝 4단계 (혁 10/28)
def squash(k):
    o = _o.astype(np.float32); c0 = (_o * (1 - _m) + _c * _m).astype(np.uint8)
    rm = np.zeros(c0.shape[:2], np.uint8); cv2.ellipse(rm, (MX, MY), (70, 40), 0, 0, 360, 255, -1)
    rm = ((rm > 0) & (cv2.cvtColor(c0, cv2.COLOR_BGR2GRAY) < 110)).astype(np.uint8) * 255; rm = cv2.dilate(rm, np.ones((9, 9), np.uint8))   # 웃는 입 선만
    c = cv2.inpaint(c0, rm, 7, cv2.INPAINT_TELEA).astype(np.float32)       # 다문 입 선 지우고 피부로
    x0, x1, y0, y1 = MX - 78, MX + 78, 726, 824                              # 벌린 입만 딱 (위 피부 X)
    patch = o[y0:y1, x0:x1]; hh = int((y1 - y0) * k)
    sq = cv2.resize(patch, (x1 - x0, max(2, hh)), interpolation=cv2.INTER_AREA)
    top = int(748 - k * (748 - y0))                                           # 윗입술: 다문 입 선(748)에서 아주 조금만 올라감 · 아래로 벌어짐
    mm = np.zeros(o.shape[:2], np.float32); cv2.ellipse(mm, (MX, top + hh // 2), (74, max(6, hh // 2 + 4)), 0, 0, 360, 1, -1); mm = cv2.GaussianBlur(mm, (0, 0), 2)[..., None]
    lay = c.copy(); lay[top:top + hh, x0:x1] = sq
    return sz((c * (1 - mm) + lay * mm).astype(np.uint8))
office_s, office_h = squash(0.35), squash(0.65)
MOUTHS = [office_closed, office_s, office_h, office]
_raw = _sp.run(['ffmpeg', '-v', 'error', '-i', VOICE, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
_x = np.frombuffer(_raw, np.float32); _rms = np.array([np.sqrt(np.mean(_x[i:i + 2000] ** 2)) for i in range(0, len(_x), 2000)]); _top = _rms.max() + 1e-9
_lv = [0 if r / _top < 0.12 else 1 if r / _top < 0.35 else 2 if r / _top < 0.65 else 3 for r in _rms]
for i in range(1, len(_lv)):                                   # 한 번에 두 단계 이상 안 뜀
    if abs(_lv[i] - _lv[i - 1]) > 1: _lv[i] = _lv[i - 1] + (1 if _lv[i] > _lv[i - 1] else -1)
def office_at(t):
    j = int((t - V_AT) * 8)
    if j < 0 or j >= len(_lv): return office_closed
    return MOUTHS[_lv[j]]
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
    if t < 0: o = office_at(kk / FPS).copy()
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
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE, '-filter_complex', f'[1:a]adelay={int(V_AT * 1000)}:all=1,apad[a]',
                '-map', '0:v', '-map', '[a]', '-t', str(n / FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/e1-angel-bloom.mp4'], check=True)
print('ep01b/e1-angel-bloom.mp4', round(n / FPS, 2), 's')
