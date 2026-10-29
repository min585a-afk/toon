"""EP02 공통 효과: 반짝이(1화 반짝이 그대로).\n"""
import numpy as np, cv2


def star(fr, x, y, L):                                           # 1화 반짝이 그대로 (ep01b/build_c6.py)
    if L < 3: return fr
    lay = np.zeros(fr.shape[:2], np.float32); w = max(2, L // 6)
    for (dx, dy), ln in [((1, 0), L * 0.7), ((0, 1), L)]:
        p = np.array([(x - dx * ln, y - dy * ln), (x + dy * w, y + dx * w), (x + dx * ln, y + dy * ln), (x - dy * w, y - dx * w)], np.int32)
        cv2.fillPoly(lay, [p], 1.0, cv2.LINE_AA)
    cv2.circle(lay, (x, y), max(2, L // 5), 1.0, -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(lay, (0, 0), L * 0.35) * 2.2 + cv2.GaussianBlur(lay, (0, 0), L * 0.1)
    g = np.clip(glow, 0, 1)[..., None]; c = np.clip(lay, 0, 1)[..., None]
    o = fr.astype(np.float32) + g * np.array([90, 190, 255], np.float32) * 0.9
    return np.clip(o * (1 - c) + 255 * c, 0, 255).astype(np.uint8)
