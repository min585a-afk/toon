"""눈 반짝이 추가 — 동그란 하이라이트 2개 + 작은 별 1개. 크레딧 0.
usage: python3 eye_sparkle.py in.png out.png "눈동자x,y,가로반경,세로반경;..." [세기 0~1, 기본 1]
"""
import sys
from PIL import Image, ImageDraw, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
irises = [tuple(map(float, e.split(','))) for e in sys.argv[3].split(';')]
k = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
im = Image.open(src).convert('RGB')
SS = 4  # 4배로 그려서 줄이기 (테두리 부드럽게)
lay = Image.new('L', (im.width * SS, im.height * SS), 0)
d = ImageDraw.Draw(lay)
def ell(x, y, rx, ry):
    d.ellipse([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], fill=255)
def star(x, y, r):
    w = r * 0.22
    for pts in ([(x, y - r), (x + w, y), (x, y + r), (x - w, y)], [(x - r, y), (x, y - w), (x + r, y), (x, y + w)]):
        d.polygon([(px * SS, py * SS) for px, py in pts], fill=255)
for x, y, rx, ry in irises:
    ell(x - 0.32 * rx, y + 0.52 * ry, 0.17 * rx * k, 0.15 * ry * k)   # 아래 동그란 하이라이트
    ell(x + 0.42 * rx, y + 0.34 * ry, 0.08 * rx * k, 0.07 * ry * k)   # 오른쪽 아래 작은 점
    star(x + 0.48 * rx, y - 0.62 * ry, 0.28 * rx * k)                 # 위쪽 작은 별
lay = lay.resize(im.size, Image.LANCZOS)
glow = lay.filter(ImageFilter.GaussianBlur(4)).point(lambda v: v * 0.35)
white = Image.new('RGB', im.size, (255, 253, 250))
im = Image.composite(white, im, glow)
im = Image.composite(white, im, lay)
im.save(dst)
print(dst)
