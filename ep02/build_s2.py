"""EP02 장면 2: 은서가 모니터 가까이 들여다봄 (얼굴 클로즈업) · 모니터 불빛 살짝 일렁 · 째깍 계속. 크레딧 0 (그림 ep02/s2-gyul-monitor.png 1cr).
usage: python3 ep02/build_s2.py → ep02/s2-gyul-monitor.mp4
"""
import subprocess, tempfile, wave
import numpy as np, cv2, sys
FPS, W, H, SR, SEC, T0 = 24, 1080, 810, 44100, 3.4, 2.6     # 혁 10/29: '퇴근각 재는 중' 2초 더      # 장면 1 에서 이어지는 초 (째깍 박자 맞춤)
# 혁 10/29: 좌우 반전 · 눈 깜빡 · 모니터 빛 비추는 효과
op = cv2.resize(cv2.imread('ep02/s2-v2.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)   # 혁 10/29: 새로 그림 (검정 가디건 · 흰 티 · 빨간 리본, 반전 X)
cl = cv2.resize(cv2.imread('ep02/s2-v2-blink.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)   # 감은 눈 (편집 1cr · 눈 자리만 합침)
# 혁 10/29: 복장은 코드로 칠하면 모니터 빛 닿은 곳 분홍이 남아서 → 검정 가디건으로 다시 편집한 그림(1cr) 씀
BLINKS = (0.6, 1.9, 2.8)                                          # 깜빡이는 시각
def eye(t):                                                    # 0 = 뜸 · 1 = 감음 (0.17초)
    for b in BLINKS:
        d = t - b
        if 0 <= d < 2 / 12: return 1.0                            # 반쯤 섞으면 눈이 겹쳐 보임 → 바로 감았다 뜸
    return 0.0
yy, xx = np.mgrid[0:H, 0:W]
glow = np.clip(1 - np.hypot((xx - W * 0.5) / (W * 1.1), (yy - H * 1.05) / (H * 0.85)), 0, 1)[..., None] ** 1.3   # 아래 모니터 쪽
tmp = tempfile.mkdtemp(); rng = np.random.default_rng(5)
for k in range(int(SEC * FPS)):
    t = (k - k % 2) / FPS; e = eye(t)
    fr = op * (1 - e) + cl * e
    flick = 0.55 + 0.3 * np.sin(t * 2 * np.pi * 2.1) + 0.15 * rng.random()                 # 화면 바뀌며 빛이 깜빡깜빡
    band = np.exp(-(((yy - (t * 0.9 % 1.0) * H * 1.4 + H * 0.2) / (H * 0.12)) ** 2))[..., None]   # 화면 글자 스크롤 빛줄기 (아래→위 천천히)
    f = glow * (0.16 * flick + 0.10 * band)
    fr = fr * (1 - f) + np.float32([255, 225, 185]) * f            # 차가운 하늘빛 (BGR)
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(fr, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
a = np.zeros(int(SEC * SR), np.float32)                        # 시계 소리 없음 (혁 10/29: 장면 2 는 조용히 '흐음…'만)
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s2-gyul-monitor.mp4'], check=True)
print('ep02/s2-gyul-monitor.mp4', SEC, 's')
