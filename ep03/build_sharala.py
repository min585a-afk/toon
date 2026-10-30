"""EP03 상상 컷 '샤랄라' (0cr): 그림 한 장 + 옛날 애니식 움직임 — 반짝이 깜빡깜빡 · 꽃잎 팔랑 떨어짐 · 비눗방울 둥실 · 아주 천천히 다가감. 12fps.
usage: python3 ep03/build_sharala.py 그림.png 초 out.mp4
"""
import subprocess, tempfile, shutil, sys
import numpy as np, cv2
sys.path.insert(0, 'ep02'); from fx import star
FPS, W, H = 24, 1080, 810
src, sec, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
img = cv2.resize(cv2.imread(src), (W, H), interpolation=cv2.INTER_AREA); rng = np.random.default_rng(3)
STARS = [(rng.uniform(60, 1020), rng.uniform(40, 770), rng.uniform(0, 1.2)) for _ in range(9)]
PET = [dict(x=rng.uniform(0, W), y=rng.uniform(-H, H), s=rng.uniform(14, 26), sp=rng.uniform(60, 120), ph=rng.uniform(0, 6)) for _ in range(14)]
BUB = [dict(x=rng.uniform(80, 1000), y=rng.uniform(200, 900), r=rng.uniform(18, 40), sp=rng.uniform(25, 50)) for _ in range(6)]
tmp = tempfile.mkdtemp(); n = int(sec * FPS)
for k in range(n):
    t = (k - k % 2) / FPS; z = 1 + 0.03 * t / sec
    fr = cv2.warpAffine(img, cv2.getRotationMatrix2D((W / 2, H / 2), 0, z), (W, H), borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    lay = np.zeros_like(fr); al = np.zeros((H, W), np.float32)
    for p in BUB:                                                # 비눗방울: 테두리만 하얗게 · 위로 둥실
        y = (p['y'] - p['sp'] * t) % (H + 100) - 50; c = (int(p['x'] + 8 * np.sin(t * 2 + p['r'])), int(y))
        cv2.circle(al, c, int(p['r']), 0.55, 2, cv2.LINE_AA); cv2.circle(al, (c[0] - int(p['r'] * .4), c[1] - int(p['r'] * .4)), max(2, int(p['r'] * .15)), 0.8, -1, cv2.LINE_AA)
    fr = fr * (1 - al[..., None]) + 255 * al[..., None]
    for p in PET:                                                # 꽃잎: 분홍 타원 · 흔들리며 떨어짐
        y = (p['y'] + p['sp'] * t) % (H + 120) - 60; x = p['x'] + 30 * np.sin(t * 1.5 + p['ph'])
        cv2.ellipse(fr, (int(x), int(y)), (int(p['s']), int(p['s'] * .55)), (t * 90 + p['ph'] * 50) % 180, 0, 360, (190, 170, 245), -1, cv2.LINE_AA)
        cv2.ellipse(fr, (int(x), int(y)), (int(p['s']), int(p['s'] * .55)), (t * 90 + p['ph'] * 50) % 180, 0, 360, (150, 120, 210), 1, cv2.LINE_AA)
    fr = np.clip(fr, 0, 255).astype(np.uint8)
    for x, y, t0 in STARS:                                       # 반짝이 깜빡
        ph = ((t + t0) % 1.2) / 0.5
        if ph < 1: fr = star(fr, int(x), int(y), int(36 * np.sin(ph * np.pi)))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
shutil.rmtree(tmp, ignore_errors=True); print(out, sec, 's')
