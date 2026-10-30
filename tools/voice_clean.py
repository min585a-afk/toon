"""대사 wav 정리: 앞 무음 · 끝 딸깍(0.08초) 자르고, 끝 여운은 넉넉히(0.3초) 남겨서 페이드 · 말소리 -16dB · (선택) 빠르기.
usage: python3 tools/voice_clean.py 원본.wav out.wav [빠르기 1.15]
(10/30 혁: '닭발?' '글쎄요…' 끝이 짤림 → 예전엔 끝 여운을 0.09초만 남겨서 잘렸음)
"""
import subprocess, sys, wave
import numpy as np
SR = 44100
src, out = sys.argv[1], sys.argv[2]; speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
af = ['-af', f'atempo={speed}'] if speed != 1.0 else []
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, *af, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()
x = x[:-int(0.08 * SR / speed)]
e = np.array([np.sqrt((x[i:i + 441] ** 2).mean()) for i in range(0, len(x) - 441, 441)])
loud = e > np.percentile(e, 99) * 0.05; run = np.convolve(loud, np.ones(5), 'same') >= 5   # 5칸(0.05초) 이어진 소리만 말소리로 (10/30: 앞 딸깍 하나로 앞 무음 남던 것)
on = np.nonzero(run)[0] if run.any() else np.nonzero(loud)[0]
x = x[max(0, on[0] * 441 - 800):min(len(x), on[-1] * 441 + int(0.3 * SR))]
f = int(0.12 * SR); x[-f:] *= np.linspace(1, 0, f) ** 2
fr = np.array([np.sqrt((x[i:i + 2205] ** 2).mean()) for i in range(0, len(x) - 2205, 2205)]); act = fr[fr > fr.max() * 0.2]
x *= min(10 ** (-16 / 20) / np.sqrt((act ** 2).mean()), 0.95 / np.abs(x).max())
with wave.open(out, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
print(out, round(len(x) / SR, 2), 's')
