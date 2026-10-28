"""EP01 뒷부분 (혁 10/27): 은서 서류 받고 천사 웃음 + 하트 → 강서늘 뒤돌아 감 → 은서 '넵!!' → 돌변 빠직 → 강서늘 휙 돌아봄(멀리)
→ 바로 천사 얼굴 → 강서늘 다시 감 → 은서 타닥타닥 → 메모장 凸凸凸 (끝). 장면 먼저 (목소리는 나중에 · 자리만 비워둠). 크레딧 0.
usage: python3 ep01b/build_end.py  → ep01b/e1~e9-*.mp4
"""
import math, subprocess, tempfile, wave
import numpy as np
import cv2

FPS, W, H, SR = 24, 1080, 810, 44100
sz = lambda im: cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)


def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)


def write(frames, audio, out):
    tmp = tempfile.mkdtemp()
    for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
    a = np.zeros(int(len(frames) / FPS * SR), np.float32)
    if audio is not None: a[:min(len(a), len(audio))] = audio[:len(a)]
    with wave.open(f'{tmp}/a.wav', 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True); print(out, round(len(frames) / FPS, 2), 's')


def video(p, start=0, sec=None):
    cap = cv2.VideoCapture(p); f = cap.get(cv2.CAP_PROP_FPS) or 24; v = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        v.append(sz(fr))
    n = int((sec or len(v) / f - start) * FPS)
    return [v[min(len(v) - 1, int((start + (k - k % 2) / FPS) * f))] for k in range(n)]


def heart(fr, x, y, s, a=1.0):
    """분홍 하트 (셀 느낌: 단색 + 검정 테두리 + 흰 반짝)."""
    if s < 4: return fr
    lay = fr.copy(); pts = []
    for t in np.linspace(0, 2 * math.pi, 60):
        hx = 16 * math.sin(t) ** 3; hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x + hx * s / 16, y + hy * s / 16))
    p = np.array(pts, np.int32)
    cv2.fillPoly(lay, [p], (170, 120, 255), cv2.LINE_AA); cv2.polylines(lay, [p], True, (40, 25, 60), max(2, s // 8), cv2.LINE_AA)
    cv2.ellipse(lay, (int(x - s * 0.4), int(y - s * 0.25)), (max(1, s // 6), max(1, s // 10)), -30, 0, 360, (255, 255, 255), -1, cv2.LINE_AA)
    return cv2.addWeighted(lay, a, fr, 1 - a, 0)


heels_step, typing = load('sfx/ep01/heel-step.wav'), load('sfx/ep01/typing-norm.wav')
angel = sz(cv2.imread('char/gyul/exp/01-angel-clean.png'))

# e1 천사 웃음 + 하트 퐁퐁 (2.0초) — 대사 '그럴 리가요~!' 자리
HEARTS = [(250, 260, 46, 2), (840, 230, 54, 5), (180, 470, 36, 8), (900, 480, 40, 11), (320, 120, 30, 14)]
fr = []
for k in range(int(2.0 * FPS)):
    o = angel.copy(); kk = k - k % 2
    for x, y, s, st in HEARTS:
        t = kk - st
        if t < 0: continue
        sc = [0.4, 1.25, 1.0][min(2, t // 2)]; dy = -t * 3                    # 퐁 커졌다가 → 천천히 위로
        o = heart(o, x + int(4 * math.sin(t * 0.6)), y + dy, int(s * sc))
    fr.append(o)
write(fr, None, 'ep01b/e1-angel-hearts.mp4')

# e2 강서늘 뒤돌아 걸어 나감 (2.0초) — 대사 '잘 부탁해요~' 자리 · 또각또각 멀어짐
leave = sz(cv2.imread('ep01b/c3-boss-leave.png')); a = np.zeros(int(2.0 * SR), np.float32)
for i, t in enumerate(np.arange(0.2, 2.0, 0.42)): j = int(t * SR); a[j:j + len(heels_step)] += heels_step[:len(a) - j] * (0.4 - i * 0.06)
write([leave] * int(2.0 * FPS), a, 'ep01b/e2-boss-leave.mp4')

# e3 은서 '넵!!' (0.8초) — 천사 얼굴 그대로
write([angel] * int(0.8 * FPS), None, 'ep01b/e3-gyul-nep.mp4')

# e4 돌변 빠직 (이미 만든 컷) · e5 강서늘 휙 돌아봄 (이미 만든 컷) · e6 바로 천사 (이미 만든 컷, 1.2초만)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'ep01b/c6-angel.mp4', '-t', '1.2', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep01b/e6-angel-back.mp4'], check=True)

# e7 강서늘 다시 돌아서 감 (1.2초) — 뒷모습(멀리) · 또각또각 멀어짐
back = sz(cv2.imread('ep01b/c5-boss-back.png')); a = np.zeros(int(1.2 * SR), np.float32)
for i, t in enumerate(np.arange(0.15, 1.2, 0.42)): j = int(t * SR); a[j:j + len(heels_step)] += heels_step[:len(a) - j] * (0.3 - i * 0.08)
write([back] * int(1.2 * FPS), a, 'ep01b/e7-boss-away.mp4')

# e8 은서 앉아서 타닥타닥 (1.2초) — H3 타자 영상
a = np.tile(typing, 2)[:int(1.2 * SR)] * 0.5
write(video('ep01b/video/c00-gyul-type-look-h3.mp4', 0.5, 1.2), a, 'ep01b/e8-gyul-type.mp4')

# e9 메모장 凸凸凸 (끝) — tools/notepad_screen.py → cel_look
subprocess.run(['python3', 'tools/notepad_screen.py', 'ep01b/e9-notepad-raw.mp4'], check=True)
subprocess.run(['python3', 'tools/cel_look.py', 'ep01b/e9-notepad-raw.mp4', 'ep01b/e9-notepad-cel.mp4', '--ref', 'ep01b/c00-gyul-work.png', '--amount', '0.6'], check=True)
v = video('ep01b/e9-notepad-cel.mp4'); n = len(v)
a = np.tile(typing, 4)[:int((n / FPS - 1.2) * SR)] * 0.5
write(v, a, 'ep01b/e9-notepad.mp4')
