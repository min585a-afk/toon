"""EP02 장면 4: 최버터 H3 영상(ep02/video/s4-butter-talk-h3.mp4, 10cr) — 머리 쓸어넘기며 "오늘 퇴근 후에 뭐 해애~?" → 윙크.
처음 1.6초 이름 '최버터 (대리)' + 반짝이 · 12fps · 목소리는 임시(나중에 정함). 크레딧 0.
usage: python3 ep02/build_s4.py [목소리.wav] → ep02/s4-butter-face.mp4
"""
import subprocess, tempfile, sys
import numpy as np, cv2
sys.path.insert(0, 'tools'); from name_card import card, fade
sys.path.insert(0, 'ep02'); from fx import star
FPS, W, H = 24, 1080, 810
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'voice/ep02/butter-dylan-use.wav'
HOLD, V_AT = 1.6, 1.3                                           # 이름 떠 있는 시간 · 목소리 시작(영상 입 움직이기 시작하는 곳)
cap = cv2.VideoCapture('ep02/video/s4-butter-talk-h3.mp4'); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
n = int(len(v) / vf * FPS); tmp = tempfile.mkdtemp()
STARS = [(735, 70, 0.0), (300, 160, 0.35), (820, 330, 0.7)]
for k in range(n):
    t = (k - k % 2) / FPS; fr = v[min(len(v) - 1, int(t * vf))].copy()
    for x, y, t0 in STARS:
        ph = ((t - t0) % 1.4) / 0.5
        if t >= t0 and ph < 1 and t < HOLD + 0.4: fr = star(fr, x, y, int(44 * np.sin(ph * np.pi)))
    fr = card(fr, '최버터', '(대리)', 540, 730, 0, alpha=fade(k - 3, int((HOLD + 0.5) * FPS) - 3))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE, '-filter_complex', f'[1:a]adelay={int(V_AT * 1000)}:all=1,apad[a]',
                '-map', '0:v', '-map', '[a]', '-t', str(n / FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep02/s4-butter-face.mp4'], check=True)
print('ep02/s4-butter-face.mp4', round(n / FPS, 2), 's')
