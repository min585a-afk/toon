"""컷 이어붙이기 → 무드 25% → 화 제목 얹기 → 배경음 깔기(대사 땐 작게) → 9:16 릴스 틀 + 컷마다 자막. 크레딧 0.
usage: python3 tools/assemble.py spec.json out.mp4
spec = {"title": ["두 얼굴", "TWO FACES", 시작초, 길이초] (없으면 위 제목만), "sfx": [["효과음.wav", "컷 이름 일부", 컷 안 초, 볼륨], ...],
        "bgm": "brand/bgm/opening-A.mp3", "bgm_vol": 0.5, "bgm_duck": 0.18, "duck_from": 5.9, "bgm_until": 3.9,
        "cuts": [{"file": "...mp4", "ko": "", "en": "", "sec": null}, ...]}
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, 'tools')
from reel_frame import W, H, TOP, VH, FJ, FG, slanted

FPS = 24
def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)


def has_audio(p):
    return 'audio' in subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout


def frame_png(path, title, ko, en):
    o = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(o)
    d.rectangle((0, TOP, W, TOP + VH), fill=(0, 0, 0, 0))
    tko, ten = title if isinstance(title, tuple) else (title, '')   # 위 제목 = 자막 글꼴 + 아래 영어 제목 (혁 10/28)
    if tko: slanted(o, tko, ImageFont.truetype(FG, 108), (255, 228, 92), TOP - (215 if ten else 180))
    if ten: slanted(o, ten, ImageFont.truetype(FG, 40), (255, 228, 92), TOP - 85)
    if ko: slanted(o, ko, ImageFont.truetype(FG, 63), (255, 255, 255), TOP + VH + 30)
    if en: slanted(o, en, ImageFont.truetype(FG, 38), (57, 255, 20), TOP + VH + 118)
    o.save(path)


def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; tmp = tempfile.mkdtemp()
    # 1) 컷마다 같은 크기 · fps · 소리 형식으로
    parts, times, cut_times, no_title, t = [], [], [], [], 0.0
    for i, c in enumerate(spec['cuts']):
        p = f'{tmp}/p{i}.mp4'; d = c.get('sec') or dur(c['file']); d = round(d * FPS) / FPS   # 프레임 단위로 딱 맞춤
        # 영상 · 소리 따로 만들고(소리는 wav 로 길이 정확히) 나중에 합침 → 컷 이을 때 소리가 조금씩 밀리던 것(10/29 한숨 싱크) 없앰
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', c['file'], '-t', str(d), '-vf', f'scale=1080:810,fps={FPS},setsar=1,tpad=stop_mode=clone:stop_duration=1',
                        '-frames:v', str(round(d * FPS)), '-an', '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', p], check=True)
        af = f"volume={c.get('vol', 1)},apad,atrim=0:{d},afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.025)}:d=0.025"   # "vol": 컷 소리 크기 · 컷 끝 뚝 소리 X
        src = ['-i', c['file']] if has_audio(c['file']) else ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']
        subprocess.run(['ffmpeg', '-y', '-v', 'error', *src, '-af', af, '-ar', '44100', '-ac', '2', '-c:a', 'pcm_s16le', f'{tmp}/a{i}.wav'], check=True)
        parts.append(p); cut_times.append((t, t + d))
        if c.get('subs'):                               # 한 컷 안에서 자막 나누기: [[시작, 끝, 한글, 영어], ...] (컷 안 초)
            for a0, b0, ko, en in c['subs']: times.append((t + a0, t + min(b0, d), ko, en))
        else: times.append((t, t + d, c.get('ko', ''), c.get('en', '')))
        if c.get('no_title'): no_title.append((t, t + d))  # 끝 화면 등: 위 제목 없이
        t += d
    open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
    open(f'{tmp}/la.txt', 'w').write(''.join(f"file '{tmp}/a{i}.wav'\n" for i in range(len(parts))))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', f'{tmp}/catv.mp4'], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/la.txt', '-c', 'copy', f'{tmp}/cata.wav'], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{tmp}/catv.mp4', '-i', f'{tmp}/cata.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'pcm_s16le', f'{tmp}/cat.mov'], check=True)
    # 2) 무드 25% → 3) 화 제목
    subprocess.run(['python3', 'tools/mood.py', f'{tmp}/cat.mov', f'{tmp}/mood.mov'], check=True, capture_output=True)
    src = f'{tmp}/mood.mov'
    if spec.get('title'):
        ko, en, st, du = spec['title']
        subprocess.run(['python3', 'tools/title_card.py', src, f'{tmp}/title.mp4', ko, en, '--start', str(st), '--dur', str(du)], check=True, capture_output=True); src = f'{tmp}/title.mp4'
    # 4) 배경음 (대사 구간부터 작게) + 5) 릴스 틀 · 컷별 자막
    total = t; title = (spec.get('reel_title') or (spec['title'][0] if spec.get('title') else ''), spec.get('reel_title_en', ''))
    times.sort(); filled, cur = [], 0.0                 # 자막 빈 구간도 채움 → 위 제목은 처음부터 끝까지 그대로
    for a0, b0, ko, en in times:
        if a0 > cur + 1e-3: filled.append((cur, a0, '', ''))
        filled.append((a0, b0, ko, en)); cur = max(cur, b0)
    if cur < total - 1e-3: filled.append((cur, total, '', ''))
    times = filled
    pngs = []
    for i, (a, b, ko, en) in enumerate(times):
        hide = any(x - 1e-3 <= a and b <= y + 1e-3 for x, y in no_title)
        frame_png(f'{tmp}/f{i}.png', ('', '') if hide else title, ko, en); pngs.append((a, b))
    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', src] + sum([['-i', f'{tmp}/f{i}.png'] for i in range(len(pngs))], [])
    fc = f'[0:v]pad={W}:{H}:0:{TOP}:black[v0];'
    for i, (a, b) in enumerate(pngs):
        fc += f"[v{i}][{i + 1}:v]overlay=0:0:enable='between(t,{a:.3f},{b - 0.001:.3f})'[v{i + 1}];"
    vlast = f'[v{len(pngs)}]'
    # 효과음 · 배경음 구간: spec["sfx"] = [["파일", "컷 이름 일부", 컷 안 초, 볼륨, (길이, 페이드인, 페이드아웃, 파일 시작초)], ...]
    sfx = []
    for e in spec.get('sfx', []):                     # [파일, 컷 이름 일부, 컷 안에서 초, 볼륨] → 전체 시간으로
        f, cut, off, vol, *x = e; st = next(a for (a, b), c in zip(cut_times, spec['cuts']) if cut in c['file']); sfx.append((f, st + off, vol, x))
    if spec.get('bed'):                               # 배경음 바닥: 곡의 좋은 구간을 이어 깔고(크로스페이드) 대사 컷에서만 살짝 낮춤 (혁 10/29)
        import numpy as np, wave
        b = spec['bed']; SRb = 44100
        y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', b['file'], '-ac', '2', '-ar', str(SRb), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).reshape(-1, 2)
        seg = y[int(b['from'] * SRb):int(b['to'] * SRb)]; xf = int(0.6 * SRb); bed = seg.copy()
        while len(bed) < total * SRb + SRb:
            r = np.linspace(0, 1, xf)[:, None]; bed = np.concatenate([bed[:-xf], bed[-xf:] * (1 - r) + seg[:xf] * r, seg[xf:]])
        bed = bed[:int(total * SRb)]; tt = np.arange(len(bed)) / SRb; duck = np.zeros(len(bed))
        for (a0, b0), c in zip(cut_times, spec['cuts']):
            if any(k in c['file'] for k in b.get('duck_cuts', [])):
                duck = np.maximum(duck, np.clip((tt - a0 + 0.25) / 0.25, 0, 1) * np.clip((b0 + 0.25 - tt) / 0.25, 0, 1))
        g = b['vol'] - (b['vol'] - b['duck_vol']) * duck
        g *= np.clip(tt / 1.0, 0, 1) * np.clip((total - tt) / 1.5, 0, 1)            # 처음 페이드 인 · 끝 페이드 아웃
        bed = bed * g[:, None]
        with wave.open(f'{tmp}/bed.wav', 'w') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SRb); w.writeframes((np.clip(bed, -1, 1) * 32767).astype(np.int16).tobytes())
        sfx.append((f'{tmp}/bed.wav', 0.0, 1.0, []))
    si0 = len(pngs) + 1
    for f, at, vol, x in sfx: cmd += ['-i', f]
    vmain = '0:a'
    if sfx:
        for k, (f, at, vol, x) in enumerate(sfx):
            # 배경음 구간도 같은 식: [파일, 컷, 컷 안 초, 볼륨, 길이, 페이드인, 페이드아웃, 파일 시작초] — 애니처럼 뚝 끊기게 하려면 페이드아웃 0.05
            pre = ''
            if x:
                ln, fi, fo, src = (list(x) + [0, 0, 0])[:4]
                pre = f"atrim=start={src}:duration={ln},asetpts=PTS-STARTPTS,afade=t=in:d={max(fi, 0.01)},afade=t=out:st={max(0, ln - max(fo, 0.01))}:d={max(fo, 0.01)},"
            fc += f"[{si0 + k}:a]aformat=sample_rates=44100:channel_layouts=stereo,{pre}volume={vol},adelay={int(at * 1000)}:all=1,apad[s{k}];"
        fc += '[0:a]' + ''.join(f'[s{k}]' for k in range(len(sfx))) + f'amix=inputs={len(sfx) + 1}:duration=first:normalize=0[am];'; vmain = '[am]'
    if spec.get('bgm'):
        cmd += ['-i', spec['bgm']]; bi = si0 + len(sfx)
        vol, duck, df = spec.get('bgm_vol', 0.5), spec.get('bgm_duck', 0.18), spec.get('duck_from', total)
        until = spec.get('bgm_until', total)  # 이 초까지만 배경음 (끝 0.8초 페이드 아웃)
        fc += (f"[{bi}:a]atrim=0:{until},volume='if(lt(t,{df}),{vol},{duck})':eval=frame,afade=t=out:st={max(0, until - 0.8)}:d=0.8,apad[bg];"
               f"{vmain if vmain != '0:a' else '[0:a]'}[bg]amix=inputs=2:duration=first:normalize=0[a]")
        amap = '[a]'
    else:
        amap = vmain
    cmd += ['-filter_complex', fc.rstrip(';'), '-map', vlast, '-map', amap, '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', out]
    subprocess.run(cmd, check=True)
    # 릴스 소리 크기 맞춤 (-14 LUFS · 폰에서 작게 안 들리게)
    os.replace(out, f'{tmp}/pre.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{tmp}/pre.mp4', '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '192k', out], check=True)
    print(out, round(total, 1), 's'); [print(f'  {round(a, 2):6.2f}~{round(b, 2):6.2f}  {k}') for a, b, k, _ in times]


if __name__ == '__main__':
    main()
