"""EP03 반전 컷 (0cr): 거울 앞 그림(ep03/s8-mirror.png)에서 얼굴 쪽 확대로 시작 → 툭 뒤로 빠지며 전체 (거울이었음!). 12fps.
usage: python3 ep03/build_mirror.py 초 → ep03/s8-mirror.mp4
"""
import subprocess, tempfile, shutil, sys
import numpy as np, cv2
FPS, W, H = 24, 1080, 810; SEC = float(sys.argv[1]) if len(sys.argv) > 1 else 2.2
img = cv2.imread('ep03/s8-mirror.png'); SH, SW = img.shape[:2]
fx, fy = SW * 0.72, SH * 0.30                                    # 거울 속 얼굴
tmp = tempfile.mkdtemp(); n = int(SEC * FPS)
for k in range(n):
    t = (k - k % 2) / FPS; p = min(1, t / 0.35); p = 1 - (1 - p) ** 3   # 0.35초 만에 확 빠짐
    z = 2.4 + (1 - 2.4) * p; cx = fx + (SW / 2 - fx) * p; cy = fy + (SH / 2 - fy) * p
    M = np.float32([[z * W / SW, 0, W / 2 - z * W / SW * cx], [0, z * H / SH, H / 2 - z * H / SH * cy]])
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep03/s8-mirror.mp4'], check=True)
shutil.rmtree(tmp, ignore_errors=True); print('ep03/s8-mirror.mp4', SEC, 's')
