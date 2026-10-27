"""EP01 앞부분 (혁 10/27 순서): 귤이 타닥타닥(또각또각 들려옴) → 팀장 걸어옴(H3, 12fps · 1.6배) → 귤이 눈만 살짝 위로 → (컷 1: 서류 내밂 → 얼굴 클로즈업 대사). 크레딧 0.
usage: python3 ep01b/build_c00.py  → ep01b/c00-gyul-work.mp4 · ep01b/c0-boss-walk.mp4 · ep01b/c00b-gyul-look.mp4
"""
import subprocess, tempfile
import numpy as np
import cv2

FPS, W, H = 24, 1080, 810
base = cv2.imread('ep01b/c00-gyul-work.png'); up = cv2.resize(cv2.imread('ep01b/talk/c00-eyes-up-raw.png'), (base.shape[1], base.shape[0]))
EYES = (1155, 690)  # 두 눈 + 눈썹 가운데 (2336x1744)
x0, y0 = EYES[0] - 320, EYES[1] - 200
g = lambda im: cv2.cvtColor(im[y0:y0 + 400, x0:x0 + 640], cv2.COLOR_BGR2GRAY).astype(np.float32)
(dx, dy), _ = cv2.phaseCorrelate(g(base), g(up))
up = cv2.warpAffine(up, np.float32([[1, 0, -dx], [0, 1, -dy]]), (base.shape[1], base.shape[0]), borderMode=cv2.BORDER_REPLICATE)
m = np.zeros(base.shape[:2], np.float32); cv2.ellipse(m, EYES, (250, 120), 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), 18)[..., None]
look = (base * (1 - m) + up * m).astype(np.uint8)
A, B = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA), cv2.resize(look, (W, H), interpolation=cv2.INTER_AREA)
cv2.imwrite('ep01b/c00-gyul-look.png', look)

TYPE_SEC, LOOK_SEC = 1.6, 0.9      # 타닥타닥 컷 · 눈 올리는 컷 길이
HEELS_AT = 0.8                     # 또각또각 시작 (타닥타닥 컷 안에서)
WALK_FROM, SPEED, WALK_SEC = 0.5, 1.6, 1.9


def write(frames, audio_filter, inputs, out, secs):
    tmp = tempfile.mkdtemp()
    for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
    cmd = ['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg'] + sum([['-i', x] for x in inputs], [])
    cmd += ['-filter_complex', audio_filter, '-map', '0:v', '-map', '[a]', '-t', str(secs), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', out]
    subprocess.run(cmd, check=True); print(out, secs, 's')


# 컷 00: 타닥타닥 + 또각또각 (멀리서 작게)
write([A] * int(TYPE_SEC * FPS), f"[1:a]atrim=0:{TYPE_SEC},volume=0.8[t];[2:a]atrim=0:{TYPE_SEC - HEELS_AT},volume=0.3,adelay={int(HEELS_AT * 1000)}:all=1[h];"
      f"[t][h]amix=inputs=2:duration=longest:normalize=0,apad[a]", ['sfx/ep01/typing.mp3', 'sfx/ep01/heels.mp3'], 'ep01b/c00-gyul-work.mp4', TYPE_SEC)

# 컷 0: 팀장 걸어옴 — 1.6배 빠르게 · 12fps (2프레임씩)
cap = cv2.VideoCapture('ep01b/video/c0-boss-walk-h3.mp4'); sf = cap.get(cv2.CAP_PROP_FPS) or 24; vf = []
while True:
    ok, fr = cap.read()
    if not ok: break
    vf.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
n = int(WALK_SEC * FPS)
frames = [vf[min(len(vf) - 1, int((WALK_FROM + (k - k % 2) / FPS * SPEED) * sf))] for k in range(n)]
hs = TYPE_SEC - HEELS_AT
write(frames, f"[1:a]atrim={hs}:{hs + WALK_SEC},asetpts=PTS-STARTPTS,volume=0.6,apad[a]", ['sfx/ep01/heels.mp3'], 'ep01b/c0-boss-walk.mp4', WALK_SEC)

# 컷 00b: 귤이 눈만 살짝 위로 (또각또각 가까이서 두 번 · 멈춤)
write([B] * int(LOOK_SEC * FPS), f"[1:a]atrim={hs + WALK_SEC}:{hs + WALK_SEC + 0.45},asetpts=PTS-STARTPTS,volume=0.7,afade=t=out:st=0.3:d=0.15,apad[a]",
      ['sfx/ep01/heels.mp3'], 'ep01b/c00b-gyul-look.mp4', LOOK_SEC)
