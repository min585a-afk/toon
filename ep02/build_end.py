"""EP02 끝 장면 (혁 10/30): '끝' 대신 웃기게 — 검정 화면에 '응, 회식 안 해.' + 아래 작게 YEP. NO TEAM DINNER. · 0.4초 페이드 인. 무음 (띠링은 full.json).
usage: python3 ep02/build_end.py → ep02/e-end.mp4  (1화 끝 ep01b/build_end.py 와 같은 틀)"""
import subprocess, tempfile
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
# 글꼴: 1화 '끝' 과 같은 나눔명조 ExtraBold ('응,회식안해.' 만 든 subset — Google Fonts css2 ?text=)
FPS, W, H, SEC, FADE = 24, 1080, 810, 2.2, 0.4
img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
d.text((W // 2, H // 2 - 30), '응, 회식 안 해.', font=ImageFont.truetype('tools/fonts/end2-NanumMyeongjo-800.ttf', 118), fill=232, anchor='mm')
d.text((W // 2, H // 2 + 85), 'YEP. NO TEAM DINNER.', font=ImageFont.truetype('tools/fonts/ga1-800.ttf', 38), fill=200, anchor='mm')
txt = cv2.GaussianBlur(np.array(img, np.float32), (0, 0), 0.8)
tmp = tempfile.mkdtemp(); rng = np.random.default_rng(9)
for k in range(int(SEC * FPS)):
    a = min(1, k / (FADE * FPS)); g = txt * a + 3 + rng.normal(0, 3, (H, W))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(np.stack([g * 0.97, g * 0.99, g], -1), 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/e-end.mp4'], check=True)
print('ep02/e-end.mp4', SEC, 's')
