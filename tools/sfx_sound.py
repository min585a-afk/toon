"""만화 효과음 합성 (크레딧 0). 컷 영상에 바로 얹어 씀.
- sparkle: 천사 웃음 '반짝반짝' — 맑은 종소리 올라가는 아르페지오 2번 + 반짝이는 쉬머
- bloom: 꽃 피어날 때마다 한 음씩 올라가는 종소리
- rage: 정색 '빠직' — 쿵(낮은 충격) + 화르륵(불 솟는 바람) + 타닥 불티
- whoosh: '휙' 바람 가르는 소리 · ting: 안경 번쩍 '띵'
usage: python3 tools/sfx_sound.py sparkle out.wav   |   import sfx_sound as ss; ss.sparkle()
"""
import sys, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(9)


def env(n, a=0.005, d=8.0):
    t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t * d)


def bell(f, dur=0.9, d=6.0, amp=0.3):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(w * np.sin(2 * np.pi * f * r * t) for r, w in [(1, 1), (2.76, 0.45), (5.4, 0.25), (8.93, 0.12)])  # 종소리 배음
    return (s * env(n, 0.002, d) * amp).astype(np.float32)


def mix(parts, dur):
    o = np.zeros(int(dur * SR), np.float32)
    for at, s in parts:
        i = int(at * SR); o[i:i + len(s)] += s[:len(o) - i]
    return o


def lowpass(x, k): return np.convolve(x, np.ones(k) / k, 'same').astype(np.float32)


def sparkle():
    """반짝반짝: 펜타토닉 위로 빠르게 2번 + 고음 쉬머."""
    notes = [1568, 1760, 2093, 2349, 2637, 3136]  # G6 A6 C7 D7 E7 G7
    parts = []
    for burst, base in [(0.0, 0), (0.32, 1)]:
        for k, f in enumerate(notes[base:base + 5]): parts.append((burst + k * 0.045, bell(f, 0.8, 7, 0.16)))
    n = int(1.0 * SR); t = np.arange(n) / SR
    shimmer = rng.normal(0, 1, n) * (np.sin(2 * np.pi * 23 * t) > 0.6) * np.exp(-t * 4) * 0.05  # 반짝반짝 노이즈
    shimmer = shimmer - lowpass(shimmer, 6)  # 고음만
    parts.append((0.0, shimmer.astype(np.float32)))
    return np.clip(mix(parts, 1.3), -1, 1)


def bloom(times):
    """꽃 피어날 때마다 종소리 한 음씩 올라가며 + 반짝 쉬머 (times = 초)."""
    notes = [1568, 1760, 2093, 2349, 2637, 3136, 3520, 4186]
    parts = [(t, bell(notes[i % len(notes)], 0.8, 6, 0.16)) for i, t in enumerate(times)]
    n = int(1.2 * SR); tt = np.arange(n) / SR
    sh = rng.normal(0, 1, n) * (np.sin(2 * np.pi * 19 * tt) > 0.5) * np.exp(-tt * 3) * 0.05
    parts.append((times[0], (sh - lowpass(sh, 6)).astype(np.float32)))
    return np.clip(mix(parts, max(times) + 1.3), -1, 1)


def rage(dur=1.6):
    """빠직: 첫 순간 쿵 + 불 화르륵 솟음 + 타닥 불티."""
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 90 * np.exp(-t * 4) + 38; boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.9
    crack = rng.normal(0, 1, int(0.05 * SR)) * env(int(0.05 * SR), 0.001, 60) * 0.7  # 빠직! 날카로운 첫 소리
    m = int(dur * SR); tt = np.arange(m) / SR
    roar = lowpass(rng.normal(0, 1, m), 30) * 3.0
    roar = roar * np.minimum(tt / 0.15, 1) * (0.8 + 0.2 * np.sin(2 * np.pi * 5 * tt)) * np.clip((dur - tt) / 0.3, 0, 1) * 0.45
    parts = [(0, boom.astype(np.float32)), (0, crack.astype(np.float32)), (0.03, roar.astype(np.float32))]
    for _ in range(14):  # 불티 타닥
        c = rng.normal(0, 1, 300) * env(300, 0.0005, 300) * rng.uniform(0.2, 0.5)
        parts.append((rng.uniform(0.1, dur - 0.1), c.astype(np.float32)))
    return np.clip(mix(parts, dur), -1, 1)


def whoosh(dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    return (lowpass(rng.normal(0, 1, n), 12) * np.sin(np.pi * t / t[-1]) ** 2 * 0.9).astype(np.float32)


def ting():
    n = int(0.5 * SR); t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 2600 * t) + 0.5 * np.sin(2 * np.pi * 3900 * t)) * np.exp(-t * 9) * 0.25).astype(np.float32)


def save(path, x):
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    save(sys.argv[2], globals()[sys.argv[1]]()); print(sys.argv[2])
