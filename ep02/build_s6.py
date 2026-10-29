"""EP02 장면 6: 최버터 H3 영상(ep02/video/s6-butter-gesture-h3.mp4, 10cr) — 머리 쓸어넘기며 윙크 "끝나고 저녁 어때~?"
입 움직이는 구간(4~47 프레임)만 대사 길이에 맞춰 돌리고, 다문 입 웃음(47~57)으로 끝. 12fps. 크레딧 0.
usage: python3 ep02/build_s6.py [목소리.wav] → ep02/s6-butter-gesture.mp4
"""
import subprocess, tempfile, sys
import cv2
FPS, W, H = 24, 1080, 810
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'voice/ep02/butter-lines/s6b-2-use.wav'   # 혁 10/29: 대사 '끝나고 저녁 어때~?' 로 바꿈
M0, M1, END = 4, 47, 58                                          # 입 벌림 · 입 다묾 · 끝 프레임
VLEN = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VOICE], capture_output=True, text=True).stdout)
cap = cv2.VideoCapture('ep02/video/s6-butter-gesture-h3.mp4'); vf = cap.get(cv2.CAP_PROP_FPS); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
def src(t):
    s0 = M0 / vf
    if t < s0: return int(t * vf)
    if t < s0 + VLEN: return int(M0 + (t - s0) / VLEN * (M1 - M0))
    return int(M1 + (t - s0 - VLEN) * vf)
n = int((M0 + (END - M1)) / vf * FPS + VLEN * FPS); tmp = tempfile.mkdtemp()
for k in range(n):
    t = (k - k % 2) / FPS; cv2.imwrite(f'{tmp}/{k:05d}.jpg', v[min(len(v) - 1, src(t))], [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE, '-filter_complex', f'[1:a]adelay={int(M0 / vf * 1000)}:all=1,apad[a]',
                '-map', '0:v', '-map', '[a]', '-t', str(n / FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep02/s6-butter-gesture.mp4'], check=True)
print('ep02/s6-butter-gesture.mp4', round(n / FPS, 2), 's')
