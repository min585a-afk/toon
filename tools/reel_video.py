"""릴스 틀 영상판 — 4:3 영상을 9:16 검정 틀 가운데에 + 위 제목 + 아래 자막(한글+영어). 크레딧 0. 값은 reel_frame.py 와 같음.
usage: python3 tools/reel_video.py in.mp4 out.mp4 "제목" "한글 자막" "영어 자막"
"""
import subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, 'tools')
from reel_frame import W, H, TOP, VH, FJ, FG, slanted


def main():
    src, out, title, ko, en = sys.argv[1:6]
    o = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(o)
    d.rectangle((0, TOP, W, TOP + VH), fill=(0, 0, 0, 0))  # 영상 자리 비움
    ft = ImageFont.truetype(FJ, 120); tw = d.textlength(title, font=ft)
    d.text(((W - tw) / 2, TOP - 50 - 130), title, font=ft, fill=(255, 228, 92))
    if ko: slanted(o, ko, ImageFont.truetype(FG, 66), (255, 255, 255), TOP + VH + 30)
    if en: slanted(o, en, ImageFont.truetype(FG, 40), (57, 255, 20), TOP + VH + 120)
    tmp = tempfile.mkdtemp(); o.save(f'{tmp}/frame.png')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-i', f'{tmp}/frame.png', '-filter_complex',
                    f'[0:v]scale={W}:{VH}:force_original_aspect_ratio=increase,crop={W}:{VH},pad={W}:{H}:0:{TOP}:black[v];[v][1:v]overlay=0:0',
                    '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', out], check=True)
    print(out)


if __name__ == '__main__':
    main()
