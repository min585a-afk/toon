"""인물 소개 자막 (1화 첫 등장) — '이름 (직급)' 한 줄, 평범한 글꼴 흰 글자 + 검정 테두리, 화면 아래 가운데. 크레딧 0.
card(fr, name, sub, x, y, t) : t = 뜬 뒤 프레임 수 (t<0 이면 안 그림). (x, y) = 가운데.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_c = {}


def _img(text, size):
    """혁 10/27: 평범한 글꼴(Gothic A1) · 흰 글자 + 검정 테두리 · 한 줄 '이름 (직급)'."""
    k = (text, size)
    if k in _c: return _c[k]
    f = ImageFont.truetype('tools/fonts/ga1-800.ttf', size); sw = max(3, size // 12)
    w = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textlength(text, font=f) + sw * 4 + 10; h = size * 1.4 + sw * 2
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((w / 2, h / 2), text, font=f, anchor='mm', fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(15, 12, 18, 255))
    _c[k] = im; return im


def card(fr, name, sub, x, y, t, size=54, alpha=1.0):
    """'이름 (직급)' 한 줄을 (x, y) 가운데에 그냥 띄움 (튀어나오는 효과 없음). t<0 이면 안 그림."""
    if t < 0 or alpha <= 0: return fr
    im = _img(f'{name} {sub}', size)
    a = np.asarray(im).astype(np.float32); h, w = a.shape[:2]; x0, y0 = int(x - w / 2), int(y - h / 2)
    H, W = fr.shape[:2]; x1, y1, x2, y2 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    a = a[y1 - y0:y2 - y0, x1 - x0:x2 - x0]; al = a[..., 3:4] / 255 * alpha
    fr[y1:y2, x1:x2] = (fr[y1:y2, x1:x2] * (1 - al) + a[..., 2::-1] * al).astype(np.uint8)
    return fr


def fade(k, n, f=7):
    """0~n 프레임 동안: 앞 f 프레임 페이드 인 · 뒤 f 프레임 페이드 아웃."""
    return 0.0 if k < 0 or k >= n else min(1, (k + 1) / f, (n - k) / f)
