"""EP02 장면 6: 최버터 H3 영상(ep02/video/s6-butter-gesture-h3.mp4, 10cr) — 머리 쓸어넘기며 윙크 "끝나고 저녁 어때~?"
입 움직이는 구간(4~47 프레임)만 대사 길이에 맞춰 돌리고, 다문 입 웃음(47~57)으로 끝. 12fps. 크레딧 0.
usage: python3 ep02/build_s6.py [목소리.wav 시작 입벌림 입다묾 끝 out.mp4] → 기본 ep02/s6-butter-gesture.mp4
      (장면 9 는 새 영상 · ep02/build_s9.py)
"""
import subprocess, tempfile, sys
import cv2
FPS, W, H = 24, 1080, 810
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'voice/ep02/butter-lines/s6b-2-use.wav'   # 혁 10/29: 대사 '끝나고 저녁 어때~?' 로 바꿈
a = sys.argv[2:]; S0, M0, M1, END = (int(x) for x in a[:4]) if a else (0, 4, 47, 58)   # 시작 · 입 벌림 · 입 다묾 · 끝 프레임
OUT = a[4] if len(a) > 4 else 'ep02/s6-butter-gesture.mp4'
VLEN = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VOICE], capture_output=True, text=True).stdout)
cap = cv2.VideoCapture('ep02/video/s6-butter-gesture-h3.mp4'); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
def src(t):
    s0 = (M0 - S0) / vf
    if t < s0: return S0 + int(t * vf)
    if t < s0 + VLEN: return talk(t - s0)
    return int(M1 + (t - s0 - VLEN) * vf)
# 목소리 쉬는 동안(0.15초 넘게 조용)은 입 덜 벌린 프레임에서 멈춤 · 말할 때만 입 프레임 진행 (혁 10/30: 대사랑 입 속도 안 맞음)
import numpy as np
SR = 44100; vx = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', VOICE, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
env = np.array([np.sqrt((vx[i:i + 441] ** 2).mean()) for i in range(0, len(vx) - 441, 441)]); act = env > env.max() * 0.12
for i in range(len(act)):                                        # 0.15초보다 짧은 쉼은 말하는 걸로
    if not act[i]:
        j = i
        while j < len(act) and not act[j]: j += 1
        if j - i < 15 and j < len(act): act[i:j] = True
cum = np.cumsum(act) / max(1, act.sum())                         # 말한 비율 → 입 프레임
def opened(f):
    h = cv2.cvtColor(cv2.resize(f, (540, 405))[100:300, 150:420], cv2.COLOR_BGR2HSV)
    return int((((h[..., 0] < 10) | (h[..., 0] > 170)) & (h[..., 1] > 110) & (h[..., 2] > 80) & (h[..., 2] < 215)).sum())
OPEN = [opened(f) for f in v]
def talk(tv):                                                    # 목소리 안 시간 → 프레임
    i = min(len(act) - 1, int(tv * 100)); p = int(M0 + cum[i] * (M1 - M0))
    if act[i]: return p
    near = range(max(M0, p - 6), min(M1, p + 6) + 1); return min(near, key=lambda q: OPEN[q])
n = int((M0 - S0 + (END - M1)) / vf * FPS + VLEN * FPS); tmp = tempfile.mkdtemp()
for k in range(n):
    t = (k - k % 2) / FPS; cv2.imwrite(f'{tmp}/{k:05d}.jpg', v[min(len(v) - 1, src(t))], [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE, '-filter_complex', f'[1:a]adelay={int((M0 - S0) / vf * 1000)}:all=1,apad[a]',
                '-map', '0:v', '-map', '[a]', '-t', str(n / FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', OUT], check=True)
print(OUT, round(n / FPS, 2), 's')
