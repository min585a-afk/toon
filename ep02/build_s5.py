"""EP02 장면 5: 은서 "예? 왜요?" → 눈만 11시로 천천히 갔다가 천천히 돌아옴 (혁 10/29). 눈 5단계 그림을 차례로. 크레딧 0 (그림 편집 5cr).
usage: python3 ep02/build_s5.py → ep02/s5-gyul-huh.mp4
"""
import subprocess, tempfile
import cv2
FPS, W, H = 24, 1080, 810
A, Q1, M, Q3, B = [cv2.resize(cv2.imread(p), (W, H)) for p in ['ep02/s5a-gyul-huh-butter.png', 'ep02/s5a-gyul-q1-butter.png', 'ep02/s5a-gyul-mid-butter.png', 'ep02/s5a-gyul-q3-butter.png', 'ep02/s5a-gyul-glance-butter.png']]
# 혁 10/29: 너무 끊김 → 눈 5단계 (0 · 25 · 50 · 75 · 100%) 12fps 로 천천히 갔다 옴
seq = [A] * 8 + [Q1] * 2 + [M] * 2 + [Q3] * 2 + [B] * 10 + [Q3] * 2 + [M] * 2 + [Q1] * 2 + [A] * 6
tmp = tempfile.mkdtemp()
for i, fr in enumerate(seq): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s5-gyul-huh.mp4'], check=True)
print('ep02/s5-gyul-huh.mp4', round(len(seq) / FPS, 2), 's')
