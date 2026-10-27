"""EP01 컷 '예?': 귤이 눈 위로 본 채 → 입 'o' + 옆에 입체 '?' 툭(살짝 기울어짐) + "예?". 크레딧 0.
usage: python3 ep01b/build_c2huh.py  → ep01b/c2-gyul-huh.mp4
"""
import subprocess, sys, tempfile
import numpy as np
import cv2
sys.path.insert(0, 'tools'); from qmark import qmark

FPS, W, H = 24, 1080, 810
PRE, SEC = 0.25, 1.6                                 # 'o' + ? + 목소리 시작 · 컷 길이
look = cv2.imread('ep01b/c00-gyul-look.png'); oo = cv2.resize(cv2.imread('ep01b/talk/c00-mouth-o-raw.png'), (look.shape[1], look.shape[0]))
MOUTH = (1150, 835)
x0, y0 = MOUTH[0] - 200, MOUTH[1] - 150
g = lambda im: cv2.cvtColor(im[y0:y0 + 300, x0:x0 + 400], cv2.COLOR_BGR2GRAY).astype(np.float32)
(dx, dy), _ = cv2.phaseCorrelate(g(look), g(oo))
oo = cv2.warpAffine(oo, np.float32([[1, 0, -dx], [0, 1, -dy]]), (look.shape[1], look.shape[0]), borderMode=cv2.BORDER_REPLICATE)
m = np.zeros(look.shape[:2], np.float32); cv2.ellipse(m, MOUTH, (70, 55), 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), 10)[..., None]
A = cv2.resize(look, (W, H), interpolation=cv2.INTER_AREA)
B = cv2.resize((look * (1 - m) + oo * m).astype(np.uint8), (W, H), interpolation=cv2.INTER_AREA)
tmp = tempfile.mkdtemp(); n = int(SEC * FPS); s = int(PRE * FPS)
for f in range(n):
    fr = A.copy() if f < s else qmark(B.copy(), 800, 270, 210, f - s)
    cv2.imwrite(f'{tmp}/{f:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', 'voice/ep01/c2-gyul-ye.wav',
                '-filter_complex', f'[1:a]adelay={int(PRE * 1000)}:all=1,apad[a]', '-map', '0:v', '-map', '[a]', '-t', str(SEC),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/c2-gyul-huh.mp4'], check=True)
print('ep01b/c2-gyul-huh.mp4', SEC, 's')
