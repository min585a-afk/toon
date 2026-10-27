"""손글씨 느낌 효과 글자를 획으로 직접 그림 (가늘고 길게 기울어진 펜 획 + 번개 끝). 크레딧 0.
usage: python3 tools/sfx_hand.py brand/sfx/ppajik.png [미리보기.jpg]
획 좌표는 아래 STROKES (1400x1000 칸, 기울이기 전).
"""
import sys
import numpy as np
import cv2

CW, CH, SHEAR, WID = 1400, 1000, 0.28, 46
# 빠직: ㅃ(ㅂ 두 개) + ㅏ / ㅈ + ㅣ + ㄱ(끝은 번개처럼 꺾임)
STROKES = [
    [(60, 170), (85, 610)], [(225, 140), (240, 590)], [(70, 380), (232, 362)], [(80, 600), (245, 588)],        # ㅂ
    [(285, 165), (305, 605)], [(445, 135), (458, 585)], [(295, 375), (452, 358)], [(300, 597), (462, 585)],   # ㅂ
    [(560, 40), (585, 820)], [(585, 400), (700, 385)],                                                       # ㅏ
    [(760, 120), (1010, 92)], [(900, 105), (740, 470)], [(880, 270), (1035, 450)],                           # ㅈ
    [(1150, 30), (1172, 560)],                                                                                # ㅣ
    [(760, 640), (1170, 612), (1110, 790), (1215, 770), (1120, 985)],                                        # ㄱ + 번개
]


def mask(scale=1.0, seed=3):
    rng = np.random.default_rng(seed); pad = 200
    W, H = int((CW + CH * SHEAR + pad * 2) * scale), int((CH + pad * 2) * scale)
    m = np.zeros((H, W), np.uint8)
    P = lambda x, y: ((x + (CH - y) * SHEAR + pad) * scale, (y + pad) * scale)
    for s in STROKES:
        pts = [np.array(P(x + rng.normal(0, 6), y + rng.normal(0, 6))) for x, y in s]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]; d = b - a; n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
            w0 = WID * scale * (0.75 if i == 0 else 1.0) / 2; w1 = WID * scale * (0.45 if i == len(pts) - 2 else 1.0) / 2
            mid = (a + b) / 2; wm = WID * scale / 2
            poly = np.array([a + n * w0, mid + n * wm, b + n * w1, b - n * w1, mid - n * wm, a - n * w0], np.int32)
            cv2.fillPoly(m, [poly], 255, cv2.LINE_AA)
            if 0 < i: cv2.circle(m, tuple(a.astype(int)), int(wm * 0.9), 255, -1, cv2.LINE_AA)
    ys, xs = np.nonzero(m); return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sprite(m):
    k = max(6, int(m.shape[1] * 0.012)); pad = k * 4; h, w = m.shape
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
