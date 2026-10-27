"""릴스 틀 — 9:16 검정 · 위 제목 · 가운데 4:3 그림/영상 자리 · 아래 자막(한글 + 영어). 크레딧 0.
README '릴스 틀 확정' 값: 영상 1080x810 을 위에서 420px · 제목 주아 120px 노랑 · 자막 Gothic A1 800 66px 흰 기울임 + 영어 40px 초록 기울임.
usage: python3 tools/reel_frame.py 그림.png out.jpg "제목" "한글 자막" "영어 자막" [--guide]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H, TOP, VH = 1080, 1920, 420, 810
FJ, FG = 'tools/fonts/jua.ttf', 'tools/fonts/ga1-800.ttf'


def slanted(o, text, font, fill, y, x_right_pad=30):
    d = ImageDraw.Draw(o)
    tw = int(d.textlength(text, font=font)) + 60
    layer = Image.new('RGBA', (tw, font.size + 40), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((30, 8), text, font=font, fill=fill, stroke_width=2, stroke_fill=(0, 0, 0))
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0.18, -0.18 * layer.height / 2, 0, 1, 0), Image.BICUBIC)
    o.paste(layer, ((W - tw) // 2 - x_right_pad, y), layer)


def frame(src, out, title, ko, en, guide=False):
    o = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(o)
    im = Image.open(src).convert('RGB')
    w, h = im.size; tw = min(w, int(h * 4 / 3)); th = int(tw * 3 / 4)
    im = im.crop(((w - tw) // 2, (h - th) // 2, (w - tw) // 2 + tw, (h - th) // 2 + th)).resize((W, VH), Image.LANCZOS)
    o.paste(im, (0, TOP))
    ft = ImageFont.truetype(FJ, 120)
    tw_ = d.textlength(title, font=ft); d.text(((W - tw_) / 2, TOP - 50 - 130), title, font=ft, fill=(255, 228, 92))
    slanted(o, ko, ImageFont.truetype(FG, 66), (255, 255, 255), TOP + VH + 30)
    slanted(o, en, ImageFont.truetype(FG, 40), (57, 255, 20), TOP + VH + 120)
    if guide:  # 인스타 UI 가 덮는 곳
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.rectangle((0, 0, W, 220), fill=(255, 0, 0, 70)); gd.rectangle((0, H - 420, W, H), fill=(255, 0, 0, 70))
        gd.rectangle((W - 140, 900, W, H - 420), fill=(255, 0, 0, 70))
        o = Image.alpha_composite(o.convert('RGBA'), g).convert('RGB')
        ImageDraw.Draw(o).text((20, 160), '인스타 UI 가림(비움)', font=ImageFont.truetype(FG, 34), fill=(255, 160, 160))
    o.save(out, quality=92); print(out)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--guide']
    frame(*a[:5], guide='--guide' in sys.argv)
