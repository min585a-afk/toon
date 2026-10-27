"""아무 그림이나 말하게 — 기준 그림 + 입 벌린 편집본에서 입 부분만 오려 붙이고, 목소리 크기로 다문/반/벌린 입 (초당 8번). 크레딧 0.
usage: python3 tools/talk_mouth.py 기준.png 입벌림.png 목소리.wav out.mp4 --mouth X,Y [--r 50,32] [--pre 0.3] [--post 0.5]
(X,Y = 기준 그림 픽셀에서 입 가운데)
"""
import argparse, subprocess, tempfile
import numpy as np
import cv2

FPS = 24


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('open'); ap.add_argument('audio'); ap.add_argument('out')
    ap.add_argument('--mouth', required=True); ap.add_argument('--r', default='50,32'); ap.add_argument('--pre', type=float, default=0.3); ap.add_argument('--post', type=float, default=0.5)
    ap.add_argument('--size', default='1080x810'); a = ap.parse_args()
    base = cv2.imread(a.base); op = cv2.imread(a.open); op = cv2.resize(op, (base.shape[1], base.shape[0]))
    mx, my = map(int, a.mouth.split(',')); rx, ry = map(int, a.r.split(','))
    # 입 주변으로 위치 맞춤 (편집본이 살짝 밀려 있을 수 있음)
    x0, y0, x1, y1 = mx - rx * 4, my - ry * 4, mx + rx * 4, my + ry * 4
    g = lambda im: cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    (dx, dy), _ = cv2.phaseCorrelate(g(base), g(op))
    op = cv2.warpAffine(op, np.float32([[1, 0, -dx], [0, 1, -dy]]), (base.shape[1], base.shape[0]), borderMode=cv2.BORDER_REPLICATE)
    m = np.zeros(base.shape[:2], np.float32); cv2.ellipse(m, (mx, my), (rx, ry), 0, 0, 360, 1, -1); m = cv2.GaussianBlur(m, (0, 0), max(3, ry / 4))[..., None]
    opened = (base * (1 - m) + op * m).astype(np.uint8)
    half = (base * (1 - m * 0.5) + op * m * 0.5).astype(np.uint8)
    W, H = map(int, a.size.split('x')); imgs = [cv2.resize(x, (W, H), interpolation=cv2.INTER_AREA) for x in (base, half, opened)]
    tmp = tempfile.mkdtemp()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', a.audio, '-af', f'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,adelay={int(a.pre*1000)}:all=1,apad=pad_dur={a.post}',
                    '-ac', '1', '-ar', '44100', f'{tmp}/a.wav'], check=True)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{tmp}/a.wav', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; n = int(len(x) / 16000 * FPS)
    hop = 16000 // 8; rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) if i < len(x) else 0 for i in range(0, len(x) + hop, hop)])
    top = np.percentile(rms[rms > 0], 95) if (rms > 0).any() else 1
    lv = np.where(rms < top * 0.12, 0, np.where(rms < top * 0.45, 1, 2))
    for f in range(n): cv2.imwrite(f'{tmp}/{f:05d}.jpg', imgs[int(lv[min(len(lv) - 1, f // 3)])], [cv2.IMWRITE_JPEG_QUALITY, 93])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', a.out], check=True)
    print(a.out, round(n / FPS, 1), 's · 입 위치 보정', round(dx, 1), round(dy, 1))


if __name__ == '__main__':
    main()
