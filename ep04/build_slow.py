"""EP04 H3 영상 컷: 옛날 TV 애니처럼 — 느리게(속도 배율) + 3프레임씩 같은 그림(8fps). 크레딧 0.
usage: python3 ep04/build_slow.py 영상.mp4 시작초 길이 속도 out.mp4   (예: 0.6 = 0.6배 느리게)
"""
import subprocess, tempfile, shutil, sys
import cv2
FPS, W, H, HOLD = 24, 1080, 810, 3
src, a0, sec, spd, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
cap = cv2.VideoCapture(src); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
tmp = tempfile.mkdtemp(); n = int(sec * FPS)
for k in range(n):
    t = (k - k % HOLD) / FPS * spd
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', v[min(len(v) - 1, int((a0 + t) * vf))], [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
shutil.rmtree(tmp, ignore_errors=True); print(out, sec, 's')
