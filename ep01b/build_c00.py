"""EP01 앞부분 (혁 10/27 순서): 귤이 타닥타닥(또각또각 멀리서 들려옴) → 팀장 걸어옴(H3) → 귤이 조금 더 치다가 눈만 위로 → (컷 1: 서류 내밀며 대사 → 얼굴 클로즈업).
귤이는 H3 영상 하나(ep01b/video/c00-gyul-type-look-h3.mp4: 타닥타닥 → 눈만 위로)를 앞뒤로 나눠 씀. 크레딧 0.
소리: 타닥타닥 = sfx/ep01/typing-norm.wav · 또각또각 = 한 걸음(sfx/ep01/heel-step.wav)을 걸음 박자에 맞춰 깔고 점점 크게.
usage: python3 ep01b/build_c00.py  → ep01b/c00-gyul-work.mp4 · ep01b/c0-boss-walk.mp4 · ep01b/c00b-gyul-look.mp4
"""
import subprocess, tempfile, wave
import numpy as np
import cv2, sys
sys.path.insert(0, 'tools'); from name_card import card

FPS, W, H, SR = 24, 1080, 810, 44100
T1, T2 = 0.8, 0.7                      # 첫 장면 훅(혁 10/27): 귤이 타닥타닥 T1 → 모니터 메모장 '출근 앤 퇴근 / 9 to 6' → 다시 귤이 T2
SCREEN = 'ep01b/c00s-screen.mp4'       # notepad_text.py → c00s-screen-raw.mp4 → tools/cel_look.py --ref ep01b/c00-gyul-work.png --amount 0.6
_cap = cv2.VideoCapture(SCREEN); SCREEN_N = int(_cap.get(cv2.CAP_PROP_FRAME_COUNT))
INTRO = 1.5                            # 1화 인물 소개: 첫 장면 멈춤 + '은서 (사원)' (혁 10/27)
GYUL_CARD = ('은서', '(사원)', 540, 95)   # 이름 · 괄호 · 위치(머리 위)
TYPE_SEC = INTRO + T1 + SCREEN_N / 24 + T2     # 이 구간 내내 타닥타닥 · 또각또각은 소개 끝나고 점점 가까이
HEELS_AT, STEP = 1.7, 0.36             # 또각또각 시작(소개 끝난 뒤) · 걸음 간격
WALK_FROM, SPEED, WALK_SEC = 0.5, 1.8, 1.6
LOOK_LAG, LOOK_HOLD = 0.25, 0.2         # 다시 귤이: 조금 더 치다가(0.8초) → 눈 위로(H3 끝 0.9초) → 멈춤(0.7초)
LOOK_SEC = LOOK_LAG + 0.9 + LOOK_HOLD


def video(p):
    cap = cv2.VideoCapture(p); f = cap.get(cv2.CAP_PROP_FPS) or 24; out = []
    while True:
        ok, fr = cap.read()
        if not ok: return out, f
        out.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))


def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)


def write(frames, audio, out):
    tmp = tempfile.mkdtemp()
    for i, fr in enumerate(frames): cv2.imwrite(f'{tmp}/{i:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
    a = np.zeros(int(len(frames) / FPS * SR), np.float32); a[:min(len(a), len(audio))] = audio[:len(a)]
    with wave.open(f'{tmp}/a.wav', 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav',
                    '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out], check=True)
    print(out, round(len(frames) / FPS, 2), 's')


# 소리 한 줄로 이어서 만든 뒤 컷마다 잘라 씀
typing, step = load('sfx/ep01/typing-norm.wav'), load('sfx/ep01/heel-step.wav')
total = TYPE_SEC + WALK_SEC + LOOK_SEC
heels = np.zeros(int(total * SR) + SR, np.float32)
arrive = TYPE_SEC + WALK_SEC + 0.3                                   # 마지막 걸음 (귤이 컷 들어가고 0.3초)
t = HEELS_AT; rng = np.random.default_rng(4)
while t <= arrive:
    v = 0.25 + 0.75 * min(1, (t - HEELS_AT) / (arrive - HEELS_AT))  # 멀리서 → 가까이
    i = int(t * SR); heels[i:i + len(step)] += step[:len(heels) - i] * v; t += STEP + rng.uniform(-0.02, 0.02)
type_track = np.zeros_like(heels)
def put_typing(a, b, vol):
    n = int((b - a) * SR); src = np.tile(typing, n // len(typing) + 2)[:n].copy()
    f = int(0.06 * SR); src[-f:] *= np.linspace(1, 0, f); type_track[int(a * SR):int(a * SR) + n] += src * vol
put_typing(0, TYPE_SEC, 0.9)
put_typing(TYPE_SEC + WALK_SEC, TYPE_SEC + WALK_SEC + LOOK_LAG, 0.9)
mix = (heels * 0.45 + type_track * 0.5)  # 또각또각 살짝 · 너무 강하지 않게 (혁 10/27)
cut = lambda a, b: mix[int(a * SR):int(b * SR)]

gv, gf = video('ep01b/video/c00-gyul-type-look-h3.mp4')
at = lambda sec: gv[min(len(gv) - 1, int(sec * gf))]
sv, _ = video(SCREEN)
intro = [card(at(0).copy(), *GYUL_CARD[:2], *GYUL_CARD[2:], k - 3) for k in range(int(INTRO * FPS))]   # 첫 그림 멈춤 + 소개
frames = intro + [at((k - k % 2) / FPS) for k in range(int(T1 * FPS))] + sv + [at(T1 + (k - k % 2) / FPS) for k in range(int(T2 * FPS))]
write(frames, cut(0, len(frames) / FPS), 'ep01b/c00-gyul-work.mp4')

bv, bf = video('ep01b/video/c0-boss-walk-h3.mp4')
write([bv[min(len(bv) - 1, int((WALK_FROM + (k - k % 2) / FPS * SPEED) * bf))] for k in range(int(WALK_SEC * FPS))],
      cut(TYPE_SEC, TYPE_SEC + WALK_SEC), 'ep01b/c0-boss-walk.mp4')

v0 = len(gv) / gf - 0.9 - LOOK_LAG                                    # H3 끝 0.9초가 눈 올리는 부분
write([at(v0 + (k - k % 2) / FPS) for k in range(int(LOOK_SEC * FPS))], cut(TYPE_SEC + WALK_SEC, total), 'ep01b/c00b-gyul-look.mp4')
