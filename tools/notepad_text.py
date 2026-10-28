"""모니터 메모장에 글자를 한 글자씩 쳐 나가는 영상 (글씨는 그림 말고 코드로 → 안 깨짐). 크레딧 0.
usage: python3 tools/notepad_text.py out.mp4 "첫 줄" "둘째 줄" ... [--sec 2.2] [--hold 0.5]
한 글자 = 3프레임(초당 8글자) · 줄 바꿀 때 4프레임 쉼 · 끝나고 hold 초 멈춤. 크기 1080x810.
"""
import argparse, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFilter
import sys
sys.path.insert(0, 'tools')
import chat_screen as cs
W, H, INK, f = cs.W, cs.H, cs.INK, cs.f
FPS = 24
TOTAL_LINES = 2


def draw(lines, caret=True, total=None):
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
    n = max(2, TOTAL_LINES); size = 150 if n <= 2 else max(80, int(150 * 2.6 / n)); gap = int(size * 1.5)   # 줄 많으면 작게
    fb = f(size); lx, ly = x0 + 110, y0 + 150 + int(size * 0.9)
    for i, t in enumerate(lines): d.text((lx, ly + i * gap), t, font=fb, fill=INK, anchor='lm')
    if caret:
        cx = lx + d.textlength(lines[-1], font=fb) + 14; cy = ly + (len(lines) - 1) * gap
        d.rectangle((cx, cy - size // 2, cx + 14, cy + size // 2), fill=INK)
    return cs.grain(o.filter(ImageFilter.GaussianBlur(0.8)), 3)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('lines', nargs='+'); ap.add_argument('--hold', type=float, default=0.5)
    a = ap.parse_args(); tmp = tempfile.mkdtemp(); frames = []
    global TOTAL_LINES; TOTAL_LINES = len(a.lines)
    shown = ['']
    def hold(img, n): frames.extend([img] * n)
    hold(draw(shown), 4)
    for li, line in enumerate(a.lines):
        if li: shown.append(''); hold(draw(shown), 4)
        for k in range(1, len(line) + 1):
            shown[-1] = line[:k]; hold(draw(shown, caret=(k % 2 == 0) or True), 3)
    hold(draw(shown), int(a.hold * FPS))
    cache = {}
    for i, im in enumerate(frames):
        if id(im) not in cache: cache[id(im)] = im.resize((1080, 810), Image.LANCZOS)
        cache[id(im)].save(f'{tmp}/{i:05d}.jpg', quality=92)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', a.out], check=True)
    print(a.out, round(len(frames) / FPS, 2), 's')


if __name__ == '__main__':
    main()
