"""EP01 컷 1: 팀장 서류 내밀며 대사 시작(상반신) → 얼굴 쪽으로 빠르게 줌 → 컷 → 얼굴 클로즈업으로 대사 마무리. 크레딧 0.
같은 목소리로 두 그림을 각각 입 맞춤(tools/talk_mouth.py) → 앞은 상반신, 뒤는 얼굴로 이어붙임.
usage: python3 ep01b/build_c1.py  → ep01b/c1-boss-talk.mp4
"""
import subprocess, tempfile
import numpy as np
import cv2

FPS, W, H = 24, 1080, 810
VOICE, PRE, WIDE_SEC, ZOOM_F = 'voice/ep01/c1-boss.wav', 0.3, 0.95, 6   # 대사 0.3초에 시작 · 상반신 0.95초(끝 6프레임 줌) 뒤 얼굴로
FACE_IN_WIDE = (1150 / 2336 * W, 300 / 1744 * H)                           # 상반신 그림에서 얼굴 가운데 (1080x810)
tmp = tempfile.mkdtemp()
run = lambda *a: subprocess.run(['python3', 'tools/talk_mouth.py', *a, '--pre', str(PRE), '--post', '0.5'], check=True)
run('ep01b/c1-boss-papers.png', 'ep01b/talk/c1-open-raw.png', VOICE, f'{tmp}/wide.mp4', '--mouth', '1150,392', '--r', '55,34')
run('char/boss/talk/mouth-1-closed.png', 'char/boss/talk/mouth-2-open.png', VOICE, f'{tmp}/face.mp4', '--mouth', '1166,918', '--r', '85,62')


def read(p):
    cap = cv2.VideoCapture(p); out = []
    while True:
        ok, fr = cap.read()
        if not ok: return out
        out.append(fr)


wide, face = read(f'{tmp}/wide.mp4'), read(f'{tmp}/face.mp4'); n = min(len(wide), len(face)); cut = int(WIDE_SEC * FPS)
frames = []
for i in range(n):
    if i < cut:
        fr = wide[i]; k = i - (cut - ZOOM_F)
        if k >= 0:  # 얼굴 쪽으로 빠르게 줌 (1 → 2.2배)
            s = 1 + 1.2 * ((k + 1) / ZOOM_F) ** 2; cx, cy = FACE_IN_WIDE
            M = np.float32([[s, 0, cx - s * cx + (W / 2 - cx) * (s - 1) / s], [0, s, cy - s * cy + (H / 2 - cy) * (s - 1) / s]])
            fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        frames.append(fr)
    else:
        frames.append(face[i])
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/face.mp4', '-map', '0:v', '-map', '1:a',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep01b/c1-boss-talk.mp4'], check=True)
print('ep01b/c1-boss-talk.mp4', round(n / FPS, 1), 's')
