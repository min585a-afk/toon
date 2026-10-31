"""EP03 거울 컷 (혁 10/31: 멈춘 그림 말고 말하는 것처럼): 거울 그림 (입 벌림 ep03/s8-mirror.png · 입 다묾 s8-mirror-closed.png, 1cr)
→ 목소리 크기에 맞춰 거울 속 입만 열고 닫음 + 말할 때 머리 살짝 끄덕(1~2px) + 아주 천천히 다가감. 12fps. 크레딧 0.
usage: python3 ep03/build_mirror.py 목소리.wav 시작초 길이 → ep03/s8-mirror.mp4
"""
import subprocess, tempfile, shutil, sys
import numpy as np, cv2
FPS, W, H, SR = 24, 1080, 810, 44100
VOICE, V_AT, SEC = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
op = cv2.resize(cv2.imread('ep03/s8-mirror.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
cl = cv2.resize(cv2.imread('ep03/s8-mirror-closed.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
M = np.zeros((H, W), np.float32); M[274:312, 698:744] = 1; M = cv2.GaussianBlur(M, (0, 0), 3)[..., None]   # 거울 속 입 둘레만
cl = op * (1 - M) + cl * M                                       # 입만 바꾼 '다문 입' 그림 (나머지 픽셀은 원본 그대로)
vx = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', VOICE, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
env = np.array([np.sqrt((vx[i:i + 441] ** 2).mean()) for i in range(0, len(vx) - 441, 441)]); env /= env.max()
tmp = tempfile.mkdtemp(); n = int(SEC * FPS)
for k in range(n):
    t = (k - k % 2) / FPS; i = int((t - V_AT) * 100); e = env[max(0, i - 2):i + 3].max() if 0 <= i < len(env) else 0
    fr = op if e > 0.25 else cl
    z = 1 + 0.03 * t / SEC; dy = 1.5 * np.sin(t * 9) * (e > 0.1)
    A = cv2.getRotationMatrix2D((W * 0.7, H * 0.35), 0, z); A[1, 2] += dy
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', cv2.warpAffine(np.clip(fr, 0, 255).astype(np.uint8), A, (W, H), borderMode=cv2.BORDER_REPLICATE), [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep03/s8-mirror.mp4'], check=True)
shutil.rmtree(tmp, ignore_errors=True); print('ep03/s8-mirror.mp4', SEC, 's')
