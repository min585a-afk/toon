"""EP01 앞부분 (혁 10/27 순서) — 귤이는 H3 영상 하나(ep01b/video/c00-gyul-type-look-h3.mp4: 타닥타닥 → 눈만 위로)를 앞뒤로 나눠 씀: 귤이 타닥타닥(또각또각 들려옴) → 팀장 걸어옴(H3, 12fps · 1.6배) → 귤이 눈만 살짝 위로 → (컷 1: 서류 내밂 → 얼굴 클로즈업 대사). 크레딧 0.
usage: python3 ep01b/build_c00.py  → ep01b/c00-gyul-work.mp4 · ep01b/c0-boss-walk.mp4 · ep01b/c00b-gyul-look.mp4
"""
import subprocess, tempfile
import numpy as np
import cv2

FPS, W, H = 24, 1080, 810
base = cv2.imread('ep01b/c00-gyul-work.png'); SZ = (base.shape[1], base.shape[0])


def part(raw, center, axes, box, blur):
    """편집본에서 한 부분만 위치 맞춰 오려 붙임 (나머지는 원본 그대로)."""
    im = cv2.resize(cv2.imread(raw), SZ); x0, y0, x1, y1 = box
    g = lambda x: cv2.cvtColor(x[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    (dx, dy), _ = cv2.phaseCorrelate(g(base), g(im))
    im = cv2.warpAffine(im, np.float32([[1, 0, -dx], [0, 1, -dy]]), SZ, borderMode=cv2.BORDER_REPLICATE)
    m = np.zeros(base.shape[:2], np.float32); cv2.ellipse(m, center, axes, 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), blur)[..., None]
    return im, m


EYES, EYE_AX, EYE_BOX = (1155, 690), (250, 120), (835, 490, 1475, 890)   # 두 눈 + 눈썹 (2336x1744)
HANDS, HAND_AX, HAND_BOX = (1180, 1560), (330, 200), (850, 1380, 1550, 1744)
up, mu = part('ep01b/talk/c00-eyes-up-raw.png', EYES, EYE_AX, EYE_BOX, 18)
bl, mb = part('ep01b/talk/c00-blink-raw.png', EYES, EYE_AX, EYE_BOX, 18)
hd, mh = part('ep01b/talk/c00-hands-raw.png', HANDS, HAND_AX, HAND_BOX, 22)
cv2.imwrite('ep01b/c00-gyul-look.png', (base * (1 - mu) + up * mu).astype(np.uint8))
_cache = {}


def frame(eyes, hands):
    """eyes: 0 뜸 · 1 반 · 2 감음 · 3 위로 / hands: 0 · 1 (타닥타닥 두 자세)."""
    k = (eyes, hands)
    if k not in _cache:
        fr = base.astype(np.float32)
        if hands: fr = fr * (1 - mh) + hd * mh
        if eyes == 1: fr = fr * (1 - mb * 0.5) + bl * mb * 0.5
        if eyes == 2: fr = fr * (1 - mb) + bl * mb
        if eyes == 3: fr = fr * (1 - mu) + up * mu
        _cache[k] = cv2.resize(fr.astype(np.uint8), (W, H), interpolation=cv2.INTER_AREA)
    return _cache[k]


def typing(n, blink_at=None, seed=1, look_from=None):
    """타닥타닥: 손 자세 2개를 2~3프레임마다 번갈아 (불규칙) · blink_at 프레임에 깜빡 · look_from 부터 손 멈추고 눈 위로."""
    rng = np.random.default_rng(seed); out = []; h = 0; nxt = 0
    for f in range(n):
        if look_from is not None and f >= look_from: out.append(frame(3, 0)); continue
        if f >= nxt: h = 1 - h; nxt = f + int(rng.integers(2, 4))
        e = 0
        if blink_at is not None and 0 <= f - blink_at < 5: e = [1, 2, 2, 1, 0][f - blink_at]
        out.append(frame(e, h))
    return out


TYPE_SEC, LOOK_SEC, LOOK_LAG = 2.2, 1.95, 0.55   # 타닥타닥 컷 · 눈 올리는 컷 · 그 컷에서 계속 치다가 눈 올리기까지
HEELS_AT = 0.3                     # 또각또각 시작 (타닥타닥 컷 초반부터)
WALK_FROM, SPEED, WALK_SEC = 0.5, 1.6, 1.9


def write(frames, audio_filter, inputs, out, secs):
    tmp = tempfile.mkdtemp()
    for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
    cmd = ['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg'] + sum([['-i', x] for x in inputs], [])
    cmd += ['-filter_complex', audio_filter, '-map', '0:v', '-map', '[a]', '-t', str(secs), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', out]
    subprocess.run(cmd, check=True); print(out, secs, 's')


# 컷 00: 타닥타닥 + 또각또각 (멀리서 작게)
write(typing(int(TYPE_SEC * FPS), blink_at=int(1.3 * FPS)), f"[1:a]atrim=0:{TYPE_SEC},volume=0.9[t];[2:a]atrim=0:{TYPE_SEC - HEELS_AT},volume=0.3,adelay={int(HEELS_AT * 1000)}:all=1[h];"
      f"[t][h]amix=inputs=2:duration=longest:normalize=0,apad[a]", ['sfx/ep01/typing-norm.wav', 'sfx/ep01/heels-norm.wav'], 'ep01b/c00-gyul-work.mp4', TYPE_SEC)

# 컷 0: 팀장 걸어옴 — 1.6배 빠르게 · 12fps (2프레임씩)
cap = cv2.VideoCapture('ep01b/video/c0-boss-walk-h3.mp4'); sf = cap.get(cv2.CAP_PROP_FPS) or 24; vf = []
while True:
    ok, fr = cap.read()
    if not ok: break
    vf.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
n = int(WALK_SEC * FPS)
frames = [vf[min(len(vf) - 1, int((WALK_FROM + (k - k % 2) / FPS * SPEED) * sf))] for k in range(n)]
hs = TYPE_SEC - HEELS_AT
write(frames, f"[1:a]atrim={hs}:{hs + WALK_SEC},asetpts=PTS-STARTPTS,volume=0.6,apad[a]", ['sfx/ep01/heels-norm.wav'], 'ep01b/c0-boss-walk.mp4', WALK_SEC)

# 컷 00b: 계속 타닥타닥 (또각또각 가까이서 멈춤) → 잠깐 뒤 눈만 살짝 위로
write(typing(int(LOOK_SEC * FPS), seed=2, look_from=int(LOOK_LAG * FPS)),
      f"[1:a]atrim=0.3:{0.3 + LOOK_LAG},asetpts=PTS-STARTPTS,volume=0.8,afade=t=out:st={LOOK_LAG - 0.1}:d=0.1[t];"
      f"[2:a]atrim={hs + WALK_SEC}:{hs + WALK_SEC + 0.45},asetpts=PTS-STARTPTS,volume=0.7,afade=t=out:st=0.3:d=0.15[h];"
      f"[t][h]amix=inputs=2:duration=longest:normalize=0,apad[a]", ['sfx/ep01/typing-norm.wav', 'sfx/ep01/heels-norm.wav'], 'ep01b/c00b-gyul-look.mp4', LOOK_SEC)


# ── H3 영상으로 교체 (혁 10/27): 앞 = 타닥타닥, 끝 = 눈만 위로 → 마지막 장면에서 멈춤
cap = cv2.VideoCapture('ep01b/video/c00-gyul-type-look-h3.mp4'); gf = cap.get(cv2.CAP_PROP_FPS) or 24; gv = []
while True:
    ok, fr = cap.read()
    if not ok: break
    gv.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
at = lambda sec: gv[min(len(gv) - 1, int(sec * gf))]
TYPE_V = [at((k - k % 2) / FPS) for k in range(int(TYPE_SEC * FPS))]                       # 0 ~ 2.2초 (12fps)
LOOK_V0 = len(gv) / gf - 0.9                                                               # 끝 0.9초 = 손 멈추고 눈 위로
LOOK_V = [at(LOOK_V0 - LOOK_LAG + (k - k % 2) / FPS) for k in range(int(LOOK_SEC * FPS))]  # 조금 더 치다가 → 눈 위로 → 끝 장면 멈춤
write(TYPE_V, f"[1:a]atrim=0:{TYPE_SEC},volume=0.9[t];[2:a]atrim=0:{TYPE_SEC - HEELS_AT},volume=0.3,adelay={int(HEELS_AT * 1000)}:all=1[h];"
      f"[t][h]amix=inputs=2:duration=longest:normalize=0,apad[a]", ['sfx/ep01/typing-norm.wav', 'sfx/ep01/heels-norm.wav'], 'ep01b/c00-gyul-work.mp4', TYPE_SEC)
write(LOOK_V, f"[1:a]atrim=0.3:{0.3 + LOOK_LAG},asetpts=PTS-STARTPTS,volume=0.8,afade=t=out:st={LOOK_LAG - 0.1}:d=0.1[t];"
      f"[2:a]atrim={hs + WALK_SEC}:{hs + WALK_SEC + 0.45},asetpts=PTS-STARTPTS,volume=0.7,afade=t=out:st=0.3:d=0.15[h];"
      f"[t][h]amix=inputs=2:duration=longest:normalize=0,apad[a]", ['sfx/ep01/typing-norm.wav', 'sfx/ep01/heels-norm.wav'], 'ep01b/c00b-gyul-look.mp4', LOOK_SEC)
