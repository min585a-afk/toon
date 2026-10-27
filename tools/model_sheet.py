"""귤이 캐릭터 도안(모델 시트) — 확정 에셋을 한 장에 배치. 크레딧 0.
가운데 평소 복장 전신 · 왼쪽 턴어라운드 · 오른쪽 얼굴 각도 · 아래 표정 · SD · 입 모양.
usage: python3 model_sheet.py out.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont
V = 'char/gyul/'
F = 'tools/fonts/ga1-800.ttf'
CW, CH = 3600, 3300
o = Image.new('RGB', (CW, CH), (246, 242, 234)); d = ImageDraw.Draw(o)
ft = ImageFont.truetype(F, 70); fh = ImageFont.truetype(F, 40); fs = ImageFont.truetype(F, 28)
def put(path, x, y, w, h, label=None, frame=True):
    im = Image.open(path).convert('RGB'); im.thumbnail((w, h), Image.LANCZOS)
    px, py = x + (w - im.width) // 2, y + (h - im.height) // 2
    if frame: d.rectangle((x - 3, y - 3, x + w + 3, y + h + 3), fill=(255, 255, 255), outline=(60, 50, 50), width=3)
    o.paste(im, (px, py))
    if label: d.text((x, y + h + 8), label, font=fs, fill=(60, 50, 50))
d.text((60, 40), '귤이 · 캐릭터 도안', font=ft, fill=(40, 30, 30))
d.text((60, 130), '앞에선 천사, 뒤에선 현실 · 90년대 TV 셀 애니 · 2026 오피스룩 · 약 4등신', font=fh, fill=(110, 90, 90))
# 가운데 전신
put(V + 'base/outfit-2026.png', 1250, 220, 1100, 1470, '평소 복장 (기준)')
# 왼쪽 턴어라운드 (흰 배경)
d.text((60, 220), '턴어라운드', font=fh, fill=(40, 30, 30))
turns = [('turn/1-left34.png', '좌 3/4'), ('turn/2-front.png', '정면'), ('turn/3-right34.png', '우 3/4'),
         ('turn/4-side.png', '옆'), ('turn/5-back.png', '뒤')]
for i, (f, l) in enumerate(turns):
    x = 60 + (i % 3) * 385; y = 290 + (i // 3) * 720
    put(V + f, x, y, 360, 660, l)
# 오른쪽 얼굴
d.text((2450, 220), '얼굴', font=fh, fill=(40, 30, 30))
faces = [('face/front.png', '정면'), ('face/left34.png', '3/4'), ('face/side.png', '옆')]
for i, (f, l) in enumerate(faces):
    put(V + f, 2450, 290 + i * 470, 540, 405, l)
d.text((3040, 220), '입 (대사용)', font=fh, fill=(40, 30, 30))
for i, (f, l) in enumerate([('talk/smile-mouth-1-closed.png', '다문'), ('talk/smile-mouth-2-half.png', '반'), ('talk/smile-mouth-3-open.png', '벌린')]):
    im = Image.open(V + f).convert('RGB').crop((880, 800, 1440, 1360)).save('/tmp/claude-0/-home-user-toon/3b6de269-8feb-5c3c-bc5e-f1bd20545e4c/scratchpad/_m.png')
    put('/tmp/claude-0/-home-user-toon/3b6de269-8feb-5c3c-bc5e-f1bd20545e4c/scratchpad/_m.png', 3040, 290 + i * 470, 500, 405, l)
# 아래 표정
y0 = 1790; d.text((60, y0), '표정', font=fh, fill=(40, 30, 30))
exps = [('01-angel', '천사 반짝'), ('02-hehe', '^^'), ('03-dark', '그림자 무표정'), ('04-angry', '핏대'), ('05-curse', '욕'), ('06-shock', '충격'), ('07-cry', '폭포 눈물'),
        ('08-sad', '슬픔'), ('09-surprised', '놀람'), ('10-shadow', '눈 가린 그림자'), ('11-shy', '수줍음'), ('12-flutter', '설렘'), ('13-teary', '눈물 맺힘'),
        ('14-blank', '멍때림 · 혼'), ('15-sleepy', '졸림'), ('16-pout', '삐짐'), ('17-squint', '실눈 의심')]
for i, (f, l) in enumerate(exps):
    x = 60 + (i % 7) * 500; y = y0 + 60 + (i // 7) * 380
    put(V + f'exp/{f}.png', x, y, 470, 330, l)
# SD
xs = 60 + 6 * 500; ys = y0 + 60 + 380
d.text((2060, y0 + 60 + 2 * 380 + 10), 'SD 개그', font=fh, fill=(40, 30, 30))
for i, f in enumerate(['01-stomp', '02-flail', '03-run']):
    put(V + f'sd/{f}.png', 2060 + i * 500, y0 + 60 + 2 * 380 + 70, 470, 330)
o.save(sys.argv[1]); print(sys.argv[1])
