"""모니터 메모장 화면 — 凸 줄을 한 칸씩 쳐 나가는 영상/그림. 크레딧 0. (凸 은 글꼴 대신 직접 그림)
usage: python3 tools/notepad_screen.py out.png|out.mp4 [줄 수 3] [한 줄 칸 10]
"""
import sys, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, 'tools')
import chat_screen as cs
W, H, INK, f = cs.W, cs.H, cs.INK, cs.f
ROWS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
COLS = int(sys.argv[3]) if len(sys.argv) > 3 else 10
HOLD = 8   # 다 쓰고 멈춤 프레임 (혁 10/29: 오래 있지 말고 바로 엔딩)


def glyph(d, x, y, s):
    """凸: 아래 넓은 네모 + 가운데 위로 솟은 네모."""
    w = s * 0.92; t = s * 0.13  # 획 두께
    # 凸 윤곽선 글자 (가운데가 높이 솟은 모양)
    pts = [(x, y + s), (x, y + s * 0.5), (x + w * 0.3, y + s * 0.5), (x + w * 0.3, y), (x + w * 0.7, y),
           (x + w * 0.7, y + s * 0.5), (x + w, y + s * 0.5), (x + w, y + s)]
    d.line(pts + [pts[0]], fill=INK, width=int(t), joint='curve')


def draw(n, caret=True):
    o = Image.new('RGB', (W, H), (214, 205, 228)); d = ImageDraw.Draw(o)
    d.rounded_rectangle((60, 40, W - 60, H - 40), 60, fill=(196, 198, 214), outline=INK, width=12)
    d.rectangle((170, 140, W - 170, H - 150), fill=(236, 240, 250), outline=INK, width=8)
    x0, y0, x1, y1 = 330, 220, W - 330, H - 230
    d.rounded_rectangle((x0 + 14, y0 + 18, x1 + 14, y1 + 18), 24, fill=(180, 184, 205))
    d.rounded_rectangle((x0, y0, x1, y1), 24, fill=(255, 255, 255), outline=INK, width=8)
    d.rounded_rectangle((x0, y0, x1, y0 + 110), 24, fill=(214, 220, 236), outline=INK, width=8)
    d.rectangle((x0 + 4, y0 + 80, x1 - 4, y0 + 106), fill=(214, 220, 236)); d.line((x0, y0 + 110, x1, y0 + 110), fill=INK, width=8)
    d.text((x0 + 50, y0 + 56), '메모장 - 제목 없음', font=f(50), fill=INK, anchor='lm')
    for i, c in enumerate([(255, 120, 120), (255, 210, 110), (130, 210, 140)]):
        d.ellipse((x1 - 70 - i * 60, y0 + 34, x1 - 30 - i * 60, y0 + 74), fill=c, outline=INK, width=4)
    s, gap, lx, ly = 118, 152, x0 + 90, y0 + 190
    k = 0
    for r in range(ROWS):
        for c in range(COLS):
            if k >= n: break
            glyph(d, lx + c * gap, ly + r * (s + 50), s); k += 1
    if caret:
        r, c = divmod(min(n, ROWS * COLS), COLS)
        if r >= ROWS: r, c = ROWS - 1, COLS
        cx = lx + c * gap + 6; cy = ly + r * (s + 50)
        d.rectangle((cx, cy - 4, cx + 8, cy + s + 4), fill=INK)
    return o.filter(ImageFilter.GaussianBlur(0.8))


if __name__ == '__main__':
    out = sys.argv[1]; total = ROWS * COLS
    if not out.endswith('.mp4'):
        cs.grain(draw(total, caret=False)).save(out); print(out); sys.exit()
    tmp = tempfile.mkdtemp(); frames = []
    frames += [draw(0)] * 6
    for n in range(1, total + 1): frames += [draw(n)] * 2   # 한 칸 = 2프레임(12fps 로 빠르게)
    frames += [draw(total, caret=(i // 6) % 2 == 0) for i in range(HOLD)]
    for i, im in enumerate(frames): cs.grain(im, i // 3).resize((1080, 810)).save(f'{tmp}/{i:05d}.jpg', quality=92)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '24', '-i', f'{tmp}/%05d.jpg', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', out], check=True)
    print(out, round(len(frames) / 24, 1), 's')
