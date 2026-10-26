"""눈만 키우기 · 눈동자 색 바꾸기 — 그림체 그대로, 크레딧 0.
usage: python3 eye_tweak.py in.png out.png 배율 "눈x,눈y,반경;..." [iris "x,y,r;..."] [hue 0~1, 기본 0.6 파랑]
"""
import sys, colorsys
import numpy as np
from PIL import Image
src, dst, s = sys.argv[1], sys.argv[2], float(sys.argv[3])
eyes = [tuple(map(float, e.split(','))) for e in sys.argv[4].split(';')]
irises = [tuple(map(float, e.split(','))) for e in sys.argv[5].split(';')] if len(sys.argv) > 5 else []
hue = float(sys.argv[6]) if len(sys.argv) > 6 else 0.6
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255
H, W = a.shape[:2]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# 1) 눈동자 색: 중간 밝기 · 색 있는 픽셀만 (흰자 · 선 · 피부 제외)
if irises:
    mx, mn = a.max(-1), a.min(-1)
    v = mx; sat = (mx - mn) / np.maximum(mx, 1e-6)
    m = np.zeros((H, W), np.float32)
    for x, y, r in irises:
        d = np.hypot(xx - x, yy - y) / r
        m = np.maximum(m, np.clip((1 - d) * 4, 0, 1))
    m *= np.clip((v - 0.12) * 6, 0, 1) * np.clip((0.93 - v) * 8, 0, 1) * np.clip((sat - 0.08) * 8, 0, 1)
    # 밝기는 그대로 두고 색만 파랑으로
    L = (a @ np.array([0.30, 0.59, 0.11], np.float32))[..., None]
    br, bg, bb = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
    blue = np.clip(L * np.array([br, bg, bb], np.float32) / (0.30*br + 0.59*bg + 0.11*bb), 0, 1)
    a = a * (1 - m[..., None]) + blue * m[..., None]
# 2) 눈 키우기: 가운데가 부풀고 가장자리는 그대로
mapx, mapy = xx.copy(), yy.copy()
for x, y, R in eyes:
    dx, dy = xx - x, yy - y
    t = np.clip(np.hypot(dx, dy) / R, 0, 1)
    f = 1 - (1 - 1 / s) * (1 - t**2) ** 2
    mapx = np.where(t < 1, x + dx * f, mapx); mapy = np.where(t < 1, y + dy * f, mapy)
# 양선형 보간
x0 = np.clip(np.floor(mapx).astype(int), 0, W - 2); y0 = np.clip(np.floor(mapy).astype(int), 0, H - 2)
fx = (mapx - x0)[..., None]; fy = (mapy - y0)[..., None]
out = (a[y0, x0] * (1-fx)*(1-fy) + a[y0, x0+1]*fx*(1-fy) + a[y0+1, x0]*(1-fx)*fy + a[y0+1, x0+1]*fx*fy)
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(dst)
print(dst)
