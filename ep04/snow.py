"""EP04 앞쪽 눈송이 한 겹 (0cr): 영상 위에 크고 흐린 눈송이가 바람 따라 비스듬히 떨어짐 (8fps 박자 맞춤).
usage: python3 ep04/snow.py in.mp4 out.mp4 [바람 0~1]
"""
import subprocess, tempfile, shutil, sys
import numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]; WIND = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS); fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f)
H, W = fr[0].shape[:2]; rng = np.random.default_rng(4)
N = 46; S = [dict(x=rng.uniform(-200, W), y=rng.uniform(-H, H), r=rng.uniform(4, 13), sp=rng.uniform(70, 150), ph=rng.uniform(0, 6)) for _ in range(N)]
tmp = tempfile.mkdtemp()
for k, f in enumerate(fr):
    t = (k - k % 3) / fps; lay = np.zeros((H, W), np.float32)
    for s in S:
        y = (s['y'] + s['sp'] * t) % (H + 60) - 30; x = (s['x'] + WIND * 200 * t + 25 * np.sin(t * 1.3 + s['ph'])) % (W + 100) - 50
        cv2.circle(lay, (int(x), int(y)), int(s['r']), 0.9 if s['r'] < 9 else 0.65, -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.6)[..., None]
    o = f.astype(np.float32) * (1 - lay) + np.array([255, 250, 245], np.float32) * lay
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(o, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(fps), '-i', f'{tmp}/%05d.jpg', '-i', src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', out], check=True)
shutil.rmtree(tmp, ignore_errors=True); print(out)
