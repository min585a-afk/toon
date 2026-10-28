"""EP01 프레임에 딱 맞춘 만화 효과음 (크레딧 0). 애니메이션 프레임 타이밍(tools/qmark.py qmark_drop 등)에 맞춰 합성.
usage: python3 ep01b/build_sfx.py  → sfx/ep01/q-drop.wav · sulk.wav · paper.wav
"""
import wave
import numpy as np

SR, FPS = 44100, 24
rng = np.random.default_rng(3)


def save(p, x):
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1)
    with wave.open(p, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
    print(p, round(len(x) / SR, 2), 's')


def tone(f0, f1, dur, wave_='sine', vib=0.0, a=0.005, d=None):
    n = int(dur * SR); t = np.arange(n) / SR; f = f0 * (f1 / f0) ** (t / dur)       # 지수로 미끄러지는 음
    if vib: f = f * (1 + vib * np.sin(2 * np.pi * 14 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) if wave_ == 'sine' else (2 / np.pi) * np.arcsin(np.sin(ph))        # sine · triangle
    env = np.minimum(t / a, 1) * (np.exp(-t * d) if d else np.ones(n))
    return s * env


def at(buf, sec, s, vol=1.0):
    i = int(sec * SR); buf[i:i + len(s)] += s[:len(buf) - i] * vol


# 1) 물음표: 떨어지는 동안(0~6프레임) 휘익 내려가는 휘슬 → 착지(6프레임) 퐁! → 통(8→10프레임) 폭 → 흔들(12→14) 톡
q = np.zeros(int(1.0 * SR))
fall = tone(1900, 950, 6 / FPS, vib=0.02); fall *= np.linspace(0.6, 1, len(fall)); at(q, 0, fall, 0.45)
at(q, 6 / FPS, tone(820, 420, 0.16, d=22), 1.0); at(q, 6 / FPS, tone(1640, 840, 0.1, d=35), 0.4)
at(q, 10 / FPS, tone(900, 520, 0.11, d=30), 0.55)
at(q, 14 / FPS, tone(1100, 700, 0.07, d=45), 0.3)
save('sfx/ep01/q-drop.wav', q)

# 2) 시무룩: 작고 낮게 '뿌우~' 내려감 (삼각파 · 0.4초)
s = tone(520, 330, 0.42, 'triangle', vib=0.015, a=0.02); s *= np.exp(-np.linspace(0, 2.2, len(s)))
save('sfx/ep01/sulk.wav', s)

# 3) 서류: 짧은 종이 '사락' (거른 노이즈 두 번)
n = int(0.22 * SR); t = np.arange(n) / SR; x = rng.normal(0, 1, n)
x = x - np.convolve(x, np.ones(6) / 6, 'same'); x = np.convolve(x, np.ones(3) / 3, 'same')        # 높은 사각 소리만
env = np.exp(-((t - 0.04) / 0.03) ** 2) + 0.6 * np.exp(-((t - 0.13) / 0.04) ** 2)
save('sfx/ep01/paper.wav', x * env)

# 4) 등장 '둥!': 낮게 떨어지는 북소리 + 짧은 타격음 + 살짝 울림
n = int(0.9 * SR); t = np.arange(n) / SR
f = 95 * np.exp(-t * 3) + 45; body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
hit = rng.normal(0, 1, n) * np.exp(-t * 60) * 0.5
tail = np.convolve(body, np.exp(-np.arange(int(0.05 * SR)) / (0.02 * SR)), 'same') * 0.002
save('sfx/ep01/dung.wav', body + hit + tail)
