"""EP01 컷 '네…': 귤이 눈 위로 본 채 → 옆에 노랑 '?' 툭(살짝 기울어짐) → 시무룩한 입·눈썹 + "네…" (혁 10/27: '예?' 대신). 크레딧 0.
usage: python3 ep01b/build_c2huh.py  → ep01b/c2-gyul-huh.mp4
"""
import subprocess, sys, tempfile
import numpy as np
import cv2
sys.path.insert(0, 'tools'); from qmark import qmark

FPS, W, H = 24, 1080, 810
Q_AT, PRE, SEC = 0.15, 0.6, 2.0                      # ? 뜨는 순간 · 시무룩 + 목소리 시작 · 컷 길이
look = cv2.imread('ep01b/c00-gyul-look.png'); oo = cv2.resize(cv2.imread('ep01b/talk/c00-mouth-sulk-raw.png'), (look.shape[1], look.shape[0]))
MOUTH = (1150, 835)
x0, y0 = MOUTH[0] - 200, MOUTH[1] - 150
g = lambda im: cv2.cvtColor(im[y0:y0 + 300, x0:x0 + 400], cv2.COLOR_BGR2GRAY).astype(np.float32)
(dx, dy), _ = cv2.phaseCorrelate(g(look), g(oo))
oo = cv2.warpAffine(oo, np.float32([[1, 0, -dx], [0, 1, -dy]]), (look.shape[1], look.shape[0]), borderMode=cv2.BORDER_REPLICATE)
m = np.zeros(look.shape[:2], np.float32); cv2.ellipse(m, MOUTH, (90, 60), 0, 0, 360, 1, -1); cv2.ellipse(m, (1155, 610), (260, 70), 0, 0, 360, 1, -1)  # 입 + 눈썹; m = cv2.GaussianBlur(m, (0, 0), 10)[..., None]
A = cv2.resize(look, (W, H), interpolation=cv2.INTER_AREA)
B = cv2.resize((look * (1 - m) + oo * m).astype(np.uint8), (W, H), interpolation=cv2.INTER_AREA)
tmp = tempfile.mkdtemp(); n = int(SEC * FPS); s = int(PRE * FPS); q = int(Q_AT * FPS)
for f in range(n):
    fr = qmark((A if f < s else B).copy(), 800, 270, 210, f - q)
    cv2.imwrite(f'{tmp}/{f:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', 'voice/ep01/c2-gyul-ne.wav',
                '-filter_complex', f'[1:a]adelay={int(PRE * 1000)}:all=1,apad[a]', '-map', '0:v', '-map', '[a]', '-t', str(SEC),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/c2-gyul-huh.mp4'], check=True)
print('ep01b/c2-gyul-huh.mp4', SEC, 's')
