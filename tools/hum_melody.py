"""은서 흥얼거림을 계이름대로 (크레딧 0): 한 음 '음~' 목소리를 음마다 높이 바꿔 이어 붙임 (ffmpeg rubberband · 목소리 결 유지).
usage: python3 tools/hum_melody.py 한음.wav 시작초 끝초 out.wav BPM "C4:8 C4:8 ... E4:4"   (8 = 8분음표, 4 = 4분음표, R = 쉼표)
       python3 tools/hum_melody.py --conform 흥얼.wav out.wav BPM "C4:8 ..."   ← 자연 흥얼을 계이름 · 박자에 맞춤
       python3 tools/hum_melody.py --syllables 흠음절들.wav out.wav BPM "C4:8 ..."   ← 은서 '흠' 음절을 악보 그대로 (혁 10/28 이쪽)
"""
import sys, subprocess, tempfile, wave
import numpy as np
SR = 44100
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()


def f0(x, fmin=120, fmax=600):                       # 자기상관으로 기본 음높이
    x = x - x.mean(); c = np.correlate(x, x, 'full')[len(x) - 1:]; lo, hi = SR // fmax, SR // fmin
    return SR / (lo + np.argmax(c[lo:hi]))


def hz(n):
    name, octv = n[:-1], int(n[-1]); semi = NOTE[name[0]] + name.count('#') - name.count('b')
    return 440 * 2 ** ((semi + 12 * (octv + 1) - 69) / 12)


def shift(x, ratio):
    tmp = tempfile.mkdtemp()
    with wave.open(f'{tmp}/i.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{tmp}/i.wav', '-af', f'rubberband=pitch={ratio}:formant=preserved', f'{tmp}/o.wav'], check=True)
    return load(f'{tmp}/o.wav')


if __name__ == '__main__' and not sys.argv[1].startswith('--'):
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


def conform(src, out, bpm, seq):
    """자연스러운 흥얼(목소리 결 그대로)을 박자 칸마다 잘라 계이름 음으로 맞춤 + 박자마다 살짝 끊어 리듬 살림."""
    x = load(src); beat = 60 / bpm
    durs = [beat * 4 / int(t.split(':')[1]) for t in seq]; L = sum(durs)
    tmp = tempfile.mkdtemp()                         # 전체 길이를 박자 길이에 맞춰 늘이고 줄임 (음높이 그대로)
    with wave.open(f'{tmp}/i.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{tmp}/i.wav', '-af', f'rubberband=tempo={len(x) / SR / L}', f'{tmp}/s.wav'], check=True)
    x = load(f'{tmp}/s.wav')[:int(L * SR)]; x = np.pad(x, (0, max(0, int(L * SR) - len(x))))
    fs = [f0(x[int(t * SR):int(t * SR) + 4096]) for t in np.cumsum([0] + durs[:-1]) + 0.03]
    base = float(np.median(fs)); first = None; y = np.zeros(int(L * SR) + SR, np.float32); t = 0.0
    for tok, d, fv in zip(seq, durs, fs):
        n = tok.split(':')[0]; a, b = int(t * SR), int((t + d) * SR); pad = int(0.03 * SR)
        seg = x[max(0, a - pad):b + pad]
        if n != 'R':
            tg = hz(n)
            if first is None:
                while tg / base > 1.41: tg /= 2
                while tg / base < 0.71: tg *= 2
                first = tg / hz(n)
            tg = hz(n) * first; r = float(np.clip(tg / fv, 0.6, 1.7)); seg = shift(seg, r)[:len(seg)]
            env = np.ones(len(seg), np.float32); k = int(0.02 * SR); env[:k] = np.linspace(0.15, 1, k)
            tail = int(0.05 * SR); env[-tail - pad:-pad] = np.linspace(1, 0.25, tail); env[-pad:] = 0.25   # 박자 끝에서 살짝 끊김
            seg = seg * env
            s0 = max(0, a - pad); y[s0:s0 + len(seg)] += seg * np.hanning(len(seg)) ** 0.05
        t += d
    y = y[:int(L * SR)]; y = y / (np.abs(y).max() + 1e-9) * 0.8
    with wave.open(out, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(out, round(L, 2), 's · 흥얼 음', round(base), 'Hz → 박자 · 계이름 맞춤')


if __name__ == '__main__' and sys.argv[1] == '--conform':
    conform(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5].split())


def syllables(src, out, bpm, seq):
    """은서 '흠' 한 음절씩(목소리 그대로)을 악보 박자 자리에 놓고 음마다 정확한 계이름으로 맞춤 (혁 10/28: 악보 그대로 · 흠흠흠)."""
    x = load(src)[:-int(0.08 * SR)]; h = 441
    db = np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) + 1e-6) for i in range(0, len(x) - h, h)])
    on = db > -60; syl = []; i = 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]: j += 1
            if j - i >= 8: syl.append(x[i * h:j * h].copy())
            i = j
        else: i += 1
    short = sorted(syl, key=len)[:max(1, len(syl) - 2)]; long_ = sorted(syl, key=len)[-2:]   # 긴 '흐음~' 은 4분음표용
    beat = 60 / bpm; y = []; k = 0; tmp = tempfile.mkdtemp(); HR = np.random.default_rng(3)
    for tok in seq:
        n, d = tok.split(':'); dur = beat * 4 / int(d); seg = np.zeros(int(dur * SR * 0.5), np.float32)
        if n != 'R':
            s = (long_[k % len(long_)] if int(d) <= 4 else short[k % len(short)]); k += 1
            mid = s[len(s) // 3: len(s) // 3 + 2048] if len(s) > 2400 else s; r = float(np.clip(hz(n) / f0(mid, 190, 450), 0.6, 1.6))   # 은서 목소리 음역(190~450Hz)에서만 찾음 → 옥타브 착각 X
            r *= 2 ** (HR.normal(0, 6) / 1200)                               # 사람처럼: 음 아주 살짝 흔들림
            # 혁 10/28: 늘이기/rubberband 는 목소리가 2~3겹으로 들림 → 그냥 재생 속도로 음만 맞춤(겹침 X) · 음표 길이에서 깔끔히 자름
            src_i = np.arange(0, len(s) - 1, r); s = np.interp(src_i, np.arange(len(s)), s).astype(np.float32)
            n_len = int(dur * SR * (0.95 if int(d) <= 4 else 0.9)); s = s[:n_len]
            f = int(0.012 * SR); s[:f] *= np.linspace(0, 1, f); f = min(len(s) // 3, int(0.05 * SR)); s[-f:] *= np.linspace(1, 0, f)
            seg = s / (np.abs(s).max() + 1e-9) * (0.8 if int(d) <= 4 else 0.7) * HR.uniform(0.8, 1.0)
        y.append((dur, seg))
    L = sum(d for d, _ in y); out_a = np.zeros(int(L * SR) + SR, np.float32); t = 0.0
    for d, seg in y:                                                       # 사람처럼: 박자 살짝 흔들림
        i = max(0, int((t + abs(HR.normal(0, 0.008))) * SR)); out_a[i:i + len(seg)] += seg[:len(out_a) - i]; t += d   # 늦게만 살짝 → 앞 음과 안 겹침
    y = out_a[:int(L * SR) + int(0.15 * SR)]; y = y / (np.abs(y).max() + 1e-9) * 0.8
    with wave.open(out, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(out, round(len(y) / SR, 2), 's · 음절', len(syl), '개')


if __name__ == '__main__' and sys.argv[1] == '--syllables':
    syllables(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5].split())
