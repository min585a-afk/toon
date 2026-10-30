"""EP03 장면 10~11: 현관 — 은서 신발 신고 나감 + 모과가 왼쪽 방문에서 나와 가운데 앉음 (H3 A) → 그대로 확 줌인 + 이름 '모과 (3살)'
→ 줌 빠지며 (왜 저래…) → 모과 돌아서 방문으로 들어감 (H3 B). 12fps. 크레딧 0 (영상 2개 20cr).
usage: python3 ep03/build_s10.py → ep03/s10-door.mp4  (컷 안 시간: ZOOM_AT · BACK_AT 를 print)
"""
import subprocess, tempfile, shutil, sys
import numpy as np, cv2
sys.path.insert(0, 'tools'); from name_card import card, fade
FPS, W, H = 24, 1080, 810
def load(p):
    cap = cv2.VideoCapture(p); v = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        v.append(fr)                                             # 원본 2K 그대로 (줌해도 선명)
    return v
A, B = load('ep03/video/s10-shoes-mogwa-h3.mp4'), load('ep03/video/s11-mogwa-back-h3.mp4')
SH, SW = A[0].shape[:2]
def dogc(fr):                                                    # 모과 가운데 (흰 털 덩어리)
    h = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV); m = ((h[..., 1] < 45) & (h[..., 2] > 200)).astype(np.uint8); m[:int(SH * .3)] = 0; m[int(SH * .8):] = 0
    n, lab, st, c = cv2.connectedComponentsWithStats(m)
    if n < 2: return SW / 2, SH * .55
    i = 1 + np.argmax(st[1:, 4]); return c[i]
END = A[-1]
dm = (cv2.GaussianBlur(np.abs(B[0].astype(int) - B[-1].astype(int)).sum(2).astype(np.float32), (0, 0), 6) > 60).astype(np.uint8)   # 모과 자리 = 모과 있을 때 − 나간 뒤
n_, lab, st, cc = cv2.connectedComponentsWithStats(dm); i_ = 1 + np.argmax(st[1:, 4]); cx, cy = cc[i_]; cy -= st[i_, 3] * 0.15   # 얼굴 쪽으로 살짝 위
def view(fr, z, fx, fy):                                         # (fx, fy) 를 가운데로 z 배 확대
    M = np.float32([[z * W / SW, 0, W / 2 - z * W / SW * fx], [0, z * H / SH, H / 2 - z * H / SH * fy]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
Z, ZIN, HOLD, ZOUT = 2.6, 0.25, 1.7, 0.3                         # 확대 배율 · 들어가는 시간 · 머묾 · 빠지는 시간
frames = []
for i in range(len(A)): frames.append(view(A[i], 1, SW / 2, SH / 2))
ZOOM_AT = len(frames) / FPS
n = int((ZIN + HOLD + ZOUT) * FPS)
for k in range(n):
    t = k / FPS
    if t < ZIN: p = 1 - (1 - t / ZIN) ** 3
    elif t < ZIN + HOLD: p = 1
    else: p = 1 - ((t - ZIN - HOLD) / ZOUT) ** 2
    z = 1 + (Z - 1) * p; fx = SW / 2 + (cx - SW / 2) * p; fy = SH / 2 + (cy - SH / 2) * p
    fr = view(END, z, fx, fy)
    if ZIN * 0.6 < t < ZIN + HOLD: fr = card(fr, '모과', '(3살)', 540, 730, 0, alpha=fade(int((t - ZIN * 0.6) * FPS), int((HOLD + ZIN * 0.4) * FPS)))
    frames.append(fr)
BACK_AT = len(frames) / FPS
for i in range(0, 100): frames.append(view(B[i], 1, SW / 2, SH / 2))
tmp = tempfile.mkdtemp()
for k in range(len(frames)): cv2.imwrite(f'{tmp}/{k:05d}.jpg', frames[k - k % 2], [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep03/s10-door.mp4'], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print('ep03/s10-door.mp4', round(len(frames) / FPS, 2), 's · 줌', round(ZOOM_AT, 2), '· 돌아감', round(BACK_AT, 2))
