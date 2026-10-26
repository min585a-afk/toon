"""90년대 셀 애니 캡처 색감 — 화질은 그대로, 색만 그 시절처럼. 크레딧 0.
레퍼런스(혁 햄스터 애)에서 잰 값: 채도 절반 · 검정은 자주빛 진갈색 · 흰색은 분홍 크림 · 대비 낮음.
usage: python3 anime_grade.py in.png out.jpg [세기 0~1, 기본 1]
       python3 anime_grade.py in.mp4 out.mp4 [세기]   (영상: 프레임마다 같은 보정, 그레인만 매번 다르게 · 소리 그대로)
완성본에 마지막으로 한 번(자막 · 제목 얹기 전). 혁 기본 0.7.
"""
import sys
import numpy as np
import cv2


def grade(bgr, k=1.0, rng=None):
    rng = rng or np.random.default_rng(7)
    # 셀처럼 평평하게: 선은 두고 칠 안의 결만 정리
    flat = cv2.bilateralFilter(bgr, 9, 40, 9)
    a = flat[..., ::-1].astype(np.float32) / 255
    # 1) 채도: 진한 색(가디건 · 오리 · 하늘)만 눌러줌, 피부 분홍은 살림
    mx = a.max(-1, keepdims=True); mn = a.min(-1, keepdims=True)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    cap = 0.28 + (sat - 0.28) * (1 - 0.6 * k)
    scale = np.where(sat > 0.28, cap / np.maximum(sat, 1e-6), 1.0)
    a = mx - (mx - a) * scale
    # 2) 검정 → 자주빛 진갈색 (어두운 곳만), 흰색 → 분홍 크림
    black = np.array([0.13, 0.09, 0.12], np.float32)
    dk = np.clip(1 - mx / 0.45, 0, 1) ** 1.5
    a = a + (black - a) * dk * 0.75 * k
    white = np.array([0.96, 0.88, 0.88], np.float32)
    lt = np.clip((mx - 0.8) / 0.2, 0, 1)
    a = a + (np.minimum(a, white) - a) * lt * k
    # 3) 전체 살짝 분홍 쪽으로 · 밝게
    a = a * (1 - 0.07 * k) + np.array([1.0, 0.82, 0.85], np.float32) * 0.07 * k
    # 4) 아주 살짝 부드럽게 + 고운 그레인
    a = cv2.GaussianBlur(a, (0, 0), 0.6 * k)
    a += rng.normal(0, 0.012 * k, a.shape[:2]).astype(np.float32)[..., None]
    return (np.clip(a, 0, 1)[..., ::-1] * 255).astype(np.uint8)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    if src.lower().endswith(('.mp4', '.mov')):
        import os, subprocess, tempfile
        cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
        tmp = tempfile.mktemp(suffix='.mp4'); out = None; rng = np.random.default_rng(7)
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            g = grade(fr, k, rng)
            if out is None:
                out = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (g.shape[1], g.shape[0]))
            out.write(g)
        out.release()
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-i', src, '-map', '0:v', '-map', '1:a?',
                        '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy', dst], check=True)
        os.remove(tmp)
    else:
        cv2.imwrite(dst, grade(cv2.imread(src), k), [cv2.IMWRITE_JPEG_QUALITY, 93])
    print(dst)
