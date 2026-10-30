"""EP03 상상 컷 '샤랄라' (0cr): 그림 한 장 + 옛날 애니식 움직임 — 반짝이 깜빡깜빡 · 꽃잎 팔랑 떨어짐 · 비눗방울 둥실 · 아주 천천히 다가감. 12fps.
usage: python3 ep03/build_sharala.py 그림.png 초 out.mp4 [--flash] [--shake]
  --flash: 카메라 플래시 팡팡 (패셔니스타) · --shake: 시작에 깜짝 놀라 흔들림 · --glint x,y: 번쩍 (안경 · 메달) · --confetti: 색종이 · --bloom: 둘레에 꽃이 하나씩 피어나며 나타남 (혁 10/30 '꽃 페이드')
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
FLASH, SHAKE, BLOOM = '--flash' in sys.argv, '--shake' in sys.argv, '--bloom' in sys.argv
CONF = '--confetti' in sys.argv                                   # --confetti: 색종이 팔랑 (신부)
CF = [dict(x=rng.uniform(0, W), y=rng.uniform(-H, H), w=rng.uniform(8, 14), sp=rng.uniform(90, 160), ph=rng.uniform(0, 6), c=[(240, 200, 120), (180, 220, 250), (200, 170, 250), (150, 230, 200)][i % 4]) for i in range(22)]
GLINT = tuple(int(v) for v in sys.argv[sys.argv.index('--glint') + 1].split(',')) if '--glint' in sys.argv else None   # --glint x,y : 안경 번쩍 (0.3초에 크게)
FLW = [(90, 120, 0.15), (990, 90, 0.3), (60, 470, 0.45), (1020, 420, 0.55), (180, 760, 0.7), (900, 760, 0.8), (520, 40, 0.95), (330, 770, 1.05), (720, 790, 1.15)]   # (x, y, 피기 시작 초) — 얼굴 피해 둘레
def flower(fr, x, y, r, a, rot, col=(200, 175, 250), dark=(150, 120, 215)):   # 셀 꽃: 다섯 꽃잎 + 노란 가운데 · a = 불투명도
    lay = fr.copy()
    for i in range(5):
        ang = rot + i * 72; dx, dy = np.cos(np.radians(ang)) * r * 0.55, np.sin(np.radians(ang)) * r * 0.55
        cv2.ellipse(lay, (int(x + dx), int(y + dy)), (int(r * 0.5), int(r * 0.34)), ang, 0, 360, col, -1, cv2.LINE_AA)
        cv2.ellipse(lay, (int(x + dx), int(y + dy)), (int(r * 0.5), int(r * 0.34)), ang, 0, 360, dark, 2, cv2.LINE_AA)
    cv2.circle(lay, (int(x), int(y)), int(r * 0.22), (90, 200, 250), -1, cv2.LINE_AA); cv2.circle(lay, (int(x), int(y)), int(r * 0.22), (60, 150, 210), 2, cv2.LINE_AA)
    return fr * (1 - a) + lay * a
FL = [(0.25, 120, 90), (0.9, 980, 120), (1.5, 140, 700), (2.2, 960, 690), (2.7, 560, 60)]   # (초, x, y) 플래시 터지는 곳
tmp = tempfile.mkdtemp(); n = int(sec * FPS)
for k in range(n):
    t = (k - k % 2) / FPS; z = 1 + 0.03 * t / sec
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    if SHAKE and t < 0.5: M[0, 2] += 10 * np.sin(t * 60) * (1 - t / 0.5); M[1, 2] += 6 * np.cos(t * 50) * (1 - t / 0.5)
    fr = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    lay = np.zeros_like(fr); al = np.zeros((H, W), np.float32)
    for p in BUB:                                                # 비눗방울: 테두리만 하얗게 · 위로 둥실
        y = (p['y'] - p['sp'] * t) % (H + 100) - 50; c = (int(p['x'] + 8 * np.sin(t * 2 + p['r'])), int(y))
        cv2.circle(al, c, int(p['r']), 0.55, 2, cv2.LINE_AA); cv2.circle(al, (c[0] - int(p['r'] * .4), c[1] - int(p['r'] * .4)), max(2, int(p['r'] * .15)), 0.8, -1, cv2.LINE_AA)
    fr = fr * (1 - al[..., None]) + 255 * al[..., None]
    if BLOOM:
        for x, y, t0 in FLW:
            p = np.clip((t - t0) / 0.45, 0, 1)
            if p > 0: fr = flower(fr, x, y, 70 * (0.35 + 0.65 * (1 - (1 - p) ** 3)), p, t * 25 + x)
    for p in PET:                                                # 꽃잎: 분홍 타원 · 흔들리며 떨어짐
        y = (p['y'] + p['sp'] * t) % (H + 120) - 60; x = p['x'] + 30 * np.sin(t * 1.5 + p['ph'])
        cv2.ellipse(fr, (int(x), int(y)), (int(p['s']), int(p['s'] * .55)), (t * 90 + p['ph'] * 50) % 180, 0, 360, (190, 170, 245), -1, cv2.LINE_AA)
        cv2.ellipse(fr, (int(x), int(y)), (int(p['s']), int(p['s'] * .55)), (t * 90 + p['ph'] * 50) % 180, 0, 360, (150, 120, 210), 1, cv2.LINE_AA)
    if FLASH:
        yy, xx = np.mgrid[0:H, 0:W]
        for t0, fx, fy in FL:
            a = t - t0
            if 0 <= a < 0.25:
                g = np.exp(-((xx - fx) ** 2 + (yy - fy) ** 2) / (2 * 260 ** 2)) * (1 - a / 0.25)
                fr = fr + (255 - fr) * (g[..., None] * 0.9 + 0.25 * (1 - a / 0.25) * (a < 0.09))
    fr = np.clip(fr, 0, 255).astype(np.uint8)
    if GLINT and 0.25 <= t < 0.7: fr = star(fr, GLINT[0], GLINT[1], int(80 * np.sin((t - 0.25) / 0.45 * np.pi)))
    for x, y, t0 in STARS:                                       # 반짝이 깜빡
        ph = ((t + t0) % 1.2) / 0.5
        if ph < 1: fr = star(fr, int(x), int(y), int(36 * np.sin(ph * np.pi)))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
shutil.rmtree(tmp, ignore_errors=True); print(out, sec, 's')
