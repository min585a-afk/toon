"""EP01 뒷부분: 장면 '은서 꽃밭'(장면 1 끝부분 꽃밭+반짝만 반복, '헷 ><') · 장면 '다시 걸어나감'(돌아본 고개 → 다시 앞으로 → 걸어감). 크레딧 0.
usage: python3 ep01b/build_e5.py  → ep01b/e5-angel-loop.mp4 · ep01b/e6-boss-away.mp4
"""
import subprocess, tempfile, wave
import numpy as np
import cv2

FPS, W, H, SR = 24, 1080, 810, 44100


def video(p):
    cap = cv2.VideoCapture(p); out = []
    while True:
        ok, fr = cap.read()
        if not ok: return out
        out.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))


def write(frames, audio, out):
    tmp = tempfile.mkdtemp()
    for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
    a = np.zeros(int(len(frames) / FPS * SR), np.float32)
    if audio is not None: a[:min(len(a), len(audio))] = audio[:len(a)]
    with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
    print(out, round(len(frames) / FPS, 2), 's')


# 은서 꽃밭: 장면 1 에서 꽃이 다 핀 뒤(반짝 깜빡) 구간만 반복 → 1.6초
e1 = video('ep01b/e1-angel-bloom.mp4'); tail = e1[-int(1.0 * FPS):]
loop = (tail + tail[::-1]) * 3
write(loop[:int(1.6 * FPS)], None, 'ep01b/e5-angel-loop.mp4')

# 다시 걸어나감: 돌아본 고개 → 옆얼굴 → 반쯤 → 뒷모습 (휙 돌아섬) → H3 2.0초부터 남은 걸음
sz = lambda p: cv2.resize(cv2.imread(p), (W, H), interpolation=cv2.INTER_AREA)
look, side, half, back = [sz(f'ep01b/e5-boss-far-{n}.png' if n == 'back' else f'ep01b/e5-boss-far-{n}-fix.png') for n in ['look', 'side', 'half', 'back']]
cap = cv2.VideoCapture('ep01b/video/e6-boss-away-h3.mp4'); f = cap.get(cv2.CAP_PROP_FPS) or 24; v = video('ep01b/video/e6-boss-away-h3.mp4')   # 멈춘 자리에서 이어 걷는 H3
walk = [v[min(len(v) - 1, int((k - k % 2) / FPS * 1.2 * f))] for k in range(int(2.0 * FPS))]                       # 2초 더 걸어감 (혁 10/28)
frames = [look] * 4 + [side] + [half] + [back] * 3 + walk
step = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/ep01/heel-step.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(len(frames) / FPS * SR) + SR, np.float32)
for i, t in enumerate(np.arange(9 / FPS, len(frames) / FPS, 0.4)): j = int(t * SR); a[j:j + len(step)] += step[:len(a) - j] * 0.3 * (1 - i * 0.2)
write(frames, a, 'ep01b/e6-boss-away.mp4')
