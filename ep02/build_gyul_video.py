"""EP02 은서 H3 영상 컷 공통: 구간만 · 배속 · 12fps + 왼쪽 최버터 뒷모습(장면 3 그대로) 얹기. 크레딧 0.
usage: python3 ep02/build_gyul_video.py 영상.mp4 시작초 끝초 배속 out.mp4
"""
import subprocess, tempfile, sys
import numpy as np, cv2
FPS, W, H = 24, 1080, 810
src, V0, V1, SPD, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
cap = cv2.VideoCapture(src); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32))
E = cv2.resize(cv2.imread('ep02/s3-butter-back2.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
M = cv2.GaussianBlur((cv2.imread('ep02/s3-butter-back2-mask.png', 0) > 127).astype(np.float32), (0, 0), 2)[..., None]
n = int((V1 - V0) / SPD * FPS); tmp = tempfile.mkdtemp()
for k in range(n):
    fr = v[min(len(v) - 1, int((V0 + (k - k % 2) / FPS * SPD) * vf))]
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(fr * (1 - M) + E * M, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, round(n / FPS, 2), 's')

import shutil; shutil.rmtree(tmp, ignore_errors=True)   # 임시 프레임 지움 (10/30 디스크 꽉 참)
