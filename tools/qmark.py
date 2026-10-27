"""만화 '?' — brand/sfx/qmark.png (손그림 입체 노랑 물음표) 를 툭 띄우고 살짝 기울임. 크레딧 0.
qmark(fr, x, y, size, t) : t=뜬 뒤 프레임 수 → 툭 커졌다 제자리 + 각도가 살짝 기울어짐.
usage(시험): python3 tools/qmark.py out.png
"""
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

_cache = {}


def sprite(size):
    """혁 고른 물음표(10/27): 손그림 셀 느낌 입체 '?' (GPT 그림, 노랑으로 색 바꿈) = brand/sfx/qmark.png. size = 세로 픽셀."""
    if size in _cache: return _cache[size]
    im = Image.open('brand/sfx/qmark.png').convert('RGBA'); r = size / im.height
    _cache[size] = im.resize((int(im.width * r), size), Image.LANCZOS); return _cache[size]


def qmark(fr, x, y, size, t, tilt=-14):
    """fr: BGR 프레임 · (x, y) 가운데 · t<0 이면 안 그림."""
    if t < 0: return fr
    sc = 1.3 if t < 2 else (1.1 if t < 4 else 1.0)
    ang = tilt * min(1, t / 6)                                     # 뜬 뒤 6프레임 동안 살짝 기울어짐
    sp = sprite(size); im = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.LANCZOS).rotate(ang, expand=True, resample=Image.BICUBIC)
    a = np.asarray(im).astype(np.float32); h, w = a.shape[:2]; x0, y0 = int(x - w / 2), int(y - h / 2)
    H, W = fr.shape[:2]; x1, y1, x2, y2 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    a = a[y1 - y0:y2 - y0, x1 - x0:x2 - x0]; al = a[..., 3:4] / 255
    fr[y1:y2, x1:x2] = (fr[y1:y2, x1:x2] * (1 - al) + a[..., 2::-1] * al).astype(np.uint8)
    return fr


if __name__ == '__main__':
    fr = np.full((400, 400, 3), (200, 180, 220), np.uint8); cv2.imwrite(sys.argv[1], qmark(fr, 200, 200, 220, 8)); print(sys.argv[1])
