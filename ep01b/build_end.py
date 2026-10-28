"""EP01 끝 장면 (혁 10/28): 검정 화면에 '끝' + 아래 작게 END · 0.4초 페이드 인 → 머묾. 무음.
usage: python3 ep01b/build_end.py → ep01b/e9-end.mp4"""
import subprocess, tempfile
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

# 글꼴: 제목과 같은 나눔명조 ExtraBold ('끝' 한 자만 든 subset — Google Fonts css2 ?text=끝)
FPS, W, H, SEC, FADE = 24, 1080, 810, 1.8, 0.4
f = ImageFont.truetype('tools/fonts/end-NanumMyeongjo-800.ttf', 150)
img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
d.text((W // 2, H // 2 - 30), '끝', font=f, fill=232, anchor='mm')       # 바랜 흰색 (필터 맞춤)
d.text((W // 2, H // 2 + 95), 'END', font=ImageFont.truetype('tools/fonts/ga1-800.ttf', 40), fill=200, anchor='mm')   # 아래 END (혁 10/28)
txt = cv2.GaussianBlur(np.array(img, np.float32), (0, 0), 0.8)
tmp = tempfile.mkdtemp(); rng = np.random.default_rng(9)
for k in range(int(SEC * FPS)):
    a = min(1, k / (FADE * FPS))
    g = txt * a + 3 + rng.normal(0, 3, (H, W))                      # 틀 검정과 이어지게 · 그레인만 살짝
    fr = np.clip(np.stack([g * 0.97, g * 0.99, g], -1), 0, 255).astype(np.uint8)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep01b/e9-end.mp4'], check=True)
print('ep01b/e9-end.mp4', SEC, 's')
