"""손글씨 느낌 효과 글자를 획으로 직접 그림 (가늘고 길게 기울어진 펜 획 + 번개 끝). 크레딧 0.
usage: python3 tools/sfx_hand.py brand/sfx/ppajik.png [미리보기.jpg]
획 좌표는 아래 STROKES (기울이기 전). 혁 예시(번쩍): 굵기 일정 · 끝 네모 · 가로획 오른쪽 위로 삐져나옴 · 많이 기울임 · 계단.
"""
import sys
import numpy as np
import cv2

CW, CH, SHEAR, WID = 1000, 1100, 0.36, 46
SLOPE = 0.33   # 가로획은 오른쪽으로 올라감
DX, DY = 640, 200  # 둘째 글자는 오른쪽 아래로 계단처럼


def bar(x0, x1, y):  # 가로획: 세로획보다 양쪽으로 삐져나옴
    return [(x0, y), (x1, y - (x1 - x0) * SLOPE)]


def shift(st, dx, dy): return [[(x + dx, y + dy) for x, y in s] for s in st]


# 빠직: ㅃ + ㅏ / ㅈ + ㅣ + ㄱ(끝은 번개처럼 꺾임)
STROKES = [
    [(30, 150), (30, 590)], [(150, 90), (150, 540)], bar(-20, 200, 380), bar(-10, 205, 600),         # ㅂ
    [(240, 125), (240, 560)], [(360, 65), (360, 515)], bar(195, 410, 330), bar(205, 415, 550),      # ㅂ
    [(475, -40), (475, 760)], bar(475, 600, 400),                                                    # ㅏ
] + shift([
    bar(0, 250, 70), [(150, 30), (10, 420)], [(110, 210), (250, 390)],                              # ㅈ
    [(330, -110), (330, 520)],                                                                       # ㅣ
    bar(-10, 370, 640) + [(300, 750), (385, 728), (310, 880)],                                       # ㄱ + 번개
], DX, DY)


def mask(scale=1.0, seed=3):
    rng = np.random.default_rng(seed); pad = 250
    W, H = int((CW + 900 + CH * SHEAR + pad * 2) * scale), int((CH + 900 + pad * 2) * scale)
    m = np.zeros((H, W), np.uint8)
    P = lambda x, y: ((x + (CH - y) * SHEAR + pad) * scale, (y + pad) * scale)
    wd = WID * scale / 2
    for s in STROKES:
        pts = [np.array(P(x + rng.normal(0, 5), y + rng.normal(0, 5))) for x, y in s]
        for i in range(len(pts) - 1):  # 끝이 네모난 일정한 굵기 펜 획
            a, b = pts[i], pts[i + 1]; d = b - a; n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
            cv2.fillPoly(m, [np.array([a + n * wd, b + n * wd, b - n * wd, a - n * wd], np.int32)], 255, cv2.LINE_AA)
            if i: cv2.circle(m, tuple(a.astype(int)), int(wd), 255, -1, cv2.LINE_AA)
    ys, xs = np.nonzero(m); return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sprite(m):
    k = max(6, int(m.shape[1] * 0.02)); pad = k * 4; h, w = m.shape
    outline = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k * 2 + 1, k * 2 + 1)))
    can = np.zeros((h + pad * 2, w + pad * 2, 4), np.uint8)
    def put(mask, col, dx=0, dy=0):
        mm = np.zeros(can.shape[:2], np.uint8); mm[pad + dy:pad + dy + h, pad + dx:pad + dx + w] = mask
        a = mm.astype(np.float32)[..., None] / 255; can[..., :3] = (can[..., :3] * (1 - a) + np.array(col) * a).astype(np.uint8)
        can[..., 3] = np.maximum(can[..., 3], mm)
    put(outline, (20, 10, 20), int(k * 1.6), int(k * 1.8)); put(outline, (20, 10, 20)); put(m, (255, 255, 255))
    return can


if __name__ == '__main__':
    m = mask(); s = sprite(m); cv2.imwrite(sys.argv[1], s); print(sys.argv[1], s.shape[1], 'x', s.shape[0])
    if len(sys.argv) > 2:  # 미리보기: 분홍 + 라벤더 그림자(예시 느낌) | 흰 + 검정 테두리
        pv = np.full((m.shape[0] + 40, m.shape[1] + 40, 3), 255, np.uint8)
        sh = np.zeros(pv.shape[:2], np.uint8); sh[22:22 + m.shape[0], 26:26 + m.shape[1]] = m
        pv[sh > 127] = (245, 215, 215); mm = np.zeros(pv.shape[:2], np.uint8); mm[14:14 + m.shape[0], 14:14 + m.shape[1]] = m
        pv[mm > 127] = (200, 185, 245)
        bg = np.full((s.shape[0], s.shape[1], 3), (40, 20, 90), np.uint8); a = s[..., 3:4] / 255
        v = (bg * (1 - a) + s[..., :3] * a).astype(np.uint8); pv = cv2.resize(pv, (int(pv.shape[1] * v.shape[0] / pv.shape[0]), v.shape[0]))
        cv2.imwrite(sys.argv[2], cv2.resize(np.hstack([pv, v]), None, fx=0.35, fy=0.35))
