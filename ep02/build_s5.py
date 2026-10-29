"""EP02 장면 5: 은서 "예? 왜요?" (최버터 보며 놀람) → 눈만 오른쪽 시계로 한 번 힐끗 → 다시 최버터. 크레딧 0 (그림 편집 2cr).
usage: python3 ep02/build_s5.py → ep02/s5-gyul-huh.mp4
"""
import subprocess, tempfile
import cv2
FPS, W, H = 24, 1080, 810
a = cv2.resize(cv2.imread('ep02/s5a-gyul-huh-butter.png'), (W, H)); b = cv2.resize(cv2.imread('ep02/s5a-gyul-glance-butter.png'), (W, H))
seq = [a] * int(0.7 * FPS) + [b] * int(0.6 * FPS) + [a] * int(0.3 * FPS)        # 최버터 → 시계 힐끗 → 최버터
tmp = tempfile.mkdtemp()
for i, fr in enumerate(seq): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s5-gyul-huh.mp4'], check=True)
print('ep02/s5-gyul-huh.mp4', round(len(seq) / FPS, 2), 's')
