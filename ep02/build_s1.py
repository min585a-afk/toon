"""EP02 장면 1: 벽시계 5:55 · 초침이 실제로 째깍째깍 (코드 바늘) + 째깍 소리. 크레딧 0.
usage: python3 ep02/build_s1.py [시 분 초 길이 out] → ep02/s1-clock.mp4 (기본 5 55 0 2.6)
"""
import subprocess, tempfile, wave, sys
import numpy as np, cv2
sys.path.insert(0, 'ep02'); from clock import clock_at
FPS, W, H, SR = 24, 1080, 810, 44100
a = sys.argv[1:]; T0 = (int(a[0]) * 3600 + int(a[1]) * 60 + float(a[2])) if a else 5 * 3600 + 55 * 60.0
SEC = float(a[3]) if len(a) > 3 else 2.6; OUT = a[4] if len(a) > 4 else 'ep02/s1-clock.mp4'
FLASH = '--flash' in a                                          # 6:00 땡: 정각 순간 흰 번쩍 1장 + 띠링
tmp = tempfile.mkdtemp()
for k in range(int(SEC * FPS)):
    fr = cv2.resize(clock_at(min(T0 + k / FPS, 18 * 3600) if FLASH else T0 + k / FPS), (W, H), interpolation=cv2.INTER_AREA)
    if FLASH and abs(T0 + k / FPS - 18 * 3600) < 1.5 / FPS: fr[:] = 255
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
tk = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/anime/tick-syn.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(SEC * SR), np.float32)
for s in np.arange(np.ceil(T0) - T0, SEC, 1.0):
    j = int(s * SR); a[j:j + len(tk)] += tk[:len(a) - j] * 0.6
if FLASH:
    ding = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/anime/tiring-syn.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
    j = int((18 * 3600 - T0) * SR); a[j:j + len(ding)] += ding[:len(a) - j] * 0.8
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', OUT], check=True)
print(OUT, SEC, 's')
