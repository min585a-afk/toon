"""EP01 컷 '왜요? 어려운가요?': 팀장 클로즈업 — 안경 하얗게 번쩍(눈 가림) → 빛이 렌즈를 대각선으로 쓸고 지나가며 눈이 조금씩 보임(혁 10/27) → 대사. 크레딧 0.
usage: python3 ep01b/build_c3why.py  → ep01b/c3-boss-why.mp4
"""
import os, subprocess, tempfile
import numpy as np
import cv2

FPS, W, H = 24, 1080, 810
GLARE_SEC = 0.7
H3 = 'ep01b/video/c3-boss-glasses-h3.mp4'          # 안경 번쩍 → 고쳐 씀 (있으면 씀)
tmp = tempfile.mkdtemp()
subprocess.run(['python3', 'tools/talk_mouth.py', 'char/boss/talk/mouth-1-closed.png', 'char/boss/talk/mouth-2-open.png', 'voice/ep01/c3-boss-why.wav',
                f'{tmp}/talk.mp4', '--mouth', '1166,918', '--r', '85,62', '--pre', '0.15', '--post', '1.0'], check=True)
face0 = cv2.imread('char/boss/talk/mouth-1-closed.png'); gl = cv2.resize(cv2.imread('ep01b/c3-boss-glare.png'), (face0.shape[1], face0.shape[0]))
gg = lambda im: cv2.cvtColor(im[500:900, 700:1700], cv2.COLOR_BGR2GRAY).astype(np.float32)
(ddx, ddy), _ = cv2.phaseCorrelate(gg(face0), gg(gl)); gl = cv2.warpAffine(gl, np.float32([[1, 0, -ddx], [0, 1, -ddy]]), (face0.shape[1], face0.shape[0]), borderMode=cv2.BORDER_REPLICATE)
lens = ((cv2.absdiff(gl, face0).max(2) > 40) & (cv2.cvtColor(gl, cv2.COLOR_BGR2GRAY) > 190)).astype(np.uint8)   # 하얗게 바뀐 렌즈만
lens[:560] = 0; lens[860:] = 0                                                                                      # 눈썹·입은 제외
lens = cv2.morphologyEx(lens, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
lens = cv2.GaussianBlur(lens.astype(np.float32), (0, 0), 2)[..., None]
glare = (face0 * (1 - lens) + gl * lens).astype(np.uint8)           # 번쩍은 렌즈 안에서만
yy, xx = np.mgrid[0:face0.shape[0], 0:face0.shape[1]].astype(np.float32); diag = (xx + yy * 0.6)
lo, hi = diag[lens[..., 0] > 0.3].min(), diag[lens[..., 0] > 0.3].max()
REVEAL = 10                                                          # 빛이 쓸고 지나가는 프레임 수 (12fps → 0.8초)
def reveal(p):
    edge = lo + (hi - lo) * p; w = (hi - lo) * 0.12
    show = np.clip((edge - diag) / w, 0, 1)[..., None]               # 지나간 곳 = 눈 보임
    streak = np.exp(-((diag - edge) / (w * 0.35)) ** 2)[..., None]   # 빛줄기
    o = gl * (1 - show) + face0 * show; o = o + 255 * streak * 0.6
    return np.clip(face0 * (1 - lens) + o * lens, 0, 255).astype(np.uint8)
frames = [cv2.resize(glare, (W, H), interpolation=cv2.INTER_AREA)] * int(GLARE_SEC * FPS)
for k in range(REVEAL * 2):
    frames.append(cv2.resize(reveal(((k - k % 2) / 2 + 1) / REVEAL), (W, H), interpolation=cv2.INTER_AREA))
if os.path.exists(H3):
    cap = cv2.VideoCapture(H3); f = cap.get(cv2.CAP_PROP_FPS) or 24; v = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
    frames += [v[min(len(v) - 1, int((k - k % 2) / FPS * f))] for k in range(int(len(v) / f * FPS))]
pre = len(frames)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{tmp}/talk.mp4', f'{tmp}/t_%05d.jpg'], check=True)
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/f_{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
n = len([x for x in os.listdir(tmp) if x.startswith('t_')])
for k in range(n): os.rename(f'{tmp}/t_{k + 1:05d}.jpg', f'{tmp}/f_{pre + k:05d}.jpg')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/f_%05d.jpg', '-i', f'{tmp}/talk.mp4',
                '-filter_complex', f'[1:a]adelay={int(pre / FPS * 1000)}:all=1,apad[a]', '-map', '0:v', '-map', '[a]', '-t', str((pre + n) / FPS),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/c3-boss-why.mp4'], check=True)
print('ep01b/c3-boss-why.mp4', round((pre + n) / FPS, 1), 's')
