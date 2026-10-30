"""EP02 장면 9: 최버터 H3 영상(ep02/video/s9-butter-count-h3.mp4, 10cr) — 손가락 하나 "삼겹살?" → 두 개 "아니면 닭발?" → 윙크.
대사 마디에 맞춰 영상 프레임을 구간별로 맞춤 (쉬는 동안은 입 다문 프레임). 12fps. 크레딧 0.
usage: python3 ep02/build_s9.py → ep02/s9-butter-menu.mp4
"""
import subprocess, tempfile
import numpy as np, cv2, sys
sys.path.insert(0, 'ep02'); from fx import star
FPS, W, H = 24, 1080, 810
VOICE = 'voice/ep02/butter-lines/s9b-1-use.wav'                 # 삼겹살? 0.03~1.16 · 아니면 1.47~2.35 · 닭발? 2.65~3.03
LEAD = 0.55                                                      # 말 시작 전: 이빨 반짝! (혁 10/30) + 손 올라옴 (영상 4 → 16)
GLINT = (0.03, 0.33)                                             # 반짝 커졌다 작아지는 시간 (출력 초)
# (목소리 초, 영상 프레임): 손가락 하나 + 말 16~54 · 쉼(입 다묾 54) · 두 개로 바뀌며 '아니면' 70~92 · 쉼 96 · '닭발?' 98~108
KEY = [(-LEAD, 0), (-0.2, 0), (0.0, 12), (0.1, 16), (1.16, 54), (1.47, 54), (1.5, 70), (2.35, 92), (2.4, 96), (2.62, 96), (2.65, 98), (3.03, 108)]
TAIL = (112, 124)                                                # 끝: 입 다물고 윙크
cap = cv2.VideoCapture('ep02/video/s9-butter-count-h3.mp4'); v = []
while True:
    ok, fr = cap.read()
    if not ok: break
    v.append(cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA))
kt, kf = zip(*KEY); seq = []
for k in range(int((LEAD + kt[-1]) * FPS)): t = (k - k % 2) / FPS - LEAD; seq.append(int(np.interp(t, kt, kf)))
seq += list(range(*TAIL)); tmp = tempfile.mkdtemp()
def tooth(fr):                                                   # 이빨 반짝이 자리 (입 오른쪽 위 하얀 점)
    h = cv2.cvtColor(fr[360:450, 480:680], cv2.COLOR_BGR2HSV); m = ((h[..., 2] > 235) & (h[..., 1] < 35)).astype(np.uint8)
    n, lab, st, c = cv2.connectedComponentsWithStats(m)
    if n < 2: return None
    i = 1 + np.argmax(st[1:, 4]); return int(c[i][0]) + 480, int(c[i][1]) + 360
def unglint(fr):                                                 # 영상에 박힌 이빨 반짝 점 지움 (혁 10/30: 계속 있음 → 반짝! 한 번만)
    y0, x0 = 340, 440; c = fr[y0:460, x0:700].astype(np.float32); h = cv2.cvtColor(fr[y0:460, x0:700], cv2.COLOR_BGR2HSV)
    core = (h[..., 2] > 242) & (h[..., 1] < 30)
    if core.sum() == 0: return fr
    ys, xs = np.nonzero(core); cy, cx = ys.mean(), xs.mean()
    yy, xx = np.mgrid[0:c.shape[0], 0:c.shape[1]]; near = (yy - cy) ** 2 + (xx - cx) ** 2 < 22 ** 2
    m = near & (((h[..., 2] > 205) & (h[..., 1] < 45)) | core)      # 별 + 둘레 하얀 빛 (이빨은 V 190 쯤이라 거의 안 걸림)
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    for r in np.unique(np.nonzero(m)[0]):                        # 줄마다 왼쪽 · 오른쪽 안 빛난 색으로 이어 칠함 (이빨 · 입술선 · 혀 경계가 가로라 맞음)
        row = m[r]; ok = np.nonzero(~row)[0]
        if len(ok) < 2: continue
        bad = np.nonzero(row)[0]
        for ch in range(3): c[r, bad, ch] = np.interp(bad, ok, c[r, ok, ch])
    out = fr.copy(); out[y0:460, x0:700] = np.clip(c, 0, 255).astype(np.uint8); return out
for k, j in enumerate(seq):
    fr = v[min(len(v) - 1, j)].copy(); t = (k - k % 2) / FPS; p = tooth(fr); fr = unglint(fr)
    if GLINT[0] <= t <= GLINT[1] and p:
        ph = (t - GLINT[0]) / (GLINT[1] - GLINT[0]); fr = star(fr, p[0], p[1], int(40 * np.sin(ph * np.pi)))
    cv2.imwrite(f'{tmp}/{k:05d}.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 93])
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg', '-i', VOICE, '-i', 'sfx/anime/kiran-syn.wav', '-filter_complex', f'[1:a]adelay={int(LEAD * 1000)}:all=1[v];[2:a]volume=0.35[g];[v][g]amix=2:normalize=0,apad[a]',
                '-map', '0:v', '-map', '[a]', '-t', str(len(seq) / FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', 'ep02/s9-butter-menu.mp4'], check=True)
print('ep02/s9-butter-menu.mp4', round(len(seq) / FPS, 2), 's')
