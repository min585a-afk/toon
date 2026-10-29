"""EP02 장면 2: 은서가 모니터 가까이 들여다봄 (얼굴 클로즈업) · 모니터 불빛 살짝 일렁 · 째깍 계속. 크레딧 0 (그림 ep02/s2-gyul-monitor.png 1cr).
usage: python3 ep02/build_s2.py → ep02/s2-gyul-monitor.mp4
"""
import subprocess, tempfile, wave
import numpy as np, cv2
FPS, W, H, SR, SEC, T0 = 24, 1080, 810, 44100, 1.6, 2.6      # 장면 1 에서 이어지는 초 (째깍 박자 맞춤)
img = cv2.resize(cv2.imread('ep02/s2-gyul-monitor.png'), (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W]; glow = np.clip(1 - np.hypot((xx - W * 0.85) / (W * 0.9), (yy - H) / (H * 0.9)), 0, 1)[..., None]
tmp = tempfile.mkdtemp()
for k in range(int(SEC * FPS)):
    f = 0.06 * glow * (0.5 + 0.5 * np.sin((k - k % 2) / FPS * 2 * np.pi * 1.3))          # 모니터 불빛 살짝 (12fps)
    fr = img * (1 - f) + np.float32([255, 220, 190]) * f
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', np.clip(fr, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
tk = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'sfx/anime/tick-syn.wav', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
a = np.zeros(int(SEC * SR), np.float32)
for s in np.arange(np.ceil(T0) - T0, SEC, 1.0):
    j = int(s * SR); a[j:j + len(tk)] += tk[:len(a) - j] * 0.45                            # 째깍 (조금 멀게)
with wave.open(f'{tmp}/a.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', f'{tmp}/a.wav', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', 'ep02/s2-gyul-monitor.mp4'], check=True)
print('ep02/s2-gyul-monitor.mp4', SEC, 's')
