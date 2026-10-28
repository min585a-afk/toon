"""은서 흥얼거림을 계이름대로 (크레딧 0): 한 음 '음~' 목소리를 음마다 높이 바꿔 이어 붙임 (ffmpeg rubberband · 목소리 결 유지).
usage: python3 tools/hum_melody.py 한음.wav 시작초 끝초 out.wav BPM "C4:8 C4:8 ... E4:4"   (8 = 8분음표, 4 = 4분음표, R = 쉼표)
"""
import sys, subprocess, tempfile, wave
import numpy as np
SR = 44100
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()


def f0(x):                                           # 자기상관으로 기본 음높이
    x = x - x.mean(); c = np.correlate(x, x, 'full')[len(x) - 1:]; lo, hi = SR // 600, SR // 120
    return SR / (lo + np.argmax(c[lo:hi]))


def hz(n):
    name, octv = n[:-1], int(n[-1]); semi = NOTE[name[0]] + name.count('#') - name.count('b')
    return 440 * 2 ** ((semi + 12 * (octv + 1) - 69) / 12)


def shift(x, ratio):
    tmp = tempfile.mkdtemp()
    with wave.open(f'{tmp}/i.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{tmp}/i.wav', '-af', f'rubberband=pitch={ratio}:formant=preserved', f'{tmp}/o.wav'], check=True)
    return load(f'{tmp}/o.wav')


if __name__ == '__main__':
    src, a0, b0, out, bpm, seq = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], float(sys.argv[5]), sys.argv[6].split()
    x = load(src)[int(a0 * SR):int(b0 * SR)]; base = f0(x[len(x) // 4: len(x) // 4 + 4096])
    beat = 60 / bpm; y = []; cache = {}
    for tok in seq:
        n, d = tok.split(':'); dur = beat * 4 / int(d); seg = np.zeros(int(dur * SR), np.float32)
        if n != 'R':
            t = hz(n)
            while t / base > 1.5: t /= 2                 # 목소리 높이에 가까운 옥타브로
            while t / base < 0.75: t *= 2
            if n not in cache: cache[n] = shift(x, t / base)
            s = cache[n][:int(dur * 0.85 * SR)].copy(); k = int(0.015 * SR); s[:k] *= np.linspace(0, 1, k); k = int(0.05 * SR); s[-k:] *= np.linspace(1, 0, k)
            seg[:len(s)] = s
        y.append(seg)
    y = np.concatenate(y); y = y / (np.abs(y).max() + 1e-9) * 0.8
    with wave.open(out, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(out, round(len(y) / SR, 2), 's · 원래 음', round(base), 'Hz')
