"""EP01 뒷부분 장면 '은서 분노': 장면 1 과 같은 구도(모니터 뒤 · 서류 쥠) — 정색 그림자 · 이 악물기 · 핏대 · 서류 구김 (e3-gyul-rage.png)
+ 뒤에서 만화식 불꽃이 확 솟아 일렁임(인물 뒤로만) · 빨간 깜빡 · 부들부들 떨림 · 빠직 손글씨. 크레딧 0.
usage: python3 ep01b/build_e3.py  → ep01b/e3-gyul-rage.mp4
"""
import subprocess, sys, tempfile
import numpy as np
import cv2

FPS, W, H, SEC = 24, 1080, 810, 1.8
img = cv2.resize(cv2.imread('ep01b/e3-gyul-rage.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
bgc = np.median(img[:60, -300:].reshape(-1, 3), 0)                                       # 평평한 진빨강 배경색
fg = (np.abs(img - bgc).sum(2) > 60).astype(np.uint8)
n_, lab, st, _ = cv2.connectedComponentsWithStats(fg); fg = np.isin(lab, 1 + np.argsort(st[1:, 4])[-2:]).astype(np.uint8)   # 은서 + 모니터
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
ff = fg * 255; mk = np.zeros((H + 2, W + 2), np.uint8); cv2.floodFill(ff, mk, (W - 5, 5), 128); fg = (ff != 128).astype(np.float32)
fg = cv2.GaussianBlur(fg, (0, 0), 1.2)[..., None]
COLS = [(40, 40, 200), (30, 120, 245), (90, 210, 255)]                                    # 빨강 · 주황 · 노랑 (셀 단색 3겹)


def flames(t, seed, rise):
    lay = np.zeros((H, W, 3), np.float32); a = np.zeros((H, W), np.float32); rng = np.random.default_rng(seed)
    for li, (col, base, amp) in enumerate(zip(COLS, [H * 0.2, H * 0.38, H * 0.55], [H * 0.6, H * 0.45, H * 0.3])):
        pts = [(0, H)]
        for x in range(0, W + 60, 60):
            h = (base + amp * (0.55 + 0.45 * np.sin(x * 0.021 + t * 9 + li * 2)) * rng.uniform(0.75, 1.15)) * rise
            pts += [(x - 30, H - h * 0.55), (x, H - h)]
        pts += [(W, H)]; p = np.array(pts, np.int32)
        cv2.fillPoly(lay, [p], col); cv2.fillPoly(a, [p], 1.0); cv2.polylines(lay, [p], True, (20, 10, 30), 3, cv2.LINE_AA)
    return lay, cv2.GaussianBlur(a, (0, 0), 1.2)[..., None]


sys.path.insert(0, 'tools')
spr = cv2.imread('brand/sfx/ppajik.png', cv2.IMREAD_UNCHANGED).astype(np.float32)
# 우리 만화 필터에 맞춤 (혁 10/28): 순백 → 그림 속 흰색(살짝 따뜻하고 바랜) · 검정 → 그림 선색 · 선 살짝 뭉개짐
_rgb = spr[..., :3]; _lum = _rgb.mean(2, keepdims=True) / 255
_rgb = _lum * np.array([228, 234, 240], np.float32) + (1 - _lum) * np.array([38, 24, 34], np.float32)   # BGR: 바랜 흰색 · 그림 선색(진한 남보라)
spr = np.dstack([cv2.GaussianBlur(_rgb, (0, 0), 1.6), cv2.GaussianBlur(spr[..., 3], (0, 0), 1.6)])
def ppajik(fr, x, y, hgt, t):
    if t < 0: return fr
    sc = 1.3 if t < 2 else (1.08 if t < 4 else 1.0); r = hgt * sc / spr.shape[0]
    im = cv2.resize(spr, (int(spr.shape[1] * r), int(spr.shape[0] * r)), interpolation=cv2.INTER_AREA).astype(np.float32)
    im[..., :3] += np.random.default_rng(t).normal(0, 6, im.shape[:2])[..., None]   # 그레인
    h, w = im.shape[:2]; x0, y0 = int(x - w / 2), int(y - h / 2); x1, y1, x2, y2 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    a = im[y1 - y0:y2 - y0, x1 - x0:x2 - x0]; al = a[..., 3:4] / 255
    fr[y1:y2, x1:x2] = fr[y1:y2, x1:x2] * (1 - al) + a[..., :3] * al; return fr


# H3 영상 (혁 10/28: 영상으로 자연스럽게): 웃음 → 그림자 → 불꽃 → 이 악물기. 불꽃 꺼지기 전까지만 · 1.25배 · 12fps + 빠직
V, V0, V1, SPD = 'ep01b/video/e3-rage-h3.mp4', 0.3, 3.7, 1.7   # 불타오르는 템포 빠르게 (혁 10/28)
cap = cv2.VideoCapture(V); vf = cap.get(cv2.CAP_PROP_FPS) or 24; vv = []
while True:
    ok, fr = cap.read()
    if not ok: break
    vv.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32))
# 혁 10/28: 불타오르기 전 그림자 멈춤이 길어서 가운데(1.1~2.1초)를 건너뜀 → 1.4초
CUT_A, CUT_B = 1.1, 2.1
src_t = lambda t: V0 + t * SPD if V0 + t * SPD < CUT_A else CUT_B + (V0 + t * SPD - CUT_A)
n = int(((CUT_A - V0) + (V1 - CUT_B)) / SPD * FPS); PPAJIK_AT = int(((CUT_A - V0) + (2.45 - CUT_B)) / SPD * FPS)
tmp = tempfile.mkdtemp()
for f in range(n):
    k = f - f % 2; fr = vv[min(len(vv) - 1, int(src_t(k / FPS) * vf))].copy()
    if f >= PPAJIK_AT:
        sx, sy = np.random.default_rng(k).normal(0, 3, 2)
        fr = cv2.warpAffine(fr, np.float32([[1, 0, sx], [0, 1, sy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)   # 부들부들
        fr = ppajik(fr, int(W * 0.8), int(H * 0.3), int(H * 0.36), f - PPAJIK_AT)
    cv2.imwrite(f'{tmp}/{f:05d}.jpg', np.clip(fr, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep01b/e3-gyul-rage.mp4'], check=True)
print('ep01b/e3-gyul-rage.mp4', round(n / FPS, 2), 's')
