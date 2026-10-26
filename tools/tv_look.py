"""옛날 투니버스(SD 방송 · VHS) 재질 후처리. 크레딧 0.
usage: python3 tv_look.py in.png out.png [strength 0~1, 기본 1] [선 진하기 0~1, 기본 0.7]
배경은 뭉개고, 캐릭터 테두리(어두운 선)만 원본에서 다시 얹어 또렷하게 — 꿈별 · oldku_ku 채널 재질.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
line_k = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
rng = np.random.default_rng(7)

im = Image.open(src).convert('RGB')
orig = im
W, H = im.size
# 1) SD 해상도로 내렸다 올림 — 480줄 방송 화질
sd_h = 480
sd_w = round(W * sd_h / H)
im = im.resize((sd_w, sd_h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.6 * k))
a = np.asarray(im).astype(np.float32)

# 2) 색 번짐 — YIQ 로 바꿔 색 신호만 가로로 흐리고 살짝 밀기
r, g, b = a[..., 0], a[..., 1], a[..., 2]
Y = 0.299 * r + 0.587 * g + 0.114 * b
I = 0.596 * r - 0.274 * g - 0.322 * b
Q = 0.211 * r - 0.523 * g + 0.312 * b
def hblur(c, n):
    ker = np.ones(n) / n
    return np.apply_along_axis(lambda row: np.convolve(row, ker, mode='same'), 1, c)
n = max(1, int(7 * k))
I = np.roll(hblur(I, n), int(2 * k), axis=1)
Q = np.roll(hblur(Q, n), int(2 * k), axis=1)

# 3) 바랜 색 — 채도 살짝 빼고 검정을 들어 올림(필름/브라운관), 따뜻하게
I *= 1 - 0.12 * k
Q *= 1 - 0.12 * k
Y = Y * (1 - 0.08 * k) + 14 * k
r = Y + 0.956 * I + 0.621 * Q
g = Y - 0.272 * I - 0.647 * Q
b = Y - 1.106 * I + 1.703 * Q
a = np.stack([r + 4 * k, g + 1 * k, b - 4 * k], -1)

# 4) 주사선 · 그레인 · 미세 가로 흔들림
lines = (np.arange(sd_h) % 2 == 0)[:, None, None]
a = a * np.where(lines, 1.0, 1 - 0.07 * k)
a += rng.normal(0, 4.0 * k, a.shape[:2])[..., None]
for y in range(sd_h):
    s = int(round(np.sin(y / 23.0) * 0.8 * k))
    if s:
        a[y] = np.roll(a[y], s, axis=0)

# 5) 가장자리 살짝 어둡게(브라운관)
yy, xx = np.mgrid[0:sd_h, 0:sd_w]
d = ((xx - sd_w / 2) / (sd_w / 2)) ** 2 + ((yy - sd_h / 2) / (sd_h / 2)) ** 2
a *= (1 - 0.10 * k * np.clip(d, 0, 1))[..., None]

out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
# 밀린 가장자리 몇 픽셀 잘라냄(색 번짐 · 흔들림이 반대편으로 넘어온 줄)
out = out.crop((4, 0, sd_w - 4, sd_h))
sd_w -= 8
# 원래 크기로 부드럽게 다시 키움 — 업스케일된 옛날 방송 캡처 느낌
out = out.resize((round(sd_w * 2), sd_h * 2), Image.BICUBIC)

# 6) 테두리 다시 얹기 — 원본을 같은 크기로 줄여 어두운 선만 골라 진한 갈색으로 덮음
if line_k > 0:
    ow, oh = out.size
    scale = oh / (sd_h)
    crop_px = round(4 * orig.width / (sd_w + 8))
    o = orig.crop((crop_px, 0, orig.width - crop_px, orig.height)).resize((ow, oh), Image.LANCZOS)
    o = o.filter(ImageFilter.GaussianBlur(0.4))
    L = np.asarray(o.convert('L')).astype(np.float32)
    m = np.clip((95 - L) / 45, 0, 1) * line_k
    ink = np.array([38, 24, 26], np.float32)
    b2 = np.asarray(out).astype(np.float32)
    b2 = b2 * (1 - m[..., None]) + ink * m[..., None]
    b2 += rng.normal(0, 2.0 * k, b2.shape[:2])[..., None]
    out = Image.fromarray(np.clip(b2, 0, 255).astype(np.uint8))
out.save(dst, quality=88)
print(dst, out.size)
