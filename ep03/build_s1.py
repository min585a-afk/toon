"""EP03 장면 1: H3 영상(ep03/video/s1-think-talk-h3.mp4, 10cr) — 팔짱 -ㅅ- 흐음… → 눈 번쩍 말 터짐.
영상 52~58 프레임(팔 풀 때 손이 뭉개진 중간 그림) 대신 깨끗하게 다시 그린 '두 손 번쩍' 키 그림(ep03/s1-handsup.png, 1cr)을 0.33초 넣음 (혁 10/30: 손 드는 동작은 좋은데 뭉개짐만 문제) + 그 순간 확 다가왔다 돌아오는 줌. 12fps. 크레딧 0.
usage: python3 ep03/build_s1.py → ep03/s1-think-talk.mp4
"""
import subprocess, tempfile, shutil
import numpy as np, cv2
FPS, W, H = 24, 1080, 810
CUT_A, CUT_B = 50, 60                                            # 여기까지 흐음 · 여기부터 말함
cap = cv2.VideoCapture('ep03/video/s1-think-talk-h3.mp4'); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
KEY = cv2.resize(cv2.imread('ep03/s1-handsup.png'), (W, H), interpolation=cv2.INTER_AREA); HOLD = 8
v.append(KEY); seq = list(range(0, CUT_A + 1)) + [len(v) - 1] * HOLD + list(range(CUT_B, len(v) - 1)); tmp = tempfile.mkdtemp()
for k in range(len(seq)):
    j = seq[k - k % 2]; fr = v[j]; a = k - (CUT_A + 1)
    if 0 <= a < 8:                                               # 번쩍: 1.1배로 확 → 4프레임 동안 돌아옴
        z = 1 + 0.1 * (1 - a / 8) ** 2; fr = cv2.warpAffine(fr, cv2.getRotationMatrix2D((W * 0.55, H * 0.42), 0, z), (W, H), borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep03/s1-think-talk.mp4'], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print('ep03/s1-think-talk.mp4', round(len(seq) / FPS, 2), 's · 말 시작', round((CUT_A + 1) / FPS, 2), 's')
