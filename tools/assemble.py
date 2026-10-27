"""컷 이어붙이기 → 무드 25% → 화 제목 얹기 → 배경음 깔기(대사 땐 작게) → 9:16 릴스 틀 + 컷마다 자막. 크레딧 0.
usage: python3 tools/assemble.py spec.json out.mp4
spec = {"title": ["두 얼굴", "TWO FACES", 시작초, 길이초],
        "bgm": "brand/bgm/opening-A.mp3", "bgm_vol": 0.5, "bgm_duck": 0.18, "duck_from": 5.9,
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
    ft = ImageFont.truetype(FJ, 120); tw = d.textlength(title, font=ft); d.text(((W - tw) / 2, TOP - 180), title, font=ft, fill=(255, 228, 92))
    if ko: slanted(o, ko, ImageFont.truetype(FG, 66), (255, 255, 255), TOP + VH + 30)
    if en: slanted(o, en, ImageFont.truetype(FG, 40), (57, 255, 20), TOP + VH + 120)
    o.save(path)


def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; tmp = tempfile.mkdtemp()
    # 1) 컷마다 같은 크기 · fps · 소리 형식으로
    parts, times, t = [], [], 0.0
    for i, c in enumerate(spec['cuts']):
        p = f'{tmp}/p{i}.mp4'; d = c.get('sec') or dur(c['file'])
        cmd = ['ffmpeg', '-y', '-v', 'error', '-i', c['file']]
        if not has_audio(c['file']): cmd += ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']
        cmd += ['-t', str(d), '-vf', f'scale=1080:810,fps={FPS},setsar=1', '-map', '0:v', '-map', '0:a' if has_audio(c['file']) else '1:a',
                '-ar', '44100', '-ac', '2', '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', p]
        subprocess.run(cmd, check=True); parts.append(p); times.append((t, t + d, c.get('ko', ''), c.get('en', ''))); t += d
    open(f'{tmp}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/l.txt', '-c', 'copy', f'{tmp}/cat.mp4'], check=True)
    # 2) 무드 25% → 3) 화 제목
    subprocess.run(['python3', 'tools/mood.py', f'{tmp}/cat.mp4', f'{tmp}/mood.mp4'], check=True, capture_output=True)
    src = f'{tmp}/mood.mp4'
    if spec.get('title'):
        ko, en, st, du = spec['title']
        subprocess.run(['python3', 'tools/title_card.py', src, f'{tmp}/title.mp4', ko, en, '--start', str(st), '--dur', str(du)], check=True, capture_output=True); src = f'{tmp}/title.mp4'
    # 4) 배경음 (대사 구간부터 작게) + 5) 릴스 틀 · 컷별 자막
    total = t; title = spec.get('reel_title') or (spec['title'][0] if spec.get('title') else '')
    pngs = []
    for i, (a, b, ko, en) in enumerate(times):
        frame_png(f'{tmp}/f{i}.png', title, ko, en); pngs.append((a, b))
    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', src] + sum([['-i', f'{tmp}/f{i}.png'] for i in range(len(pngs))], [])
    fc = f'[0:v]pad={W}:{H}:0:{TOP}:black[v0];'
    for i, (a, b) in enumerate(pngs):
        fc += f"[v{i}][{i + 1}:v]overlay=0:0:enable='between(t,{a:.3f},{b - 0.001:.3f})'[v{i + 1}];"
    vlast = f'[v{len(pngs)}]'
    if spec.get('bgm'):
        cmd += ['-i', spec['bgm']]; bi = len(pngs) + 1
        vol, duck, df = spec.get('bgm_vol', 0.5), spec.get('bgm_duck', 0.18), spec.get('duck_from', total)
        fc += (f"[{bi}:a]atrim=0:{total},volume='if(lt(t,{df}),{vol},{duck})':eval=frame,afade=t=out:st={max(0, total - 1)}:d=1[bg];"
               f"[0:a][bg]amix=inputs=2:duration=first:normalize=0[a]")
        amap = '[a]'
    else:
        amap = '0:a'
    cmd += ['-filter_complex', fc.rstrip(';'), '-map', vlast, '-map', amap, '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', out]
    subprocess.run(cmd, check=True)
    print(out, round(total, 1), 's')


if __name__ == '__main__':
    main()
