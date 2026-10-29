"""EP02 장면 5: 은서 "예? 왜요?" → 눈만 11시로 천천히 갔다가 천천히 돌아옴 (혁 10/29). 눈 5단계 그림을 차례로. 크레딧 0 (그림 편집 5cr).
usage: python3 ep02/build_s5.py → ep02/s5-gyul-huh.mp4
"""
import subprocess, tempfile
import cv2
FPS, W, H = 24, 1080, 810
import numpy as np
# 혁 10/29 프레임 분석: 처음 그림(huh-big)만 눈 모양이 달라 튀고, 75% 그림이 100% 보다 더 가 있어서 눈이 왔다갔다 → 같은 눈 모양 그림만 · 잰 위치 순서대로
P0, P1, P2 = [cv2.resize(cv2.imread(p), (W, H)) for p in ['ep02/s5a-gyul-q1-butter.png', 'ep02/s5a-gyul-mid-butter.png', 'ep02/s5a-gyul-q3-butter.png']]
sharpen = lambda im: cv2.addWeighted(im, 1.35, cv2.GaussianBlur(im, (0, 0), 1.2), -0.35, 0)            # 편집본 살짝 흐린 것 맞춤
P0, P1, P2 = [sharpen(x) for x in (P0, P1, P2)]
seq = [P0] * 9 + [P1] * 3 + [P2] * 11 + [P1] * 3 + [P0] * 8     # 최버터 → 중간 → 11시(머묾) → 중간 → 최버터
tmp = tempfile.mkdtemp()
for i, fr in enumerate(seq): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s5-gyul-huh.mp4'], check=True)
print('ep02/s5-gyul-huh.mp4', round(len(seq) / FPS, 2), 's')
