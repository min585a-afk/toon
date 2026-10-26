"""캐릭터 도안(콜아웃 시트) — 확정 전신 1장에서 부위를 잘라 둘레에 배치 + 지시선 + 색 팔레트. 크레딧 0.
잘라 쓰니까 원본과 100% 같음. 나중에 생성한 디테일 컷으로 칸만 바꿔 끼우면 됨.
usage: python3 callout_sheet.py out.png
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
SRC = 'presets/v3/gyul-step1-fullbody-02-2026.png'
F = 'tools/fonts/ga1-800.ttf'
im = Image.open(SRC).convert('RGB'); A = np.asarray(im).astype(int)
CW, CH = 2600, 2250
o = Image.new('RGB', (CW, CH), (246, 242, 234)); d = ImageDraw.Draw(o)
fl = ImageFont.truetype(F, 40); fs = ImageFont.truetype(F, 30); ft = ImageFont.truetype(F, 56)
# 가운데 전신
fx0, fx1 = 340, 1500; k = 1800 / im.height
fig = im.crop((fx0, 0, fx1, im.height)); fig = fig.resize((int(fig.width * k), 1800), Image.LANCZOS)
ox = (CW - fig.width) // 2; oy = 120; o.paste(fig, (ox, oy))
P2 = lambda x, y: (ox + (x - fx0) * k, oy + y * k)
d.text((60, 30), '귤이 · 캐릭터 도안 v1', font=ft, fill=(40, 30, 30))
# 콜아웃: (이름, 잘라낼 영역, 지시선 끝점, 칸 위치)
B = 500
calls = [
    ('머리 · 남보라 각진 광택', (600, 40, 1200, 360), (900, 150), (60, 140)),
    ('사원증 · 남색 줄 · 빈 카드', (780, 780, 960, 1220), (870, 1100), (60, 760)),
    ('흰 스니커즈', (660, 2080, 1040, 2280), (850, 2200), (60, 1380)),
    ('얼굴 · 90년대 눈 · 빗금 볼', (660, 380, 1140, 780), (900, 600), (CW - B - 60, 140)),
    ('아아 · 빨대 컵 · 손', (600, 840, 840, 1110), (720, 980), (CW - B - 60, 760)),
    ('오버핏 빨간 니트 가디건', (920, 1000, 1240, 1380), (1080, 1200), (CW - B - 60, 1380)),
]
for name, box, tgt, (bx, by) in calls:
    c = im.crop(box); c.thumbnail((B - 20, B - 20), Image.LANCZOS)
    d.rounded_rectangle((bx, by, bx + B, by + B), 18, fill=(255, 255, 255), outline=(40, 30, 30), width=5)
    o.paste(c, (bx + (B - c.width) // 2, by + (B - c.height) // 2))
    d.text((bx, by + B + 8), name, font=fs, fill=(40, 30, 30))
    tx, ty = P2(*tgt); sx = bx + B if bx < CW / 2 else bx; sy = by + B / 2
    d.line([(sx, sy), (tx, ty)], fill=(220, 60, 50), width=5); d.ellipse((tx - 10, ty - 10, tx + 10, ty + 10), fill=(220, 60, 50))
# 색 팔레트 (원본에서 뽑은 값)
def med(box, cond=None):
    x0, y0, x1, y1 = box; p = A[y0:y1, x0:x1].reshape(-1, 3)
    if cond is not None: p = p[cond(p)]
    return tuple(int(v) for v in np.median(p, 0))
pal = [
    ('머리', med((420, 450, 560, 700), lambda p: p.max(1) < 70)),
    ('머리 광택', med((600, 40, 1200, 360), lambda p: (p[:, 2] - p[:, 0] > 25) & (p.max(1) < 170) & (p.max(1) > 70))),
    ('피부', med((780, 480, 1020, 560), lambda p: p.min(1) > 150)),
    ('볼', med((700, 600, 1100, 700), lambda p: (p[:, 0] > 200) & (p[:, 1] < 175))),
    ('가디건', med((560, 1150, 760, 1350), lambda p: p[:, 0] - p[:, 1] > 60)),
    ('티', med((840, 820, 940, 900), lambda p: p.min(1) > 200)),
    ('슬랙스', med((700, 1600, 1000, 1900))),
    ('사원증 줄', med((800, 780, 900, 1000), lambda p: (p[:, 2] - p[:, 0] > 30) & (p.max(1) < 180))),
]
py = 2020; d.text((60, py - 60), '색', font=fl, fill=(40, 30, 30))
for i, (n, c) in enumerate(pal):
    x = 60 + i * 310
    d.rounded_rectangle((x, py, x + 120, py + 120), 14, fill=c, outline=(40, 30, 30), width=3)
    d.text((x + 135, py + 14), n, font=fs, fill=(40, 30, 30))
    d.text((x + 135, py + 62), '#%02X%02X%02X' % c, font=fs, fill=(110, 100, 100))
o.save(sys.argv[1]); print(sys.argv[1]); [print(n, '#%02X%02X%02X' % c) for n, c in pal]
