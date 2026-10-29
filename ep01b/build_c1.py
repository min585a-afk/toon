"""EP01 컷 1: 팀장 서류 내밀며 대사 시작(상반신) → 얼굴 쪽으로 빠르게 줌 → 컷 → 얼굴 클로즈업으로 대사 마무리. 크레딧 0.
같은 목소리로 두 그림을 각각 입 맞춤(tools/talk_mouth.py) → 앞은 상반신, 뒤는 얼굴로 이어붙임.
usage: python3 ep01b/build_c1.py  → ep01b/c1-boss-talk.mp4
"""
import subprocess, tempfile
import numpy as np
import cv2, sys
sys.path.insert(0, 'tools'); from name_card import card, fade
BOSS_CARD = ('강서늘', '(팀장)', 540, 730)   # 이름 · 괄호 · 위치(은서와 같은 자리)
INTRO_SEC = 2.1   # 이름 조금 더 오래 (컷 줄인 만큼)

FPS, W, H = 24, 1080, 810
VOICE, PRE, WIDE_SEC, ZOOM_F = 'voice/ep01/c1-boss.wav', 0.7, 2.2, 0   # 혁 10/29: 대사 전 멈춤 길어서 줄임 → 서류 들고 바로 대사   # 1화 소개: 대사 전 1.4초 멈춤 + 이름 자막   # 대사 0.4초에 시작 · 상반신 1.3초 → 바로 얼굴 클로즈업 컷 (줌 과정 X · 템포 살짝 천천히, 혁 10/27)
FACE_IN_WIDE = (1150, 300)                                                 # 상반신 원본(2336x1744)에서 얼굴 가운데
WW, WH = 2336, 1744
tmp = tempfile.mkdtemp()
run = lambda *a: subprocess.run(['python3', 'tools/talk_mouth.py', *a, '--pre', str(PRE), '--post', '0.6'], check=True)  # 대사 끝나고 0.6초 (템포)
run('ep01b/c1-boss-papers3-m.png', 'ep01b/talk/c1-papers3-open-m.png', VOICE, f'{tmp}/wide.mp4', '--mouth', '1118,552', '--r', '60,36', '--size', '2336x1744')  # 원본 크기 → 줌해도 안 흐림
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
        fr = wide[i]; k = i - (cut - ZOOM_F); s = 1.0
        if k >= 0: s = 1 + 1.2 * ((k + 1) / ZOOM_F) ** 2   # 얼굴 쪽으로 빠르게 줌 (1 → 2.2배)
        cx, cy = FACE_IN_WIDE; cw, ch = WW / s, WH / s
        x0 = min(max(cx - cw / 2 * (s - 1) / s - (cx - WW / 2) / s, 0), WW - cw) if s > 1 else 0
        y0 = min(max(cy - ch / 2, 0), WH - ch) if s > 1 else 0
        x0 = min(max(cx - cw / 2, 0), WW - cw) if s > 1 else 0
        # 원본 크기에서 잘라서 줄임 → 화질 유지
        im = cv2.resize(fr[int(y0):int(y0 + ch), int(x0):int(x0 + cw)], (W, H), interpolation=cv2.INTER_AREA)
        im = card(im, *BOSS_CARD[:2], *BOSS_CARD[2:], 0, alpha=fade(i - 2, int(INTRO_SEC * FPS) - 2))   # 이름 페이드 인·아웃
        frames.append(im)
    else:
        frames.append(face[i])
for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/face.mp4', '-map', '0:v', '-map', '1:a',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep01b/c1-boss-talk.mp4'], check=True)
print('ep01b/c1-boss-talk.mp4', round(n / FPS, 1), 's')
