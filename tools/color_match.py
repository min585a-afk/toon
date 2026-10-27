"""그림 색감을 기준 그림에 맞춤 (LAB 평균·편차 맞추기 + 살짝 또렷하게). 크레딧 0.
usage: python3 tools/color_match.py 기준.png 바꿀.png out.png [--amount 0.85] [--also 같은보정할.png:out2.png ...]
"""
import argparse
import numpy as np
import cv2


def stats(im):
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32); return lab.reshape(-1, 3).mean(0), lab.reshape(-1, 3).std(0)


def apply(im, src, ref, amount, sharp):
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    out = (lab - src[0]) / (src[1] + 1e-6) * ref[1] + ref[0]
    out = lab * (1 - amount) + out * amount
    o = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    if sharp: o = cv2.addWeighted(o, 1 + sharp, cv2.GaussianBlur(o, (0, 0), 1.5), -sharp, 0)
    return o


ap = argparse.ArgumentParser(); ap.add_argument('ref'); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--amount', type=float, default=0.85); ap.add_argument('--sharp', type=float, default=0.35); ap.add_argument('--also', nargs='*', default=[])
a = ap.parse_args()
ref, im = cv2.imread(a.ref), cv2.imread(a.src); s, r = stats(im), stats(ref)
cv2.imwrite(a.out, apply(im, s, r, a.amount, a.sharp)); print(a.out)
for pair in a.also:
    i, o = pair.split(':'); cv2.imwrite(o, apply(cv2.imread(i), s, r, a.amount, a.sharp)); print(o)
