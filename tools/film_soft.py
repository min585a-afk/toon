"""90년대 셀 애니 캡처 화질 — 부드럽게 뭉갠 선 · 고운 그레인 · 분홍 톤 (주사선 없음). 크레딧 0.
usage: python3 film_soft.py in.png out.jpg [세기 0~1, 기본 0.6]
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
k = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
rng = np.random.default_rng(5)
im = Image.open(src).convert('RGB')
W0, H0 = im.size
# SD 정도로 줄였다 키우기 + 살짝 흐림 (선이 부드럽게 뭉개짐)
h = int(720 - 240 * k); w = round(W0 * h / H0)
im = im.resize((w, h), Image.LANCZOS).resize((W0 // 2, H0 // 2), Image.BICUBIC)
im = im.filter(ImageFilter.GaussianBlur(0.8 * k))
a = np.asarray(im).astype(np.float32)
# 번짐(헐레이션): 밝은 곳이 살짝 퍼짐
glow = np.asarray(im.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
a = a + (np.maximum(glow, a) - a) * 0.25 * k
# 분홍 톤 · 검정 살짝 띄움
a = a * (1 - 0.06 * k) + np.array([255, 205, 215]) * 0.06 * k
# 고운 그레인
a += rng.normal(0, 6 * k, a.shape[:2])[..., None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(dst, quality=92)
print(dst)
