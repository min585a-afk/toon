"""EP02 H3 영상 컷: (출력 초, 원본 프레임) 키로 대사 마디에 입을 맞춰 프레임 고름 (사이는 선형) · 12fps · 무음(목소리는 full.json). 크레딧 0.
선택 --butter: 왼쪽 최버터 뒷모습(장면 3 그대로) 얹기 (은서 컷).
usage: python3 ep02/build_keyed.py 영상.mp4 '[[0,10],[0.2,12],...]' 길이초 out.mp4 [--butter]
"""
import subprocess, tempfile, sys, json
import numpy as np, cv2
FPS, W, H = 24, 1080, 810
src, keys, sec, out = sys.argv[1], json.loads(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
cap = cv2.VideoCapture(src); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
if '--butter' in sys.argv:
    E = cv2.resize(cv2.imread('ep02/s3-butter-back2.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
    M = cv2.GaussianBlur((cv2.imread('ep02/s3-butter-back2-mask.png', 0) > 127).astype(np.float32), (0, 0), 2)[..., None]
kt, kf = zip(*keys); tmp = tempfile.mkdtemp(); n = int(sec * FPS)
for k in range(n):
    fr = v[min(len(v) - 1, int(round(np.interp((k - k % 2) / FPS, kt, kf))))]
    if '--butter' in sys.argv: fr = np.clip(fr * (1 - M) + E * M, 0, 255).astype(np.uint8)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, sec, 's')
