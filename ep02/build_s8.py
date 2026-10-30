"""EP02 장면 8: 은서 머쓱한 웃음 "하하…" — 그림(ep02/s5-gyul-haha-butter.png) + 웃을 때마다 어깨·머리 들썩 (코드 워프, 크레딧 0).
머리는 많이 · 가슴은 조금 · 손은 그대로 (y 에 따라 이동량) · 최버터 뒷모습 · 모니터는 고정.
usage: python3 ep02/build_s8.py [목소리.wav] → ep02/s8-gyul-haha.mp4
"""
import subprocess, tempfile, sys
import numpy as np, cv2
FPS, W, H, SEC = 24, 1080, 810, 1.5
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'voice/ep02/gyul-lines/s8d-1-use.wav'   # 혁 10/30: 머쓱한 '하하…' (은서 목소리 높이 맞음)
V_AT = 0.12; BEATS = [0.17, 0.46]                            # 목소리 시작 · 웃음 소리 나는 곳 (목소리 기준 초)
img = cv2.resize(cv2.imread('ep02/s5-gyul-haha-butter.png'), (W, H), interpolation=cv2.INTER_AREA)
m = (cv2.imread('ep02/s8-gyul-mask.png', 0) > 127).astype(np.float32); m = cv2.dilate(m, np.ones((25, 25), np.uint8)); m[390:, :470] = 0   # 머리 윤곽 겹침 안 보이게 넓힘 · 모니터 빼기
m = cv2.GaussianBlur(m, (0, 0), 4)[..., None]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); wy = np.clip((620 - yy) / 380, 0, 1)        # 위로 갈수록 많이 움직임
def bounce(t):                                                   # 웃음마다 위로 톡 → 내려옴
    return sum(9 * np.exp(-((t - (V_AT + b + 0.05)) / 0.06) ** 2) for b in BEATS)
# 입: 웃음 소리 날 때만 벌림 (혁 10/30) — 원래 그림(벌린 입) · 반 벌림(세로로 눌러) · 다묾(피부로 덮고 웃는 선)
mm = np.zeros((H, W), np.float32); mk = cv2.imread('ep02/fx/s8-mouth-mask.png', 0); mm[325:385, 470:560] = mk / 255.0; mm = cv2.GaussianBlur(mm, (0, 0), 1.2)[..., None]
skin = np.median(img[320:330, 470:560].reshape(-1, 3), 0).astype(np.float32)
closed = img.astype(np.float32) * (1 - mm) + skin * mm
cv2.ellipse(closed, (514, 350), (24, 9), 0, 15, 165, (52, 38, 48), 2, cv2.LINE_AA)            # 웃는 입 선
closed = closed.astype(np.uint8)
half = img.copy(); top = 340; seg = img[top:376, 480:548]                                      # 위 입술선 기준으로 세로 55%
sq = cv2.resize(seg, (seg.shape[1], int(seg.shape[0] * 0.55)), interpolation=cv2.INTER_AREA)
half[top:376, 480:548] = closed[top:376, 480:548]; half[top:top + sq.shape[0], 480:548] = np.where(cv2.resize(mk[15:51, 10:78], (68, sq.shape[0]))[..., None] > 127, sq, half[top:top + sq.shape[0], 480:548])
SRv = 44100; vx = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', VOICE, '-ac', '1', '-ar', str(SRv), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
venv = np.array([np.sqrt((vx[i:i + 441] ** 2).mean()) for i in range(0, len(vx) - 441, 441)]); venv /= venv.max()
def mouth(t):                                                     # 0 다묾 · 1 반 · 2 벌림
    i = int((t - V_AT) * 100)
    if i < 0 or i >= len(venv): return 0
    e = venv[max(0, i - 2):i + 3].max(); return 2 if e > 0.35 else 1 if e > 0.1 else 0
tmp = tempfile.mkdtemp(); n = int(SEC * FPS)
for k in range(n):
    t = (k - k % 2) / FPS; d = bounce(t)
    base = (closed, half, img)[mouth(t)]
    wf = cv2.remap(base, xx, (yy + d * wy).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', (wf * m + base * (1 - m)).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE, '-filter_complex', f'[1:a]adelay={int(V_AT * 1000)}:all=1,apad[a]',
                '-map', '0:v', '-map', '[a]', '-t', str(n / FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep02/s8-gyul-haha.mp4'], check=True)
print('ep02/s8-gyul-haha.mp4', SEC, 's')

import shutil; shutil.rmtree(tmp, ignore_errors=True)   # 임시 프레임 지움 (10/30 디스크 꽉 참)
