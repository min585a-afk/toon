"""귤이 말하기 · 깜빡임 영상 — 정면 얼굴 눈 3 × 입 3 조합. 크레딧 0.
- 깜빡임: 2.5~5.5초마다 불규칙, 반 → 감음 → 반 (가끔 두 번 연속).
- 입: --audio 를 주면 소리 크기로 다문/반/벌린 자동 선택(옛날 애니처럼 초당 8번만 바뀜). 없으면 다문 입.
usage: python3 tools/talk.py out.mp4 [--set smile|neutral] [--audio voice.wav] [--seconds 6] [--seed 1]
"""
import argparse, os, subprocess, tempfile
import numpy as np
import cv2

V = 'char/gyul/talk/'
SETS = {
    'smile': {'mouth': [V + 'smile-mouth-1-closed.png', V + 'smile-mouth-2-half.png', V + 'smile-mouth-3-open.png'],
              'eyes': [V + 'eyes-1-open.png', V + 'eyes-2-half.png', V + 'smile-eyes-3-closed.png']},
    'neutral': {'mouth': [V + 'neutral-mouth-1-flat.png', V + 'neutral-mouth-2-half.png', V + 'neutral-mouth-3-open.png'],
                'eyes': [V + 'eyes-1-open.png', V + 'eyes-2-half.png', V + 'neutral-eyes-3-closed.png']},
}
EYES = [(888, 764), (1475, 782)]  # 기준 그림(2336x1744)에서 두 눈 가운데
FPS = 24


def eye_mask(h, w):
    m = np.zeros((h, w), np.float32)
    for c in EYES: cv2.ellipse(m, c, (190, 170), 0, 0, 360, 1, -1)
    return cv2.GaussianBlur(m, (0, 0), 9)[..., None]


def mouth_track(audio, n):
    """소리 크기 → 프레임별 입(0 다문 · 1 반 · 2 벌린), 3프레임(초당 8번)마다만 바뀜."""
    if not audio: return [0] * n
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', audio, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 16000 // 8; rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) if i < len(x) else 0 for i in range(0, n * 16000 // FPS + hop, hop)])
    top = np.percentile(rms[rms > 0], 95) if (rms > 0).any() else 1
    lv = np.where(rms < top * 0.12, 0, np.where(rms < top * 0.45, 1, 2))
    return [int(lv[min(len(lv) - 1, f // 3)]) for f in range(n)]


def blink_track(n, rng):
    e = [0] * n; t = int(rng.uniform(1.0, 2.5) * FPS)
    while t < n:
        for k, s in enumerate([1, 1, 2, 2, 1]):
            if t + k < n: e[t + k] = s
        if rng.random() < 0.15: t += 8; continue  # 두 번 연속 깜빡
        t += int(rng.uniform(2.5, 5.5) * FPS)
    return e


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--set', default='smile')
    ap.add_argument('--audio'); ap.add_argument('--seconds', type=float); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--size', default='1080x810'); a = ap.parse_args()
    s = SETS[a.set]; mouths = [cv2.imread(p) for p in s['mouth']]; eyes = [cv2.imread(p) for p in s['eyes']]
    h, w = mouths[0].shape[:2]; me = eye_mask(h, w)
    if a.seconds: secs = a.seconds
    elif a.audio:
        secs = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.audio], capture_output=True, text=True).stdout) + 0.5
    else: secs = 5
    n = int(secs * FPS); mt = mouth_track(a.audio, n); et = blink_track(n, np.random.default_rng(a.seed))
    W, H = map(int, a.size.split('x')); cache = {}
    tmp = tempfile.mkdtemp()
    for f in range(n):
        k = (et[f], mt[f])
        if k not in cache:
            fr = (mouths[k[1]] * (1 - me) + eyes[k[0]] * me).astype(np.uint8)
            cache[k] = cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{tmp}/{f:05d}.jpg', cache[k], [cv2.IMWRITE_JPEG_QUALITY, 93])
    cmd = ['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg']
    if a.audio: cmd += ['-i', a.audio, '-c:a', 'aac', '-shortest']
    subprocess.run(cmd + ['-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', a.out], check=True)
    print(a.out, round(secs, 1), 's')


if __name__ == '__main__':
    main()
