"""EP01 컷 '왜요? 어려운가요?': 팀장 클로즈업 — 안경 하얗게 번쩍(눈 가림) → (H3 있으면: 손으로 안경 고쳐 씀) → 대사. 크레딧 0.
usage: python3 ep01b/build_c3why.py  → ep01b/c3-boss-why.mp4
"""
import os, subprocess, tempfile
import numpy as np
import cv2

FPS, W, H = 24, 1080, 810
GLARE_SEC = 0.7
H3 = 'ep01b/video/c3-boss-glasses-h3.mp4'          # 안경 번쩍 → 고쳐 씀 (있으면 씀)
tmp = tempfile.mkdtemp()
subprocess.run(['python3', 'tools/talk_mouth.py', 'char/boss/talk/mouth-1-closed.png', 'char/boss/talk/mouth-2-open.png', 'voice/ep01/c3-boss-why.wav',
                f'{tmp}/talk.mp4', '--mouth', '1166,918', '--r', '85,62', '--pre', '0.15', '--post', '1.0'], check=True)
glare = cv2.resize(cv2.imread('ep01b/c3-boss-glare.png'), (W, H), interpolation=cv2.INTER_AREA)
frames = [glare] * int(GLARE_SEC * FPS)
if os.path.exists(H3):
    cap = cv2.VideoCapture(H3); f = cap.get(cv2.CAP_PROP_FPS) or 24; v = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
    frames += [v[min(len(v) - 1, int((k - k % 2) / FPS * f))] for k in range(int(len(v) / f * FPS))]
pre = len(frames)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{tmp}/talk.mp4', f'{tmp}/t_%05d.jpg'], check=True)
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/f_{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
n = len([x for x in os.listdir(tmp) if x.startswith('t_')])
for k in range(n): os.rename(f'{tmp}/t_{k + 1:05d}.jpg', f'{tmp}/f_{pre + k:05d}.jpg')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/f_%05d.jpg', '-i', f'{tmp}/talk.mp4',
                '-filter_complex', f'[1:a]adelay={int(pre / FPS * 1000)}:all=1,apad[a]', '-map', '0:v', '-map', '[a]', '-t', str((pre + n) / FPS),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/c3-boss-why.mp4'], check=True)
print('ep01b/c3-boss-why.mp4', round((pre + n) / FPS, 1), 's')
