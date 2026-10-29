"""EP02 H3 영상 컷 공통: 영상 → 12fps(2프레임씩) · 원하는 구간만 · 무음(목소리는 나중에). 크레딧 0.
usage: python3 ep02/build_video_cut.py 영상.mp4 시작초 길이 out.mp4
"""
import subprocess, tempfile, sys
import cv2
FPS, W, H = 24, 1080, 810
src, a0, sec, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
cap = cv2.VideoCapture(src); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
tmp = tempfile.mkdtemp(); n = int(sec * FPS)
for k in range(n): cv2.imwrite(f'{tmp}/{k:05d}.jpg', v[min(len(v) - 1, int((a0 + (k - k % 2) / FPS) * vf))], [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
print(out, sec, 's')
