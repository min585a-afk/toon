"""화 제목 얹기 — 영상 위에 제목(나눔명조 ExtraBold 흰 글씨 + 얇은 남보라 테두리 · 그림자 없음) + 영어 부제를 페이드 인으로 얹음.
영상 안에 그리지 않고 위에 얹는 거라 화마다 제목만 바꾸면 됨. 크레딧 0.
usage: python3 tools/title_card.py in.mp4 out.mp4 "두 얼굴" "TWO FACES" --start 2.7 --dur 1.8 [--fade 0.9]
"""
import argparse, subprocess, tempfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

F1, F2 = 'tools/fonts/title-NanumMyeongjo-800.ttf', 'tools/fonts/ga1-800.ttf'


def layer(w, h, ko, en):
    """제목 글자 레이어 (RGBA). 1080x810 기준 크기를 영상 크기에 맞춰 키움."""
    s = w / 1080; im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(F1, int(140 * s)); f2 = ImageFont.truetype(F2, int(30 * s)); cx, cy = w / 2, h * 0.43
    def spaced(y, text, font, gap, fill):
        ws = [d.textlength(c, font=font) for c in text]; x = cx - (sum(ws) + gap * (len(text) - 1)) / 2
        for c, cw in zip(text, ws): d.text((x, y), c, font=font, anchor='lm', fill=fill, stroke_width=max(2, int(3 * s)), stroke_fill=(50, 30, 90, 255)); x += cw + gap
    spaced(cy, ko, f1, int(6 * s), (255, 255, 255, 255))
    if en: spaced(cy + 105 * s, '  '.join(en.split(' ')), f2, int(12 * s), (255, 238, 205, 255))
    a = np.asarray(im).astype(np.float32); return a[..., 2::-1], a[..., 3:4] / 255


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('ko'); ap.add_argument('en', nargs='?', default='')
    ap.add_argument('--start', type=float, required=True); ap.add_argument('--dur', type=float, required=True); ap.add_argument('--fade', type=float, default=0.9)
    a = ap.parse_args()
    cap = cv2.VideoCapture(a.src); fps = cap.get(cv2.CAP_PROP_FPS) or 24
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rgb, al = layer(w, h, a.ko, a.en); tmp = tempfile.mkdtemp(); i = 0
    while True:
        ok, fr = cap.read()
        if not ok: break
        t = i / fps - a.start
        if 0 <= t < a.dur:
            k = min(1, t / a.fade); k = k * k * (3 - 2 * k)  # 부드럽게 페이드 인
            fr = (fr * (1 - al * k) + rgb * al * k).astype(np.uint8)
        cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93]); i += 1
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(fps), '-i', f'{tmp}/%05d.jpg', '-i', a.src, '-map', '0:v', '-map', '1:a?',
                    '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', a.out], check=True)
    print(a.out)


if __name__ == '__main__':
    main()
