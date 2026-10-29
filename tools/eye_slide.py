"""눈동자만 떼서 옮기기 (눈 굴리기 사이 프레임, 크레딧 0): 기준 그림 A 와 눈동자가 옮겨간 그림 B 에서 눈동자 위치 차이를 재고, A 의 눈동자를 t 만큼 옮겨 그림.
from eye_slide import EyeSlide; es = EyeSlide(A, B, box=(x0, y0, x1, y1)); fr = es.at(0.5)
"""
import numpy as np, cv2


def _parts(c):
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV); h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    white = ((s < 45) & (v > 195)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(white)
    sclera = np.isin(lab, [i for i in range(1, n) if st[i, 4] > 600]).astype(np.uint8)   # 큰 흰자 (작은 반짝이는 빼기)
    iris = (((h < 28) | (h > 165)) & (s > 40) & (v < 215) & (v > 25)).astype(np.uint8) | ((v < 70) & (s < 120)).astype(np.uint8)
    reg = cv2.dilate(sclera, np.ones((41, 41), np.uint8))
    E = cv2.morphologyEx(((sclera | iris) & reg), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cnts, _ = cv2.findContours(E, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); E2 = np.zeros_like(E)
    for c_ in cnts:
        if cv2.contourArea(c_) > 1500: cv2.drawContours(E2, [c_], -1, 1, -1)
    E2 = cv2.erode(E2, np.ones((5, 5), np.uint8))              # 눈꺼풀 선 안쪽만
    pupil = (E2 & (1 - sclera)).astype(np.uint8); pupil = cv2.morphologyEx(pupil, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return E2, sclera, pupil


class EyeSlide:
    def __init__(self, A, B, box):
        self.A = A.astype(np.float32); x0, y0, x1, y1 = self.box = box
        ca, cb = A[y0:y1, x0:x1], B[y0:y1, x0:x1]
        self.E, scl, self.P = _parts(ca); _, _, Pb = _parts(cb)
        W = ca.shape[1]; self.eyes = []
        for side in (slice(0, W // 2), slice(W // 2, W)):          # 왼눈 · 오른눈 따로
            pa = np.zeros_like(self.P); pa[:, side] = self.P[:, side]; pb = np.zeros_like(Pb); pb[:, side] = Pb[:, side]
            ya, xa = np.nonzero(pa); yb, xb = np.nonzero(pb)
            if len(xa) < 50 or len(xb) < 50: continue
            self.eyes.append((pa, np.array([xb.mean() - xa.mean(), yb.mean() - ya.mean()], np.float32)))
        white = ca[scl > 0].reshape(-1, 3); self.wcol = np.median(white, 0) if len(white) else np.float32([245, 245, 250])
        empty = ca.astype(np.float32).copy(); empty[self.P > 0] = self.wcol          # 눈동자 지운 눈
        self.empty = cv2.GaussianBlur(empty, (0, 0), 0.8)
        self.ca = ca.astype(np.float32)

    def at(self, t):
        x0, y0, x1, y1 = self.box; c = self.empty.copy(); E = self.E.astype(np.float32)
        for pa, off in self.eyes:
            M = np.float32([[1, 0, off[0] * t], [0, 1, off[1] * t]])
            lay = cv2.warpAffine(self.ca, M, (c.shape[1], c.shape[0])); m = cv2.warpAffine(pa.astype(np.float32), M, (c.shape[1], c.shape[0]))
            m = cv2.GaussianBlur(m * E, (0, 0), 0.8)[..., None]                       # 눈 안에서만
            c = c * (1 - m) + lay * m
        o = self.A.copy(); o[y0:y1, x0:x1] = c; return o
