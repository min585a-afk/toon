"""옛날 애니 '적게 움직이고 많이 움직이는 척' — 멈춘 그림으로 줌 · 흔들림 · 번쩍 · 속도선 · 배경 흐름. 크레딧 0.
usage: python3 animatic.py out.mp4   (EP02 컷 4장 데모)
"""
import sys, subprocess, math, os, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W, H, FPS = 1080, 810, 24
rng = np.random.default_rng(1)
def load(p): return Image.open(p).convert('RGB')
def view(im, z=1.0, cx=0.5, cy=0.5, dx=0, dy=0):
    w, h = im.size; s = max(W / w, H / h) * z
    big = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    x = int(big.width * cx - W / 2 + dx); y = int(big.height * cy - H / 2 + dy)
    x = max(0, min(big.width - W, x)); y = max(0, min(big.height - H, y))
    return big.crop((x, y, x + W, y + H))
def speedlines(fr, n, seed, horizontal=False):
    d = ImageDraw.Draw(fr); r = np.random.default_rng(seed)
    for _ in range(n):
        if horizontal:
            y = r.integers(0, H); x = r.integers(-200, W); L = r.integers(150, 500)
            d.line([(x, y), (x + L, y)], fill=(255, 255, 255), width=int(r.integers(2, 6)))
        else:
            a = r.uniform(0, 2 * math.pi); r0 = r.uniform(260, 380)
            d.line([(W/2 + math.cos(a)*r0, H/2 + math.sin(a)*r0), (W/2 + math.cos(a)*900, H/2 + math.sin(a)*900)], fill=(255, 255, 255), width=int(r.integers(2, 7)))
    return fr
frames = []
c1, c2, c3, c4 = [load(f'ep02/cut{i}.png') for i in (1, 2, 3, 4)]
# 컷1 3초: 천천히 줌인 (긴장)
for i in range(72):
    t = i / 71; frames.append(view(c1, 1.0 + 0.12 * t, 0.62, 0.42))
# 컷2 3초: 흰 번쩍 2장 → 확 당겨진 줌 → 흔들림 + 집중선 깜빡
for i in range(2): frames.append(Image.new('RGB', (W, H), (255, 255, 255)))
for i in range(70):
    z = 1.35 - 0.3 * min(1, i / 6)  # 펀치 줌
    sh = 14 * math.exp(-i / 18)
    fr = view(c2, z, 0.5, 0.45, rng.normal(0, sh), rng.normal(0, sh))
    if (i // 3) % 2 == 0: fr = speedlines(fr, 40, i)
    frames.append(fr)
# 컷3 2초: 빨강 번쩍 1장 → 덜덜 떨림
frames.append(Image.new('RGB', (W, H), (200, 30, 40)))
for i in range(47):
    frames.append(view(c3, 1.08, 0.5, 0.45, rng.normal(0, 5), rng.normal(0, 3)))
# 컷4 4초: 배경 오른쪽으로 흐름(카메라 따라가기) + 통통 튐 + 가로 속도선
for i in range(96):
    t = i / 95
    fr = view(c4, 1.25, 0.35 + 0.5 * t, 0.5, 0, -abs(math.sin(i * 0.9)) * 18)
    fr = speedlines(fr, 25, 1000 + i, horizontal=True)
    frames.append(fr)
# 옛날 애니처럼 8fps 로 끊기: 3장마다 같은 그림
tmp = tempfile.mkdtemp()
for k, fr in enumerate(frames):
    frames[k - k % 3].save(f'{tmp}/{k:04d}.jpg', quality=92)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%04d.jpg', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', sys.argv[1]], check=True)
print(sys.argv[1], len(frames) / FPS, 's')
