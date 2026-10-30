"""완성본 내기 전 점검 (혁 10/30: '저런 거 통일 잘 시켜줘'). 크레딧 0.
usage: python3 tools/qa_check.py ep02/full.json ep02/ep02-full.mp4
1) 제목 · 자막 가운데 (컷마다 가운데 ±8px)   2) 전체 크기 -14 LUFS 근처 · 피크 -1dB 아래
3) 대사 wav 가 컷 안에서 끝나는지            4) 대사 원본 끝 글자 잘림 (원본 끝 0.3초에 소리 남아 있으면)
5) 효과음 · 대사 자리에서 소리 들리는지 (-45dB 아래면 안 들림)
"""
import json, subprocess, sys, os, re
import numpy as np, cv2
spec, video = json.load(open(sys.argv[1])), sys.argv[2]; FPS, bad = 24, []
dur = lambda p: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
st, t = {}, 0.0
for c in spec['cuts']:
    n = c['file'].split('/')[-1][:-4]; st[n] = (t, round(dur(c['file']) * FPS) / FPS); t += st[n][1]
# 1) 가운데
cap = cv2.VideoCapture(video)
for n, (a, d) in st.items():
    cap.set(cv2.CAP_PROP_POS_MSEC, (a + d / 2) * 1000); ok, f = cap.read(); g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    for nm, (y0, y1) in {'제목': (150, 300), '자막': (1380, 1480)}.items():
        xs = np.nonzero((g[y0:y1] > 140).any(0))[0]
        if len(xs) and abs((xs.min() + xs.max()) / 2 - 540) > 8: bad.append(f'가운데 아님: {n} {nm} {(xs.min() + xs.max()) / 2:.0f}px')
# 2) 크기
o = subprocess.run(['ffmpeg', '-v', 'info', '-i', video, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1]); P = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', o)[-1])
print(f'크기 {I} LUFS · 피크 {P} dBFS')
if abs(I + 14) > 1.0: bad.append(f'전체 크기 {I} LUFS (목표 -14)')
if P > -1.0: bad.append(f'피크 {P} dBFS (-1 넘음)')
# 3) 4) 대사
rd = lambda p: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '44100', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
voices = [(s[0], s[1], s[2]) for s in spec['sfx'] if s[0].startswith('voice/')]
for vf, cut, off in voices:
    if off + dur(vf) > st[cut][1] - 0.03: bad.append(f'대사가 컷 넘어감: {cut} {vf}')
for vf in sorted({v[0] for v in voices} | {m for b in sorted(os.listdir(os.path.dirname(sys.argv[1]))) if b.startswith('build_') for m in re.findall(r"'(voice/[^']+-use\.wav)'", open(os.path.join(os.path.dirname(sys.argv[1]), b)).read())}):
    raw = vf.replace('-use.wav', '.wav')
    if not os.path.exists(raw): continue
    x = rd(raw)[:-int(0.08 * 44100)]; n = 2205; e = np.array([np.sqrt((x[i:i + n] ** 2).mean()) for i in range(0, len(x) - n, n)])
    if len(e) > 3 and e[-3:].max() > 0.3 * e.max(): bad.append(f'대사 끝 잘렸을 수 있음: {raw}')
# 5) 소리 자리
x = rd(video) / 2
for s in spec['sfx']:
    if s[1] not in st: bad.append(f'없는 컷 이름: {s}'); continue
    a = st[s[1]][0] + s[2]; seg = x[int(a * 44100):int((a + 0.4) * 44100)]
    if len(seg) and 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9) < -45: bad.append(f'안 들림: {s[0]} @ {a:.2f}s')
print('문제 없음' if not bad else '문제:\n  ' + '\n  '.join(bad))
