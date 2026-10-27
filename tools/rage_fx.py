"""분노 효과 — 정지 그림 위에 만화식 불꽃(아래에서 위로) · 빨간 깜빡임 · 흔들림 · 머리카락 끝 일렁임. 크레딧 0.
불꽃은 90년대 셀 애니처럼 단색 덩어리 2~3겹(그라데이션 X), 초당 8장으로 끊김.
usage: python3 tools/rage_fx.py in.png out.mp4 [초 1.6]   (in-cut.png = 배경 제거 RGBA 가 있으면 인물 뒤로만 불)
"""
import sys, subprocess, tempfile
import numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]; secs = float(sys.argv[3]) if len(sys.argv) > 3 else 1.6
W, H, FPS = 1080, 810, 24
img = cv2.resize(cv2.imread(src), (W, H), interpolation=cv2.INTER_AREA)
# 인물 마스크: 같은 이름의 -cut.png (배경 제거 결과 RGBA) 가 있으면 그 알파 사용
import os
cut = src.replace('.png', '-cut.png')
if os.path.exists(cut):
    al = cv2.imread(cut, cv2.IMREAD_UNCHANGED)[..., 3]; fg = cv2.resize(al, (W, H)).astype(np.float32) / 255
else:
    fg = np.ones((H, W), np.float32)
fg = cv2.GaussianBlur(fg, (0, 0), 1.2)[..., None]
COLS = [(40, 40, 200), (30, 120, 245), (90, 210, 255)]  # BGR 빨강 · 주황 · 노랑


def flames(t, seed):
    lay = np.zeros((H, W, 3), np.uint8); a = np.zeros((H, W), np.float32); rng = np.random.default_rng(seed)
    for li, (col, base, amp) in enumerate(zip(COLS, [H * 0.15, H * 0.32, H * 0.48], [H * 0.55, H * 0.42, H * 0.28])):
        pts = [(0, H)]
        for x in range(0, W + 60, 60):
            h = base + amp * (0.55 + 0.45 * np.sin(x * 0.021 + t * 9 + li * 2)) * rng.uniform(0.75, 1.15)
            pts += [(x - 30, H - h * 0.55), (x, H - h)]
        pts += [(W, H)]
        cv2.fillPoly(lay, [np.array(pts, np.int32)], col); cv2.fillPoly(a.view(), [np.array(pts, np.int32)], 1.0)
    cv2.polylines(lay, [], False, (0, 0, 0))
    return lay, cv2.GaussianBlur(a, (0, 0), 1.5)[..., None]


def vein(fr, cx, cy, r, k):
    """빨간 핏대(빡침 마크): 네 개의 꺾인 획이 가운데를 보고 모인 모양 + 진한 테두리. k 프레임마다 맥박."""
    from PIL import Image, ImageDraw
    sc = 4; R = r * (1.0 + 0.18 * ((k // 3) % 2)); im = Image.new('RGBA', (int(R * 2.6 * sc), int(R * 2.6 * sc)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = R * 1.3 * sc; rr = R * 0.78 * sc
    for qx, qy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        ox, oy = c + qx * R * 0.92 * sc, c + qy * R * 0.92 * sc        # 바깥 모서리에 원 중심 → 가운데 쪽으로 볼록한 호
        mid = np.degrees(np.arctan2(-qy, -qx)); box = (ox - rr, oy - rr, ox + rr, oy + rr)
        d.arc(box, mid - 42, mid + 42, fill=(30, 15, 25, 255), width=int(R * 0.40 * sc))
        d.arc(box, mid - 38, mid + 38, fill=(235, 55, 60, 255), width=int(R * 0.24 * sc))
    im = im.resize((im.width // sc, im.height // sc), Image.LANCZOS); a = np.asarray(im).astype(np.float32)
    x0, y0 = int(cx - a.shape[1] / 2), int(cy - a.shape[0] / 2)
    roi = fr[y0:y0 + a.shape[0], x0:x0 + a.shape[1]].astype(np.float32); al = a[..., 3:4] / 255
    fr[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = (roi * (1 - al) + a[..., 2::-1][..., :3] * al).astype(np.uint8)
    return fr


VEIN = (int(W * 0.66), int(H * 0.17), 74)


def sfx(fr, text, x, y, size, ang, k, start, stretch=1.0, font='tools/fonts/sfx-BlackHanSans.ttf'):
    """만화 효과 글자: 흰 글자 + 굵은 검정 테두리, 기울임, 툭 튀어나오며 커졌다 제자리."""
    from PIL import Image, ImageDraw, ImageFont
    t = k - start
    if t < 0: return fr
    sc = 1.35 if t < 2 else (1.1 if t < 4 else 1.0)
    f = ImageFont.truetype(font, int(size * sc))
    tw = int(f.getlength(text)) + 60; im = Image.new('RGBA', (tw, int(size * sc * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((30, 10), text, font=f, fill=(255, 255, 255, 255), stroke_width=max(4, int(size * sc * (0.05 if stretch > 1 else 0.09))), stroke_fill=(20, 15, 20, 255))
    if stretch != 1.0: im = im.resize((int(im.width / stretch ** 0.4), int(im.height * stretch)), Image.LANCZOS)  # 세로로 길쭉하게
    im = im.rotate(ang, expand=True, resample=Image.BICUBIC); a = np.asarray(im).astype(np.float32)
    x0, y0 = int(x - a.shape[1] / 2), int(y - a.shape[0] / 2); h, w = a.shape[:2]
    x1, y1 = max(0, x0), max(0, y0); x2, y2 = min(W, x0 + w), min(H, y0 + h)
    a = a[y1 - y0:y2 - y0, x1 - x0:x2 - x0]; al = a[..., 3:4] / 255
    fr[y1:y2, x1:x2] = (fr[y1:y2, x1:x2] * (1 - al) + a[..., 2::-1][..., :3] * al).astype(np.uint8)
    return fr   # 이마 오른쪽 위 (그림마다 다르면 고치기)
tmp = tempfile.mkdtemp(); n = int(secs * FPS)
for f in range(n):
    k = f - f % 3; t = k / FPS
    fl, fa = flames(t, k)
    bg = img.astype(np.float32)
    pulse = 0.35 + 0.25 * (k // 3 % 2)                                  # 빨간 깜빡임 (8fps)
    bg = bg * (1 - pulse * 0.4) + np.array([20, 20, 160], np.float32) * pulse * 0.4
    bg = bg * (1 - fa) + fl * fa                                        # 불은 인물 뒤
    fr = bg * (1 - fg) + img.astype(np.float32) * fg
    # 머리카락 끝 일렁임: 위쪽을 살짝 좌우로 물결
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = 6 * np.sin(yy * 0.03 + t * 14) * np.clip((H * 0.6 - yy) / (H * 0.6), 0, 1)
    fr = cv2.remap(fr.astype(np.uint8), xx + dx, yy, cv2.INTER_LINEAR)
    sx, sy = np.random.default_rng(k + 5).normal(0, 5, 2)                # 흔들림
    fr = cv2.warpAffine(fr, np.float32([[1.03, 0, sx - W * 0.015], [0, 1.03, sy - H * 0.015]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    if f >= 4: fr = vein(fr, VEIN[0] + int(sx), VEIN[1] + int(sy), VEIN[2], k)  # 0.17초 뒤 툭
    fr = sfx(fr, '빠직', int(W * 0.13) + int(sx), int(H * 0.40) + int(sy), 135, -16, f, 3, stretch=2.3, font='tools/fonts/sfx-DoHyeon.ttf')
    cv2.imwrite(f'{tmp}/{f:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 92])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', out], check=True)
print(out)
