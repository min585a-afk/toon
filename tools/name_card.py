"""인물 소개 자막 (1화 첫 등장) — 이름 크게 + 괄호 안 나이/직급, 흰 글자 + 굵은 남색 테두리, 툭 튀어나옴. 크레딧 0.
card(fr, name, sub, x, y, t) : t = 뜬 뒤 프레임 수 (t<0 이면 안 그림). (x, y) = 가운데.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_c = {}


def _img(name, sub, size):
    k = (name, sub, size)
    if k in _c: return _c[k]
    f1, f2 = ImageFont.truetype('tools/fonts/jua.ttf', size), ImageFont.truetype('tools/fonts/jua.ttf', int(size * 0.55))
    sw = max(4, size // 9); tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    w = max(tmp.textlength(name, font=f1), tmp.textlength(sub, font=f2)) + sw * 4 + 20; h = size * 1.75 + sw * 4
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((w / 2 + 4, size * 0.55 + sw + 5), name, font=f1, anchor='mm', fill=(30, 25, 60, 150), stroke_width=sw, stroke_fill=(30, 25, 60, 150))  # 그림자
    d.text((w / 2, size * 0.55 + sw), name, font=f1, anchor='mm', fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(40, 35, 80, 255))
    d.text((w / 2, size * 1.35 + sw), sub, font=f2, anchor='mm', fill=(255, 232, 120, 255), stroke_width=max(3, sw * 2 // 3), stroke_fill=(40, 35, 80, 255))
    _c[k] = im; return im


def card(fr, name, sub, x, y, t, size=86):
    if t < 0: return fr
    sc = 1.25 if t < 2 else (1.08 if t < 4 else 1.0)
    im = _img(name, sub, size); im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32); h, w = a.shape[:2]; x0, y0 = int(x - w / 2), int(y - h / 2)
    H, W = fr.shape[:2]; x1, y1, x2, y2 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    a = a[y1 - y0:y2 - y0, x1 - x0:x2 - x0]; al = a[..., 3:4] / 255
    fr[y1:y2, x1:x2] = (fr[y1:y2, x1:x2] * (1 - al) + a[..., 2::-1] * al).astype(np.uint8)
    return fr
