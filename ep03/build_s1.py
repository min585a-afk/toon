"""EP03 장면 1: 팔짱 -ㅅ- 흐음… → 두 손 번쩍 "아니야!" → 몸 내밀고 말함. 크레딧 0 (영상은 H3 두 개 20cr).
  A ep03/video/s1a-think-handsup-h3.mp4 (흐음 → 손 번쩍 키 그림 ep03/s1-handsup.png 에 도착)
  B ep03/video/s1b-handsup-talk-h3.mp4 (손 번쩍 → 말하는 얼굴) — A 끝 = B 시작 같은 그림이라 이어짐
A 61~65 프레임(팔 풀 때 손 뭉개진 2~3장, 혁 10/30)은 빼고 바로 손 번쩍 + 그 순간 확 다가왔다 돌아오는 줌. 12fps.
usage: python3 ep03/build_s1.py → ep03/s1-think-talk.mp4
"""
import subprocess, tempfile, shutil
import numpy as np, cv2
FPS, W, H = 24, 1080, 810
def load(p):
    cap = cv2.VideoCapture(p); v = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
    return v
A, B = load('ep03/video/s1a-think-handsup-h3.mp4'), load('ep03/video/s1b-handsup-talk-h3.mp4')
seq = [A[i] for i in range(0, 61)] + [A[i] for i in range(66, 82)] + [B[i] for i in range(0, 76)]
POP = 61; tmp = tempfile.mkdtemp()
for k in range(len(seq)):
    fr = seq[k - k % 2]; a = k - POP
    if 0 <= a < 8: fr = cv2.warpAffine(fr, cv2.getRotationMatrix2D((W * 0.55, H * 0.42), 0, 1 + 0.1 * (1 - a / 8) ** 2), (W, H), borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep03/s1-think-talk.mp4'], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print('ep03/s1-think-talk.mp4', round(len(seq) / FPS, 2), 's · 손 번쩍', round(POP / FPS, 2), 's')
