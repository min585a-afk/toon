"""EP02 장면 4: 최버터 얼굴 — 반짝반짝 + 이름 '최버터 (대리)' 1.6초 멈춤 → 잘난 척 "오늘 퇴근 후에 뭐 해애~?" (입 맞춤). 크레딧 0.
usage: python3 ep02/build_s4.py [목소리.wav] → ep02/s4-butter-face.mp4
"""
import subprocess, tempfile, sys, os
import numpy as np, cv2
sys.path.insert(0, 'tools'); from name_card import card, fade
sys.path.insert(0, 'ep02'); from fx import star
FPS, W, H = 24, 1080, 810
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'voice/ep02/butter-line1.wav'
HOLD = 1.6                                                       # 혁 10/29: 얼굴 나오고 1~2초 멈춤 + 이름
tmp = tempfile.mkdtemp()
subprocess.run(['python3', 'tools/talk_mouth.py', 'char/butter/talk/mouth-1-closed.png', 'char/butter/talk/mouth-2-open.png', VOICE, f'{tmp}/talk.mp4',
                '--mouth', '1204,861', '--r', '150,70', '--size', '2336x1744', '--pre', str(HOLD), '--post', '0.7'], check=True)


cap = cv2.VideoCapture(f'{tmp}/talk.mp4'); frames = []
while True:
    ok, fr = cap.read()
    if not ok: break
    frames.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
STARS = [(735, 70, 0.0), (300, 160, 0.35), (820, 330, 0.7), (250, 420, 1.05)]   # 머리 · 얼굴 둘레 반짝 (x, y, 시작초)
out = []
for k, fr in enumerate(frames):
    t = (k - k % 2) / FPS
    for x, y, t0 in STARS:
        ph = ((t - t0) % 1.4) / 0.5                               # 0.5초 동안 커졌다 작아짐, 1.4초마다
        if t >= t0 and ph < 1: fr = star(fr, x, y, int(46 * np.sin(ph * np.pi)))
    if k < int((HOLD + 0.5) * FPS): fr = card(fr, '최버터', '(대리)', 540, 730, 0, alpha=fade(k - 3, int((HOLD + 0.5) * FPS) - 3))
    out.append(fr)
for i, fr in enumerate(out): cv2.imwrite(f'{tmp}/f{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/f%05d.jpg', '-i', f'{tmp}/talk.mp4', '-map', '0:v', '-map', '1:a',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s4-butter-face.mp4'], check=True)
print('ep02/s4-butter-face.mp4', round(len(out) / FPS, 2), 's')
