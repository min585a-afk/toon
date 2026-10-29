"""EP02 벽시계: 바늘 없는 시계 그림(ep02/s1-clock.png) 위에 코드로 시·분·초침 (실제 시간대로 째깍 · 초침 살짝 튕김). 크레딧 0.
from clock import clock_at; img = clock_at(5*3600 + 55*60 + 0.0)   # 초 단위 시각
"""
import numpy as np, cv2
SRC = cv2.imread('ep02/s1-clock.png')
H0, W0 = SRC.shape[:2]
# 시계판 맞춤 (그림 2336x1744 기준): 가운데 · 12시 방향 · 3시 방향 벡터 (원 → 기울어진 타원)
# 원근(아래쪽이 더 가까움) → 눈금 12·3·6·9 바깥 끝 네 점으로 호모그래피 (800x600 미리보기에서 잰 값 × 2.92)
_sc = W0 / 800; _img_pts = np.float32([[390, 89], [553, 292], [407, 452], [222, 243]]) * _sc
HM = cv2.getPerspectiveTransform(np.float32([[0, -1], [1, 0], [0, 1], [-1, 0]]), _img_pts)
C0 = cv2.perspectiveTransform(np.float32([[[0, 0]]]), HM)[0, 0]; C = np.float32([395, 262]) * _sc   # 그림 속 가운데 핀 (바늘 시작점)


def P(theta, r):                                    # theta: 12시에서 시계방향 라디안 · r: 반지름 비율 (바깥 눈금 = 1)
    p = cv2.perspectiveTransform(np.float32([[[r * np.sin(theta), -r * np.cos(theta)]]]), HM)[0, 0]
    return p + (C - C0) * max(0.0, 1 - abs(r))          # 가운데는 핀에 맞추고 바깥 눈금은 그대로


def hand(img, theta, r0, r1, w, col, shadow=True):
    a, b = P(theta, r0), P(theta, r1)
    if shadow:
        o = np.array([10, 14]); cv2.line(img, tuple((a + o).astype(int)), tuple((b + o).astype(int)), (150, 120, 150), w + 4, cv2.LINE_AA)
    cv2.line(img, tuple(a.astype(int)), tuple(b.astype(int)), (25, 20, 30), w + 8, cv2.LINE_AA)      # 굵은 검정 선(셀 애니)
    cv2.line(img, tuple(a.astype(int)), tuple(b.astype(int)), col, w, cv2.LINE_AA)


def clock_at(t):
    img = SRC.copy().astype(np.uint8)
    s = t % 60; si = int(s); fr = s - si
    tick = si + min(1.0, fr / 0.08) + 0.12 * np.sin(min(1.0, fr / 0.25) * np.pi) * (fr < 0.25)  # 째깍: 0.08초에 넘어가고 살짝 튕김
    m = (t / 60) % 60; h = (t / 3600) % 12
    hand(img, h / 12 * 2 * np.pi, -0.08, 0.48, 26, (70, 50, 60))
    hand(img, m / 60 * 2 * np.pi, -0.1, 0.74, 18, (70, 50, 60))
    hand(img, tick / 60 * 2 * np.pi, -0.18, 0.84, 6, (60, 60, 220))
    cv2.circle(img, tuple(C.astype(int)), 26, (25, 20, 30), -1, cv2.LINE_AA); cv2.circle(img, tuple(C.astype(int)), 16, (60, 60, 220), -1, cv2.LINE_AA)
    out = cv2.GaussianBlur(img, (0, 0), 1.2)                                                    # 선 살짝 뭉개짐 (그림이랑 맞춤)
    return out
