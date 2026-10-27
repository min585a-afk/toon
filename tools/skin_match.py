"""피부색만 기준 그림에 맞춤 (피부 영역 LAB 평균·편차) + 피부 결 매끈하게 + 선 살짝 또렷하게. 크레딧 0.
usage: python3 tools/skin_match.py 기준.png 바꿀.png out.png [같은보정할.png:out2.png ...]
"""
import sys
import numpy as np
import cv2


def skin_mask(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 0] > 5) & (hsv[..., 0] < 25) & (hsv[..., 1] > 40) & (hsv[..., 1] < 140) & (hsv[..., 2] > 150)).astype(np.float32)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); return cv2.GaussianBlur(m, (0, 0), 3)[..., None]


def stats(im, m):
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32); w = m[..., 0] > 0.5
    return lab[w].mean(0), lab[w].std(0)


ref, src, out = sys.argv[1:4]
R, I = cv2.imread(ref), cv2.imread(src); mI = skin_mask(I); rs, ss = stats(R, skin_mask(R)), stats(I, mI)


def fix(im, m):
    smooth = cv2.bilateralFilter(im, 9, 30, 7)                                  # 피부 결 매끈하게 (선은 유지)
    lab = cv2.cvtColor(smooth, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab = (lab - ss[0]) / (ss[1] + 1e-6) * np.maximum(rs[1], ss[1] * 0.6) + rs[0]
    sk = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    o = im * (1 - m) + sk * m
    o = cv2.addWeighted(o, 1.3, cv2.GaussianBlur(o, (0, 0), 1.2), -0.3, 0)    # 선 살짝 또렷하게
    return np.clip(o, 0, 255).astype(np.uint8)


cv2.imwrite(out, fix(I, mI)); print(out)
for pair in sys.argv[4:]:
    i, o = pair.split(':'); im = cv2.imread(i); cv2.imwrite(o, fix(im, skin_mask(im))); print(o)
