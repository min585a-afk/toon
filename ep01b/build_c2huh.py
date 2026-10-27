"""EP01 컷 '네?..': 귤이 H3 영상(눈 위로 본 채 → 시무룩해지며 '네…' 입 움직임) + 목소리 + 물음표가 위에서 떨어짐. 크레딧 0.
usage: python3 ep01b/build_c2huh.py  → ep01b/c2-gyul-huh.mp4
"""
import subprocess, sys, tempfile
import cv2
sys.path.insert(0, 'tools'); from qmark import qmark_drop

FPS, W, H = 24, 1080, 810
V, V_FROM = 'ep01b/video/c2-gyul-ne-h3.mp4', 2.6       # H3 에서 쓸 구간 시작 (입 움직이기 직전)
VOICE_AT, SEC = 0.35, 2.4                              # 목소리 · 물음표 시작 · 컷 길이
cap = cv2.VideoCapture(V); f = cap.get(cv2.CAP_PROP_FPS) or 24; v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
tmp = tempfile.mkdtemp(); n = int(SEC * FPS); q = int(VOICE_AT * FPS)
for k in range(n):
    fr = v[min(len(v) - 1, int((V_FROM + (k - k % 2) / FPS) * f))].copy()   # 12fps
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', qmark_drop(fr, 815, 290, 200, k - q), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', 'voice/ep01/c2-gyul-ne.wav',
                '-filter_complex', f'[1:a]adelay={int(VOICE_AT * 1000)}:all=1,apad[a]', '-map', '0:v', '-map', '[a]', '-t', str(SEC),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/c2-gyul-huh.mp4'], check=True)
print('ep01b/c2-gyul-huh.mp4', SEC, 's')
