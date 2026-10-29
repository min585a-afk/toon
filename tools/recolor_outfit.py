"""은서 빨강 가디건 → 다른 색 (화마다 복장 바꾸기, 크레딧 0). 빨강(채도 높은) 픽셀만 · 볼 홍조 · 입술 같은 얼굴 쪽은 y_min 위로 제외.
from recolor_outfit import to_black; fr = to_black(fr, y_min=0.45, x_range=(0.2, 1.0))
"""
import numpy as np, cv2


def to_black(fr, y_min=0.4, x_range=(0.0, 1.0), extra_mask=None, face=None, s_min=125, hue_hi=165, v_max=232):
    """face = (cx, cy, rx, ry) 비율 — 이 타원 안(볼 홍조 · 입술 · 귀)은 안 바꿈."""
    im = fr.astype(np.uint8); H, W = im.shape[:2]; hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(np.float32), hsv[..., 1].astype(np.float32), hsv[..., 2].astype(np.float32)
    red = (((h < 10) | (h > hue_hi)) & (s > s_min) & (v > 50) & (v < v_max)).astype(np.uint8)   # 피부(채도 낮고 밝음)는 빼기
    red[:int(H * y_min)] = 0; red[:, :int(W * x_range[0])] = 0; red[:, int(W * x_range[1]):] = 0
    if face is not None:
        cv2.ellipse(red, (int(face[0] * W), int(face[1] * H)), (int(face[2] * W), int(face[3] * H)), 0, 0, 360, 0, -1)
    if extra_mask is not None: red &= extra_mask
    red = cv2.morphologyEx(red, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.GaussianBlur(red.astype(np.float32), (0, 0), 1.2)[..., None]
    shade = (v / 255.0) ** 1.4                                    # 원래 명암(주름 · 그림자) 유지
    black = np.stack([46 + 40 * shade, 40 + 38 * shade, 44 + 40 * shade], -1)   # 살짝 보랏빛 도는 검정 (셀 애니 검정 옷)
    return (fr * (1 - m) + black * m).astype(fr.dtype)
