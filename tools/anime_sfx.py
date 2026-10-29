"""옛날 TV 애니 효과음 합성 (크레딧 0): 키랑(안경 번쩍) · 하테나(물음표 슬라이드 휘슬) · 고고고(분노 오라) · 키라키라(반짝 종소리) · 뽀용(헷) · 삐킷(빠직) · 띠링(끝) · 휙(돌아봄) · 띠용(멘붕) · 쭈뼛(싸늘) · 긴장(정적 밑).
잘 나온 건 sfx/lib/ 에 확정 이름으로 복사해서 화마다 재활용 (목록 sfx/lib/README.md).
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


def whoosh():                                        # 휙: 짧은 바람 가르는 소리 (밴드패스 노이즈 스윕)
    d = 0.35; t = t_(d); n = rng.normal(0, 1, len(t)); y = np.zeros_like(n); fc = 600 + 3400 * np.sin(np.pi * t / d) ** 2
    lp = 0.0; bp = 0.0
    for i in range(len(n)):                          # 상태변수 필터 (주파수 움직임)
        f = 2 * np.sin(np.pi * fc[i] / SR); lp += f * bp; hp = n[i] - lp - 0.6 * bp; bp += f * hp; y[i] = bp
    return verb(y * np.sin(np.pi * t / d) ** 1.5, 0.3, 0.15)


def tiyong():                                        # 띠요옹: 고무줄 튕기듯 비브라토 내려감
    t = t_(0.8); f = 520 * (1 - 0.35 * t / 0.8) * (1 + 0.06 * np.sin(2 * np.pi * 11 * t)); x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x = (x + 0.3 * np.sin(2 * 2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 2.5) * np.minimum(1, t / 0.01)
    return verb(x, 0.3, 0.2)


def zawa():                                          # 쭈뼛(싸늘): 높은 떨리는 현 + 낮은 바람
    t = t_(1.6); env = np.minimum(1, t / 0.25) * np.exp(-np.maximum(0, t - 0.6) * 2)
    x = sum(np.sin(2 * np.pi * f * t * (1 + 0.004 * np.sin(2 * np.pi * 6 * t))) for f in (1244, 1318, 1975)) / 3
    n = np.convolve(rng.normal(0, 1, len(t)), np.ones(40) / 40, 'same') * 4
    return verb((x * 0.5 + n * 0.5) * env, 0.8, 0.35)


def tension():                                       # 긴장: 정적 밑에 깔리는 낮은 웅~ + 심장 두근
    d = 2.2; t = t_(d); env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t) + 0.3 * np.sin(2 * np.pi * 110.6 * t)) * env * 0.4
    y = drone.copy()
    for s in (0.3, 0.55, 1.2, 1.45):                 # 두-근 두-근
        k = t_(0.18); b = np.sin(2 * np.pi * (60 - 25 * k / 0.18) * k) * np.exp(-k * 22); i = int(s * SR); y[i:i + len(b)] += b
    return verb(y, 0.5, 0.2)


def heartbeat():                                     # 두-근 두-근만 (혁 10/28: 웅~ 빼고)
    d = 2.0; t = t_(d); y = np.zeros_like(t)
    for s in (0.15, 0.4, 1.05, 1.3):
        k = t_(0.2); b = np.sin(2 * np.pi * (62 - 28 * k / 0.2) * k) * np.exp(-k * 20); i = int(s * SR); y[i:i + len(b)] += b * (1 if s in (0.15, 1.05) else 0.7)
    return verb(y, 0.3, 0.12)


def fire():                                         # 화르륵: 불길 확 붙는 바람 + 타닥 불꽃 (불타는 중)
    d = 1.0; t = t_(d); n = rng.normal(0, 1, len(t))
    roar = np.convolve(n, np.ones(25) / 25, 'same') * 5 * np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 0.3) * 2.5)
    hiss = (n - np.convolve(n, np.ones(6) / 6, 'same')) * 0.35 * np.minimum(1, t / 0.05) * np.exp(-t * 3)
    y = roar + hiss
    for s in rng.uniform(0.05, 0.9, 14):             # 타닥 불티
        i = int(s * SR); k = int(0.008 * SR); y[i:i + k] += rng.normal(0, 1, k) * np.exp(-np.arange(k) / (k / 4)) * rng.uniform(0.4, 1.0)
    return verb(y, 0.4, 0.2)


def tick():                                         # 째깍: 시계 초침 (짧은 나무 딸깍 두 겹)
    t = t_(0.09); x = np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 160) + 0.5 * np.sin(2 * np.pi * 1300 * t) * np.exp(-t * 90)
    x += rng.normal(0, 1, len(t)) * np.exp(-t * 400) * 0.4
    return verb(x, 0.25, 0.12)


def _click(f, q):                                    # 벽시계 기계 딸깍 한 번 (짧고 마른 소리, 울림 거의 없음)
    t = t_(0.05); x = np.sin(2 * np.pi * f * t) * np.exp(-t * q) + 0.6 * np.sin(2 * np.pi * f * 1.9 * t) * np.exp(-t * q * 1.6)
    x += rng.normal(0, 1, len(t)) * np.exp(-t * 900) * 0.5
    return verb(x, 0.12, 0.06)


def tik(): return _click(3200, 260)                  # 똑 (높게)
def tok(): return _click(2100, 220)                  # 딱 (조금 낮게)


def gloom():                                        # 우울 '뿌우우~' (축 처지는 낮은 소리 · 개그 우울)
    d = 1.6; t = t_(d); f = 150 * (1 - 0.35 * t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 6)) * np.minimum(1, t / 0.06) * np.exp(-np.maximum(0, t - 1.0) * 3)
    x *= 1 + 0.15 * np.sin(2 * np.pi * 5 * t)
    return verb(x * 0.5, 0.6, 0.25)


ALL = dict(gloom=gloom, tick=tick, tik=tik, tok=tok, fire=fire, heartbeat=heartbeat, whoosh=whoosh, tiyong=tiyong, zawa=zawa, tension=tension, kiran=kiran, hatena=hatena, gogogo=gogogo, kirakira=kirakira, poyon=poyon, pikit=pikit, tiring=tiring)
if __name__ == '__main__':
    for name in sys.argv[1:] or ALL:
        x = ALL[name](); x = x / (np.abs(x).max() + 1e-9) * 0.85
        with wave.open(f'sfx/anime/{name}-syn.wav', 'w') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
        print(f'sfx/anime/{name}-syn.wav', round(len(x) / SR, 2), 's')
