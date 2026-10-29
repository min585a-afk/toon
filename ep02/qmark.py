"""만화 셀 재질 '?' (우리 그림체: 굵기 들쭉날쭉한 먹선 · 셀 두 톤 칠 + 하이라이트 · 살짝 흐림 + 종이 결). 크레딧 0.
usage: from qmark import make_q → RGBA (numpy, H×W×4)
"""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont


def make_q(size=230, fill=(255, 236, 150), shade=(236, 186, 92), seed=3):
    S = size * 4; rng = np.random.default_rng(seed)
    im = Image.new('L', (S, S)); d = ImageDraw.Draw(im)
    d.text((S // 2, S // 2), '?', font=ImageFont.truetype('tools/fonts/jua.ttf', int(S * 0.78)), fill=255, anchor='mm')
    m = np.array(im).astype(np.float32) / 255
    m = cv2.warpAffine(m, cv2.getRotationMatrix2D((S / 2, S / 2), -10, 1.0), (S, S))     # 살짝 기울임
    body = (m > 0.5).astype(np.uint8)
    # 먹선: 바깥으로 두께가 들쭉날쭉 (손으로 그은 느낌) — 거리 + 저주파 노이즈
    dist = cv2.distanceTransform(1 - body, cv2.DIST_L2, 5)
    nz = cv2.resize(rng.random((8, 8)).astype(np.float32), (S, S), interpolation=cv2.INTER_CUBIC)
    line = (dist < S * (0.022 + 0.018 * nz)).astype(np.float32)
    # 셀 칠: 오른쪽 아래 그림자 한 톤 + 왼쪽 위 흰 하이라이트 한 줄
    inside = cv2.distanceTransform(body, cv2.DIST_L2, 5)
    sh = cv2.warpAffine(body.astype(np.float32), np.float32([[1, 0, -S * 0.035], [0, 1, -S * 0.045]]), (S, S))
    shadow = (body > 0) & (sh < 0.5)
    hi = cv2.warpAffine(body.astype(np.float32), np.float32([[1, 0, S * 0.03], [0, 1, S * 0.035]]), (S, S))
    high = (body > 0) & (hi < 0.5) & (inside > S * 0.012) & (np.arange(S)[:, None] < S * 0.55)
    rgb = np.zeros((S, S, 3), np.float32); rgb[body > 0] = fill; rgb[shadow] = shade; rgb[high] = (255, 255, 250)
    ink = np.float32([38, 30, 44]); a = np.maximum(line, body.astype(np.float32))
    rgb = rgb * (1 - line[..., None] * (body == 0)[..., None]) + ink * (line * (body == 0))[..., None]
    rgb = cv2.resize(rgb, (size, size), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (size, size), interpolation=cv2.INTER_AREA)
    rgb = cv2.GaussianBlur(rgb, (0, 0), 0.6) + rng.normal(0, 4, rgb.shape)                # 그림 흐림 + 종이 결
    return np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8)


if __name__ == '__main__':
    q = make_q(); bg = np.full((260, 260, 3), 200, np.uint8); a = q[..., 3:] / 255
    bg[15:245, 15:245] = (q[..., :3] * a + bg[15:245, 15:245] * (1 - a)).astype(np.uint8)
    cv2.imwrite('/tmp/claude-0/q.png', cv2.cvtColor(bg, cv2.COLOR_RGB2BGR))
