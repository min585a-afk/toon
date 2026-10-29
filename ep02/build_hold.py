"""EP02 멈춘 그림 컷 (목소리 정해지면 입 맞춤으로 바꿈): 그림 → 12fps 살짝 숨쉬기(1px) + 선택: 반짝이 · 째깍. 크레딧 0.
usage: python3 ep02/build_hold.py 그림.png 초 out.mp4 [--stars] [--tick 시작초]
"""
import subprocess, tempfile, wave, sys
import numpy as np, cv2
sys.path.insert(0, 'ep02'); from fx import star
FPS, W, H, SR = 24, 1080, 810, 44100
src, sec, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]; stars = '--stars' in sys.argv
img = cv2.resize(cv2.imread(src), (W, H), interpolation=cv2.INTER_AREA)
tmp = tempfile.mkdtemp(); n = int(sec * FPS)
for k in range(n):
    t = (k - k % 2) / FPS; fr = img.copy()
    if stars:
        for x, y, t0 in [(760, 90, 0.0), (330, 200, 0.4), (880, 360, 0.8)]:
            ph = ((t - t0) % 1.2) / 0.45
            if t >= t0 and ph < 1: fr = star(fr, x, y, int(40 * np.sin(ph * np.pi)))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, sec, 's')
