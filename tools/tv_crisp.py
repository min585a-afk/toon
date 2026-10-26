"""2000년대 TV 방송 재질 — 선명하고 진한 색은 그대로, 화질만 그 시절처럼. 크레딧 0.
usage: python3 tv_crisp.py in.png out.jpg [세기 0~1, 기본 0.6]
바랜 색 · 검정 띄우기 없음(tv_look 과 다름). SD 해상도 · 색 번짐 · 그레인 · 약한 주사선 · 살짝 진한 채도/대비.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
k = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
rng = np.random.default_rng(3)
im = Image.open(src).convert('RGB')
H = 540; W = round(im.width * H / im.height)
sd = im.resize((W, H), Image.LANCZOS)
a = np.asarray(sd).astype(np.float32)
# 채도 · 대비 살짝 올림 (진한 TV 색)
g = a.mean(-1, keepdims=True); a = g + (a - g) * (1 + 0.15 * k)
a = (a - 128) * (1 + 0.08 * k) + 128
# 색 번짐: 색차만 가로로 흐림
r, gg, b = a[..., 0], a[..., 1], a[..., 2]
Y = 0.299*r + 0.587*gg + 0.114*b; Cb = b - Y; Cr = r - Y
n = max(1, int(5 * k)); ker = np.ones(n) / n
blur = lambda c: np.apply_along_axis(lambda row: np.convolve(row, ker, mode='same'), 1, c)
Cb = np.roll(blur(Cb), 1, 1); Cr = np.roll(blur(Cr), 1, 1)
r = Y + Cr; b = Y + Cb; gg = (Y - 0.299*r - 0.114*b) / 0.587
a = np.stack([r, gg, b], -1)
# 약한 주사선 + 그레인
a *= np.where((np.arange(H) % 2 == 0)[:, None, None], 1.0, 1 - 0.05 * k)
a += rng.normal(0, 5 * k, a.shape[:2])[..., None]
out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
out = out.resize((W * 2, H * 2), Image.BICUBIC).filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
out.save(dst, quality=92)
print(dst, out.size)
