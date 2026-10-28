"""코드로 그린 화면(메모장 · 메신저 등)을 우리 셀 애니 그림체에 맞춤 — 장면 그림 색감 · 살짝 뭉개진 선 · 손그림처럼 미세하게 떨리는 선(3프레임마다) · 종이결 + 그레인. 크레딧 0.
usage: python3 tools/cel_look.py in.mp4 out.mp4 --ref 장면그림.png [--amount 0.55]
"""
import argparse, subprocess, tempfile
import numpy as np
import cv2

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--ref', required=True); ap.add_argument('--amount', type=float, default=0.55)
a = ap.parse_args()
ref = cv2.cvtColor(cv2.imread(a.ref), cv2.COLOR_BGR2LAB).astype(np.float32).reshape(-1, 3); rm, rs = ref.mean(0), ref.std(0)
cap = cv2.VideoCapture(a.src); fps = cap.get(cv2.CAP_PROP_FPS) or 24; W, H = int(cap.get(3)), int(cap.get(4))
rng = np.random.default_rng(7)
paper = cv2.GaussianBlur(rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32), (0, 0), 1.2); paper = cv2.resize(paper, (W, H))[..., None] * 5
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
first = None; tmp = tempfile.mkdtemp(); i = 0; wob = None
while True:
    ok, fr = cap.read()
    if not ok: break
    lab = cv2.cvtColor(fr, cv2.COLOR_BGR2LAB).astype(np.float32)
    if first is None: sm, ss = lab.reshape(-1, 3).mean(0), lab.reshape(-1, 3).std(0) + 1e-6; first = 1
    tgt = lab - sm + rm; tgt[..., 0] = (lab[..., 0] - sm[0]) * 0.9 + rm[0] * 0.25 + sm[0] * 0.75          # 색은 장면 쪽으로 · 밝기는 조금만
    lab = lab * (1 - a.amount) + tgt * a.amount
    o = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    if i % 3 == 0:                                                                                        # 손그림 떨림 (초당 8번 바뀜)
        n = cv2.resize(rng.normal(0, 1, (H // 60, W // 60, 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC); wob = n * 0.55
    o = cv2.remap(o, xx + wob[..., 0], yy + wob[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    o = cv2.GaussianBlur(o, (0, 0), 1.1).astype(np.float32)                                              # 옛날 TV 처럼 살짝 뭉개짐
    o = o + paper + rng.normal(0, 3.5, (H, W, 1))                                                         # 종이결 + 그레인
    cv2.imwrite(f'{tmp}/{i:05d}.jpg', np.clip(o, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93]); i += 1
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(fps), '-i', f'{tmp}/%05d.jpg', '-i', a.src, '-map', '0:v', '-map', '1:a?',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', a.out], check=True)
print(a.out)
