"""옛날 TV 애니 효과음 합성 (크레딧 0): 키랑(안경 번쩍) · 하테나(물음표 슬라이드 휘슬) · 고고고(분노 오라) · 키라키라(반짝 종소리) · 뽀용(헷) · 삐킷(빠직) · 띠링(끝).
usage: python3 tools/anime_sfx.py [이름 ...]  → sfx/anime/<이름>-syn.wav (없으면 전부)
"""
import sys, wave
import numpy as np
SR = 44100
rng = np.random.default_rng(7)
t_ = lambda d: np.arange(int(d * SR)) / SR


def verb(x, sec=0.8, mix=0.35):                     # 간단한 방 울림 (지수 감쇠 노이즈와 컨볼루션)
    ir = rng.normal(0, 1, int(sec * SR)) * np.exp(-np.arange(int(sec * SR)) / (sec * SR / 6)); ir /= np.abs(ir).sum() / 8
    y = np.convolve(x, ir)[:len(x) + len(ir)] * mix; y[:len(x)] += x; return y


def bell(f, d, partials=((1, 1), (2.76, .5), (5.4, .25), (8.9, .12))):
    t = t_(d); return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * (3 + r * 2)) for r, a in partials)


def glide(f0, f1, d, curve=2.0, vib=0.0):
    t = t_(d); p = (t / d) ** curve; f = f0 * (f1 / f0) ** p * (1 + vib * np.sin(2 * np.pi * 7 * t)); return np.sin(2 * np.pi * np.cumsum(f) / SR)


def kiran():                                         # 키라~앙: 빠르게 올라가는 반짝 + 높은 종 + 쉬머
    up = glide(1800, 5200, 0.12, 1.5) * np.linspace(0.2, 1, int(0.12 * SR))
    b = bell(3136, 1.2) + 0.6 * bell(4699, 1.2) * np.sin(2 * np.pi * 9 * t_(1.2)) ** 2
    x = np.concatenate([up, np.zeros(0)]); y = np.zeros(int(1.4 * SR)); y[:len(x)] += x * 0.5; y[int(0.1 * SR):int(0.1 * SR) + len(b)] += b * 0.6
    return verb(y, 1.0, 0.4)


def hatena():                                        # 뽀잉? 슬라이드 휘슬 위로 + 끝에 살짝 꺾임
    a = glide(700, 1500, 0.35, 0.8, vib=0.015) * np.hanning(int(0.35 * SR) * 2)[int(0.35 * SR):] ** 0.2
    b = glide(1500, 1700, 0.15, 1, vib=0.03) * np.linspace(1, 0, int(0.15 * SR))
    x = np.concatenate([a * np.linspace(0.5, 1, len(a)), b]); x += 0.25 * np.sign(x) * np.abs(x) ** 3   # 살짝 휘슬 배음
    return verb(x * 0.7, 0.5, 0.25)


def gogogo():                                        # 고고고: 낮은 웅웅 + 떨림 + 불길 쉭
    t = t_(2.6); env = np.minimum(1, t / 0.4) * np.minimum(1, (2.6 - t) / 0.5)
    saw = sum(np.sin(2 * np.pi * 46 * k * t + rng.uniform(0, 6)) / k for k in range(1, 8))
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)
    n = rng.normal(0, 1, len(t)); lo = np.convolve(n, np.ones(60) / 60, 'same')
    hi = n - np.convolve(n, np.ones(8) / 8, 'same')
    fire = hi * (0.15 + 0.35 * np.abs(np.sin(2 * np.pi * 3.5 * t))) * np.linspace(0.3, 1, len(t))
    return verb((saw * 0.35 * trem + lo * 3 + fire * 0.6) * env, 0.6, 0.3)


def kirakira():                                      # 키라키라: 펜타토닉 종소리가 위로 쏟아짐
    notes = [2093, 2349, 2637, 3136, 3520, 4186, 4699, 5274, 6272]; y = np.zeros(int(2.2 * SR))
    for i in range(16):
        f = notes[min(len(notes) - 1, i * len(notes) // 16 + rng.integers(0, 2))]; s = int((0.05 + i * 0.075 + rng.uniform(0, .02)) * SR)
        b = bell(f, 0.9) * (0.35 + 0.3 * rng.random()); y[s:s + len(b)] += b[:len(y) - s]
    return verb(y, 1.2, 0.45)


def poyon():                                         # 뽀용: 동글 통통 튀는 소리 (헷 ><)
    t = t_(0.45); f = 380 + 260 * np.exp(-t * 9) * np.cos(2 * np.pi * 7 * t); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    return verb(x * 0.8, 0.3, 0.2)


def pikit():                                         # 삐킷: 빠직 핏대 순간
    a = glide(2400, 3400, 0.05, 1) * 0.6; b = np.sign(np.sin(2 * np.pi * 2900 * t_(0.09))) * np.exp(-t_(0.09) * 30) * 0.25
    return verb(np.concatenate([a, np.zeros(int(0.03 * SR)), b, np.zeros(int(0.03 * SR)), b * 0.7]), 0.3, 0.2)


def tiring():                                        # 끝 띠링
    y = np.zeros(int(1.6 * SR)); b1, b2 = bell(1568, 1.4), bell(2093, 1.4); y[:len(b1)] += b1 * 0.5; s = int(0.16 * SR); y[s:s + len(b2)] += b2[:len(y) - s] * 0.6
    return verb(y, 1.0, 0.35)


ALL = dict(kiran=kiran, hatena=hatena, gogogo=gogogo, kirakira=kirakira, poyon=poyon, pikit=pikit, tiring=tiring)
if __name__ == '__main__':
    for name in sys.argv[1:] or ALL:
        x = ALL[name](); x = x / (np.abs(x).max() + 1e-9) * 0.85
        with wave.open(f'sfx/anime/{name}-syn.wav', 'w') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
        print(f'sfx/anime/{name}-syn.wav', round(len(x) / SR, 2), 's')
