"""EP02 장면 1: 벽시계 5:55 · 초침이 실제로 째깍째깍 (코드 바늘) + 째깍 소리. 크레딧 0.
usage: python3 ep02/build_s1.py [시 분 초 길이 out] → ep02/s1-clock.mp4 (기본 5 55 0 3.4 · 똑 딱 똑 딱 네 번)
"""
import subprocess, tempfile, wave, sys
import numpy as np, cv2
sys.path.insert(0, 'ep02'); from clock import clock_at
FPS, W, H, SR = 24, 1080, 810, 44100
a = sys.argv[1:]; T0 = (int(a[0]) * 3600 + int(a[1]) * 60 + float(a[2])) if a else 5 * 3600 + 55 * 60.0
SEC = float(a[3]) if len(a) > 3 else 3.4; OUT = a[4] if len(a) > 4 else 'ep02/s1-clock.mp4'
SPEED = float(a[a.index('--speed') + 1]) if '--speed' in a else 1.0   # 시간 빨리 감기 (5:57 → 5:58 등)
FLASH = '--flash' in a                                          # 6:00 땡: 정각 순간 흰 번쩍 1장 + 땡! 쇠종 (10/30)
SIX = 6 * 3600                                                  # 6:00 (시계는 12시간 · 예전엔 18*3600 이라 땡 · 번쩍이 안 나왔음, 10/30)
tmp = tempfile.mkdtemp()
for k in range(int(SEC * FPS)):
    tc = T0 + k / FPS * SPEED
    fr = cv2.resize(clock_at(tc), (W, H), interpolation=cv2.INTER_AREA)   # 10/30 혁: 6시 땡 뒤에도 시계 계속 감
    if FLASH and abs(tc - SIX) < 1.5 / FPS * SPEED: fr[:] = 255
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
rd = lambda p: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
tks = [rd('sfx/anime/tik-syn.wav'), rd('sfx/anime/tok-syn.wav')]   # 그냥 똑딱똑딱 (혁 10/29): 똑 · 딱 번갈아
a = np.zeros(int(SEC * SR), np.float32)
step = max(1.0 / SPEED, 0.07)                                   # 빨리 감기면 째깍도 촤라락
for i, s in enumerate(np.arange((np.ceil(T0) - T0) / SPEED, SEC, step)):
    tk = tks[(int(np.ceil(T0)) + i) % 2]; j = int((s + 0.05) * SR); a[j:j + len(tk)] += tk[:len(a) - j] * (0.5 if SPEED == 1 else 0.35)   # +0.05초: 컷 맨 앞 소리는 이어 붙일 때 먹혀서 (10/30 5:57 · 5:59 첫 똑 안 들림)
if FLASH:
    ding = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/anime/ttaeng-syn.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
    j = int((SIX - T0) / SPEED * SR); a[j:j + len(ding)] += ding[:len(a) - j] * 0.6
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', OUT], check=True)
print(OUT, SEC, 's')

import shutil; shutil.rmtree(tmp, ignore_errors=True)   # 임시 프레임 지움 (10/30 디스크 꽉 참)
