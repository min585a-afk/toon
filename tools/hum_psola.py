"""자연 흥얼(은서 목소리)을 계이름 · 박자 정확히 (TD-PSOLA: 성대 떨림 한 주기씩 다시 배치 → 음 딱 고정, 목소리 결 그대로, 겹침/화음 X). 크레딧 0.
usage: python3 tools/hum_psola.py 흥얼.wav out.wav BPM "C4:8 C4:8 C4:8 C4:8 C4:4" [반복 2] [쉼 박]
예) python3 tools/hum_psola.py voice/ep01b/hum-neon-phraseA.wav voice/ep01b/hum-neon4.wav 130 "C4:8 C4:8 C4:8 C4:8 C4:4" 2 1   (니온 앤 비온드 ×2, 혁 10/29)
음만 맞춤(흥얼 그대로): python3 tools/hum_psola.py --retune in.wav out.wav C4 0.7
"""
import sys, wave
import numpy as np
sys.path.insert(0, 'tools')
from hum_melody import load, f0, hz, SR


def notes_of(x, n):                                  # 소리 골짜기(깊게 꺼진 곳) n-1 개로 n 개 음으로 나눔
    h = 220; e = np.array([np.sqrt((x[i:i + h] ** 2).mean()) for i in range(0, len(x) - h, h)])
    db = 20 * np.log10(np.convolve(e, np.ones(3) / 3, 'same') + 1e-6); on = np.nonzero(db > db.max() - 30)[0]; a, b = on[0], on[-1]
    w = int(0.08 * SR / h); cand = []
    for i in range(a + 2, b - 2):
        if db[i] == db[max(a, i - w):min(b, i + w) + 1].min():
            prom = min(db[max(a, i - w):i].max(), db[i + 1:min(b, i + w) + 1].max()) - db[i]
            if prom > 4: cand.append((prom, i))
    mins = sorted(i for _, i in sorted(cand, reverse=True)[:n - 1])
    cuts = [a] + mins + [b]; return [(cuts[k] * h, cuts[k + 1] * h) for k in range(len(cuts) - 1)]


def marks(s, fmin=190, fmax=450):                    # 주기마다 표시 (봉우리) — 주기 따라가며 근처 봉우리
    if len(s) < 2048: return np.array([], int)
    m = [int(np.argmax(s[:int(SR / fmin)]))]
    while True:
        i = m[-1]; w = s[max(0, i - 1024):i + 1024]
        T = SR / f0(w, fmin, fmax) if len(w) >= 1024 else SR / 260
        c = int(i + T); r = int(T * 0.2)
        if c + r >= len(s): break
        m.append(c - r + int(np.argmax(s[c - r:c + r])))
    return np.array(m)


def psola(s, f_target, dur, keep=0.6, vib=0.0, scoop=40):
    """keep = 원래 음 흔들림을 얼마나 남길지(0 = 기계처럼 딱 · 1 = 원래대로). vib = 비브라토 cent. scoop = 음 시작에 아래서 올라오는 cent (사람처럼)."""
    pm = marks(s)
    if len(pm) < 4: return np.zeros(int(dur * SR), np.float32)
    per = np.diff(pm).astype(float); fn = SR / per; med = np.median(fn)
    out = np.zeros(int(dur * SR) + 2048, np.float32); ts = 0.0; L = dur * SR
    while ts < L:
        ta = pm[0] + (pm[-1] - pm[0]) * ts / L; j = int(np.clip(np.searchsorted(pm, ta), 1, len(pm) - 2))
        tt = ts / SR; cents = 1200 * np.log2(fn[min(j, len(fn) - 1)] / med) * keep          # 원래 흔들림 일부
        cents += -scoop * np.exp(-tt / 0.04)                                                  # 시작에 살짝 아래서
        cents += vib * np.sin(2 * np.pi * 5.5 * tt) * min(1, max(0, (tt - 0.12) / 0.15))      # 긴 음 끝쪽 비브라토
        T = SR / (f_target * 2 ** (cents / 1200))
        P = int((pm[j + 1] - pm[j - 1]) / 2); A, B = pm[j] - P, pm[j] + P
        if A >= 0 and B <= len(s):
            g = s[A:B] * np.hanning(B - A); c = int(ts) - P
            if c >= 0: out[c:c + len(g)] += g[:len(out) - c]
        ts += T
    out = out[:int(L)]; f = int(0.015 * SR); out[:f] *= np.linspace(0, 1, f); f = int(0.04 * SR); out[-f:] *= np.linspace(1, 0, f)
    return out


if __name__ == '__main__' and sys.argv[1] != '--retune':
    src, dst, bpm, seq = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4].split()
    rep = int(sys.argv[5]) if len(sys.argv) > 5 else 1; rest = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
    KEEP = float(sys.argv[7]) if len(sys.argv) > 7 else 0.6; VIB = float(sys.argv[8]) if len(sys.argv) > 8 else 25   # 원래 흔들림 남김 · 비브라토(cent)
    x = load(src); beat = 60 / bpm; parts = notes_of(x, len(seq)); ph = []
    for (a, b), tok in zip(parts, seq):
        n, d = tok.split(':'); dur = beat * 4 / int(d)
        seg = psola(x[a:b], hz(n), dur * (0.92 if int(d) >= 8 else 0.9), keep=KEEP, vib=0 if int(d) >= 8 else VIB)
        ph += [seg / (np.abs(seg).max() + 1e-9) * (0.85 if int(d) >= 8 else 0.8), np.zeros(int(dur * SR) - len(seg), np.float32)]
    ph = np.concatenate(ph); y = np.concatenate(sum([[ph, np.zeros(int(rest * beat * SR), np.float32)] for _ in range(rep)], [])[:-1])
    y = y / np.abs(y).max() * 0.8
    with wave.open(dst, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(dst, round(len(y) / SR, 2), 's')


def retune(src, dst, note='C4', keep=0.7):
    """흥얼 그대로(박자 · 세기 · 길이 안 건드림) 음 높이만 note 로. 소리 덩어리마다 PSOLA, 사이 조용한 곳은 원본 그대로."""
    x = load(src); y = x.copy(); h = 441
    db = np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) + 1e-6) for i in range(0, len(x) - h, h)])
    on = db > db.max() - 30; i = 0; regs = []
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]: j += 1
            if j - i >= 4: regs.append((i * h, j * h))
            i = j
        else: i += 1
    for a, b in regs:
        seg = psola(x[a:b], hz(note), (b - a) / SR, keep=keep, vib=0, scoop=0)
        f = int(0.006 * SR); w = np.ones(b - a, np.float32); w[:f] = np.linspace(0, 1, f); w[-f:] = np.linspace(1, 0, f)
        g = np.sqrt((x[a:b] ** 2).mean() / ((seg ** 2).mean() + 1e-12))           # 세기 원래대로
        y[a:b] = x[a:b] * (1 - w) + seg[:b - a] * g * w
    with wave.open(dst, 'w') as wv: wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    print(dst, '덩어리', len(regs))


if __name__ == '__main__' and sys.argv[1] == '--retune':
    retune(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'C4', float(sys.argv[5]) if len(sys.argv) > 5 else 0.7)
