"""EP02 장면 5: 은서 "예? 왜요?" → 눈 · 고개 11시로 천천히 갔다가 돌아옴 — H3 영상(ep02/video/s5-gyul-huh-h3.mp4, 10cr) 1.25~5.0초 · 1.2배 · 12fps
+ 왼쪽 최버터 뒷모습(장면 3 그대로) 얹음. 크레딧 0.
(혁 10/29: 그림 몇 장 번갈아 보여주는 건 눈이 끊기고 이상함 → 영상)
usage: python3 ep02/build_s5.py → ep02/s5-gyul-huh.mp4
"""
import subprocess, tempfile
import numpy as np, cv2
FPS, W, H = 24, 1080, 810
V0, V1, SPD = 1.25, 5.0, 1.2
cap = cv2.VideoCapture('ep02/video/s5-gyul-huh-h3.mp4'); vf = cap.get(cv2.CAP_PROP_FPS); v = []
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
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s5-gyul-huh.mp4'], check=True)
print('ep02/s5-gyul-huh.mp4', round(n / FPS, 2), 's')
