"""EP02 장면 4: 최버터 H3 영상(ep02/video/s4-butter-talk-h3.mp4, 10cr) — 머리 쓸어넘기며 "퇴근 후에 뭐 해~?" → 윙크.
처음 1.6초 이름 '최버터 (대리)' + 반짝이 · 12fps · 목소리는 임시(나중에 정함). 크레딧 0.
usage: python3 ep02/build_s4.py [목소리.wav] → ep02/s4-butter-face.mp4
"""
import subprocess, tempfile, sys
import numpy as np, cv2
sys.path.insert(0, 'tools'); from name_card import card, fade
sys.path.insert(0, 'ep02'); from fx import star
FPS, W, H = 24, 1080, 810
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'voice/ref/butter-base.wav'   # 확정 E2 '퇴근 후에 뭐 해~?' (혁 10/29)
HOLD = 1.6                                                       # 이름 떠 있는 시간
M0, M1 = 33, 100                                                 # 영상에서 입 움직이는 프레임 (1.38~4.13초) → 대사 길이에 맞춰 빨리 돌림 (혁 10/29: 대사 끝났는데 입 계속 움직임)
V_AT = M0 / 24                                                   # 목소리 시작 = 입 벌리는 순간
VLEN = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VOICE], capture_output=True, text=True).stdout)
cap = cv2.VideoCapture('ep02/video/s4-butter-talk-h3.mp4'); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
def src(t):                                                      # 출력 시간 → 원본 프레임 (입 구간만 압축)
    s0, s1 = M0 / vf, M1 / vf
    if t < s0: return int(t * vf)
    if t < s0 + VLEN: return int(M0 + (t - s0) / VLEN * (M1 - M0))
    return int(M1 + (t - s0 - VLEN) * vf)
n = int((M0 / vf + VLEN + (len(v) - M1) / vf) * FPS); tmp = tempfile.mkdtemp()
STARS = [(735, 70, 0.0), (300, 160, 0.35), (820, 330, 0.7)]
for k in range(n):
    t = (k - k % 2) / FPS; fr = v[min(len(v) - 1, src(t))].copy()
    for x, y, t0 in STARS:
        ph = ((t - t0) % 1.4) / 0.5
        if t >= t0 and ph < 1 and t < HOLD + 0.4: fr = star(fr, x, y, int(44 * np.sin(ph * np.pi)))
    fr = card(fr, '최버터', '(대리)', 540, 730, 0, alpha=fade(k - 3, int((HOLD + 0.5) * FPS) - 3))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE, '-filter_complex', f'[1:a]adelay={int(V_AT * 1000)}:all=1,apad[a]',
                '-map', '0:v', '-map', '[a]', '-t', str(n / FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep02/s4-butter-face.mp4'], check=True)
print('ep02/s4-butter-face.mp4', round(n / FPS, 2), 's')
