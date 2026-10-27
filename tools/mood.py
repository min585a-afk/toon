"""귤이 채널 기본 칠 보정 — 기준 그림을 '극장판 칠'(front-drama-test) 쪽으로 25% 섞은 느낌을 아무 그림/영상에 0cr 로.
그림자 살짝 깊게 · 가장자리 비네트 · 채도 조금 낮춤 · 고운 그레인. 혁 10/27 확정(25%).
usage: python3 tools/mood.py in.(png|jpg|mp4) out [세기 0~1, 기본 1 = 확정값]
"""
import sys, subprocess, os, tempfile
import numpy as np, cv2


def mood(img, k=1.0, seed=1):
    a = img.astype(np.float32); H, W = a.shape[:2]
    lum = a.mean(-1, keepdims=True) / 255
    a = a * (1 - 0.10 * k * (1 - lum) ** 1.5)            # 어두운 곳(그림자)만 살짝 더 깊게
    yy, xx = np.mgrid[0:H, 0:W]; r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a *= (1 - 0.18 * k * np.clip(r - 0.5, 0, 1) ** 1.5)[..., None]
    g = a.mean(-1, keepdims=True); a = g + (a - g) * (1 - 0.06 * k)
    a += np.random.default_rng(seed).normal(0, 3 * k, (H, W, 1))
    return np.clip(a, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    if src.lower().endswith(('.mp4', '.mov')):
        cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS); tmp = tempfile.mktemp(suffix='.mp4'); out = None; i = 0
        while True:
            ok, fr = cap.read()
            if not ok: break
            g = mood(fr, k, i // 3); i += 1
            if out is None: out = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (g.shape[1], g.shape[0]))
            out.write(g)
        out.release()
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-i', src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', dst], check=True); os.remove(tmp)
    else:
        cv2.imwrite(dst, mood(cv2.imread(src), k))
    print(dst)
