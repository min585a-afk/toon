"""EP01 끝: 은서 타닥타닥(또각또각 멀어지며 사라짐) → 모니터 메모장 凸 연타 → 끝. 크레딧 0.
usage: python3 ep01b/build_e7.py  → ep01b/e7-gyul-type.mp4 · ep01b/e8-notepad.mp4
"""
import subprocess, tempfile, wave
import numpy as np
import cv2

FPS, W, H, SR = 24, 1080, 810, 44100
load = lambda p: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
typing, step = load('sfx/ep01/typing-norm.wav'), load('sfx/ep01/heel-step.wav')


def video(p):
    cap = cv2.VideoCapture(p); f = cap.get(cv2.CAP_PROP_FPS) or 24; out = []
    while True:
        ok, fr = cap.read()
        if not ok: return out, f
        out.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))


def write(frames, a, out):
    tmp = tempfile.mkdtemp()
    for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
    b = np.zeros(int(len(frames) / FPS * SR), np.float32); b[:min(len(b), len(a))] = a[:len(b)]
    with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(b, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
    print(out, round(len(frames) / FPS, 2), 's')


# 은서 타닥타닥 1.4초 + 또각또각 멀어짐 (점점 작게 → 사라짐)
SEC = 1.4; gv, gf = video('ep01b/video/c00-gyul-type-look-h3.mp4')
frames = [gv[min(len(gv) - 1, int((0.3 + (k - k % 2) / FPS) * gf))] for k in range(int(SEC * FPS))]
# 화난 얼굴(혁 10/28: 너무 평온) — 얼굴만 프레임마다 위치 맞춰 덮음 · 손은 H3 그대로
base = cv2.resize(cv2.imread('ep01b/e7-type-base.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
angry = cv2.resize(cv2.imread('ep01b/e7-type-shadow.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)   # 그림자로 눈 가림 (혁 10/28)
# 핏대: 그림에서 떼어내서(지우고) 프레임마다 부드럽게 커졌다 작아졌다 다시 그림
_hsv = cv2.cvtColor(angry.astype(np.uint8), cv2.COLOR_BGR2HSV); _box = (560, 200, 680, 310)
_red = np.zeros((H, W), np.uint8); bx0, by0, bx1, by1 = _box
_r = _hsv[by0:by1, bx0:bx1]; _red[by0:by1, bx0:bx1] = (((_r[..., 0] < 10) | (_r[..., 0] > 170)) & (_r[..., 1] > 120) & (_r[..., 2] > 120)).astype(np.uint8)
_n, _l, _st, _ = cv2.connectedComponentsWithStats(_red[by0:by1, bx0:bx1])          # 귀(분홍)는 빼고 핏대 덩어리만 (혁 10/28: 귀가 같이 움직임)
_red[by0:by1, bx0:bx1] = np.isin(_l, [i for i in range(1, _n) if _st[i, 4] >= 50 and _st[i, 0] < 90]).astype(np.uint8)
_red = cv2.dilate(_red, np.ones((7, 7), np.uint8)); ys, xs = np.nonzero(_red); VC = (int(xs.mean()), int(ys.mean()))
vx0, vy0, vx1, vy1 = xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7
VEIN = angry[vy0:vy1, vx0:vx1].copy(); VEIN_A = cv2.GaussianBlur(_red[vy0:vy1, vx0:vx1].astype(np.float32), (0, 0), 1)[..., None]
angry = cv2.inpaint(angry.astype(np.uint8), _red, 5, cv2.INPAINT_TELEA).astype(np.float32)   # 핏대 없는 얼굴
# 눈 반짝(흰 점)도 지움 → 검정 그림자만 (혁 10/28)
_w = np.zeros((H, W), np.uint8); _w[260:380, 440:640] = (angry[260:380, 440:640].mean(-1) > 110).astype(np.uint8)
_sh = np.zeros((H, W), np.uint8); _sh[260:380, 440:640] = 1; _w &= cv2.erode((cv2.GaussianBlur(angry, (0, 0), 6).mean(-1) < 90).astype(np.uint8), np.ones((3, 3), np.uint8)) & _sh
angry = cv2.inpaint(angry.astype(np.uint8), cv2.dilate(_w, np.ones((5, 5), np.uint8)), 5, cv2.INPAINT_TELEA).astype(np.float32)
def vein(fr, k):
    s = 1.5 * (1.0 + 0.4 * (0.5 + 0.5 * np.sin(k / FPS * 2 * np.pi * 2.5)) ** 2)           # 더 크게 · 확 부풀었다 줄어듦 (초당 2.5번)
    ang = 8 * np.sin(k / FPS * 2 * np.pi * 5)                                              # 살짝 들썩
    sp = cv2.resize(VEIN, None, fx=s, fy=s, interpolation=cv2.INTER_LINEAR); sa = cv2.resize(VEIN_A, None, fx=s, fy=s)[..., None]
    R = cv2.getRotationMatrix2D((sp.shape[1] / 2, sp.shape[0] / 2), ang, 1); sp = cv2.warpAffine(sp, R, (sp.shape[1], sp.shape[0])); sa = cv2.warpAffine(sa, R, (sa.shape[1], sa.shape[0]))[..., None]
    h, w = sp.shape[:2]; x0, y0 = VC[0] - w // 2, VC[1] - h // 2
    fr[y0:y0 + h, x0:x0 + w] = fr[y0:y0 + h, x0:x0 + w] * (1 - sa) + sp * sa; return fr
# 앞머리 사이로 비치던 이마도 그림자로 꽉 채움 (혁 10/28)
_sm = np.zeros((H, W), np.float32); cv2.ellipse(_sm, (535, 300), (100, 95), 0, 180, 360, 1, -1); _sm[300:330, 435:635] = 1
_sm = cv2.GaussianBlur(_sm, (0, 0), 9)[..., None]; _dark = np.float32([22, 14, 18])
angry = angry * (1 - _sm) + np.minimum(angry, _dark + 0.25 * angry) * _sm
# 덮는 곳 = 그림자로 바뀐 곳 + 입만 (귀 · 머리 끝은 H3 그대로 → 귀 흔들림 X, 혁 10/28)
_d = (np.abs(angry - base).mean(-1) > 30).astype(np.uint8); _d = cv2.morphologyEx(_d, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
fm = np.zeros((H, W), np.uint8); fm[150:440, 440:640] = _d[150:440, 440:640]; cv2.ellipse(fm, (535, 400), (45, 25), 0, 0, 360, 1, -1); fm = np.maximum(fm, (_sm[..., 0] > 0.05).astype(np.uint8))
fm = cv2.GaussianBlur(cv2.dilate(fm, np.ones((15, 15), np.uint8)).astype(np.float32), (0, 0), 5)[..., None]
FX, FY = 540, 300
g = lambda im: cv2.cvtColor(im[FY - 160:FY + 160, FX - 200:FX + 200].astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
out = []
for fr in frames:
    (dx, dy), _ = cv2.phaseCorrelate(g(base), g(fr.astype(np.float32)))
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    a2 = cv2.warpAffine(angry, M, (W, H), borderMode=cv2.BORDER_REPLICATE); m2 = cv2.warpAffine(fm, M, (W, H))[..., None]
    o = fr * (1 - m2) + a2 * m2; o = vein(o, len(out))
    out.append(np.clip(o, 0, 255).astype(np.uint8))
frames = out
a = np.tile(typing, 2)[:int(SEC * SR)] * 0.5
for i, t in enumerate([0.05, 0.45, 0.85]): j = int(t * SR); a[j:j + len(step)] += step[:len(a) - j] * (0.22 - i * 0.07)
write(frames, a, 'ep01b/e7-gyul-type.mp4')

# 메모장 凸 연타 (tools/notepad_screen.py → cel_look) + 빠른 타닥타닥 · 끝 멈춤
subprocess.run(['python3', 'tools/notepad_screen.py', 'ep01b/e8-notepad-raw.mp4'], check=True)
subprocess.run(['python3', 'tools/cel_look.py', 'ep01b/e8-notepad-raw.mp4', 'ep01b/e8-notepad-cel.mp4', '--ref', 'ep01b/c00-gyul-work.png', '--amount', '0.6'], check=True)
nv, _ = video('ep01b/e8-notepad-cel.mp4'); n = len(nv); type_end = n - 30
a = np.tile(typing, 6)[:int(n / FPS * SR)].copy() * 0.55; a[int(type_end / FPS * SR):] = 0
write(nv, a, 'ep01b/e8-notepad.mp4')
