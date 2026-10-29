"""EP02 장면 1: 벽시계 5:55 · 초침이 실제로 째깍째깍 (코드 바늘) + 째깍 소리. 크레딧 0.
usage: python3 ep02/build_s1.py → ep02/s1-clock.mp4
"""
import subprocess, tempfile, wave, sys
import numpy as np, cv2
sys.path.insert(0, 'ep02'); from clock import clock_at
FPS, W, H, SR, SEC, T0 = 24, 1080, 810, 44100, 2.6, 5 * 3600 + 55 * 60 + 0.0
tmp = tempfile.mkdtemp()
for k in range(int(SEC * FPS)):
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', cv2.resize(clock_at(T0 + k / FPS), (W, H), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 93])
tk = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/anime/tick-syn.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(SEC * SR), np.float32)
for s in range(int(SEC) + 1):
    j = int(s * SR); a[j:j + len(tk)] += tk[:len(a) - j] * 0.6
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s1-clock.mp4'], check=True)
print('ep02/s1-clock.mp4', SEC, 's')
