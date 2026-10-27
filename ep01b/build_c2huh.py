"""EP01 컷 '네?..': 그림 프레임으로 직접 (H3 뭉개짐 없이, 혁 10/27) — 귤이 눈 위로 본 채 → 말하는 순간 시무룩한 얼굴로 탁 바뀜
→ 목소리 크기대로 입 열고 닫음(초당 8번) + 물음표가 위에서 곡선으로 떨어져 통 튀고 흔들 멈춤. 크레딧 0.
usage: python3 ep01b/build_c2huh.py  → ep01b/c2-gyul-huh.mp4
"""
import subprocess, sys, tempfile
import numpy as np
import cv2
sys.path.insert(0, 'tools'); from qmark import qmark_drop

FPS, W, H = 24, 1080, 810
VOICE, VOICE_AT, SEC = 'voice/ep01/c2-gyul-ne.wav', 0.4, 2.2
MOUTH = (1150, 835)
look, sulk = cv2.imread('ep01b/c00-gyul-look.png'), cv2.imread('ep01b/c00-gyul-sulk.png')
op = cv2.resize(cv2.imread('ep01b/talk/c00-sulk-open-raw.png'), (sulk.shape[1], sulk.shape[0]))
x0, y0 = MOUTH[0] - 200, MOUTH[1] - 150
g = lambda im: cv2.cvtColor(im[y0:y0 + 300, x0:x0 + 400], cv2.COLOR_BGR2GRAY).astype(np.float32)
(dx, dy), _ = cv2.phaseCorrelate(g(sulk), g(op))
op = cv2.warpAffine(op, np.float32([[1, 0, -dx], [0, 1, -dy]]), (sulk.shape[1], sulk.shape[0]), borderMode=cv2.BORDER_REPLICATE)
m = np.zeros(sulk.shape[:2], np.float32); cv2.ellipse(m, MOUTH, (75, 50), 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), 8)[..., None]
sz = lambda im: cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
A, B0, B1 = sz(look), sz(sulk), sz((sulk * (1 - m) + op * m).astype(np.uint8))

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', VOICE, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32); hop = 2000                       # 1/8초
rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)]); top = rms.max() + 1e-9
tmp = tempfile.mkdtemp(); n = int(SEC * FPS); v0 = int(VOICE_AT * FPS)
for k in range(n):
    if k < v0: fr = A
    else:
        j = (k - v0) // 3; fr = B1 if j < len(rms) and rms[j] > top * 0.35 else B0
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', qmark_drop(fr.copy(), 815, 290, 200, k - v0), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE,
                '-filter_complex', f'[1:a]adelay={int(VOICE_AT * 1000)}:all=1,apad[a]', '-map', '0:v', '-map', '[a]', '-t', str(SEC),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/c2-gyul-huh.mp4'], check=True)
print('ep01b/c2-gyul-huh.mp4', SEC, 's')
