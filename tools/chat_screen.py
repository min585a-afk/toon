"""모니터 메신저 화면 (우리만의 디자인 · 셀 애니 느낌) — 크레딧 0. 글씨가 안 깨지게 그림 대신 편집으로.
usage: python3 tools/chat_screen.py out.png [--delete]   (--delete: 마지막 말풍선 선택 + '삭제하시겠습니까?' 창)
       [--deleted]  (마지막 말풍선 없이 '메시지를 삭제했습니다' 안내)
대화 내용은 아래 CHAT 을 고쳐서 씀. 'me' = 귤이(오른쪽 분홍), 'you' = 친구(왼쪽 흰색).
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FRIEND = '지은'
CHAT = [
    ('date', '어제'),
    ('you', '잘 들어갔어?', '오후 11:42'),
    ('me', '응', '오후 11:43'),
    ('date', '오늘'),
    ('me', '아.. 출근했어..', '오전 9:58'),
    ('you', '나도...', '오전 9:59'),
    ('me', '일하기 싫다..', '오전 10:00'),
    ('me', '아 퇴사하고 싶다.. 증말.. 다들 일만 줘', '오전 10:00'),
]
W, H = 2336, 1744
F = 'tools/fonts/ga1-800.ttf'
INK = (40, 30, 40)
f = lambda s: ImageFont.truetype(F, s)


def bubble(d, x, y, text, mine, font):
    tw = d.textlength(text, font=font); pad = 34
    w, h = tw + pad * 2, font.size + pad * 1.4
    if mine: x = x - w
    d.rounded_rectangle((x, y, x + w, y + h), 38, fill=(255, 196, 200) if mine else (255, 255, 255), outline=INK, width=6)
    d.text((x + pad, y + pad * 0.55), text, font=font, fill=INK)
    return x, y, w, h


def main():
    mode = '--delete' if '--delete' in sys.argv else '--deleted' if '--deleted' in sys.argv else ''
    o = Image.new('RGB', (W, H), (214, 205, 228)); d = ImageDraw.Draw(o)
    # 모니터 테두리 (셀 선)
    d.rounded_rectangle((60, 40, W - 60, H - 40), 60, fill=(196, 198, 214), outline=INK, width=12)
    sx0, sy0, sx1, sy1 = 170, 140, W - 170, H - 150
    d.rectangle((sx0, sy0, sx1, sy1), fill=(236, 240, 250), outline=INK, width=8)
    # 메신저 창
    wx0, wy0, wx1, wy1 = 430, 190, W - 430, H - 200
    d.rounded_rectangle((wx0 + 14, wy0 + 18, wx1 + 14, wy1 + 18), 30, fill=(180, 184, 205))
    d.rounded_rectangle((wx0, wy0, wx1, wy1), 30, fill=(250, 246, 240), outline=INK, width=8)
    d.rounded_rectangle((wx0, wy0, wx1, wy0 + 130), 30, fill=(168, 196, 236), outline=INK, width=8)
    d.rectangle((wx0 + 4, wy0 + 100, wx1 - 4, wy0 + 126), fill=(168, 196, 236))
    d.line((wx0, wy0 + 130, wx1, wy0 + 130), fill=INK, width=8)
    d.ellipse((wx0 + 36, wy0 + 26, wx0 + 116, wy0 + 106), fill=(255, 226, 150), outline=INK, width=6)
    d.text((wx0 + 140, wy0 + 34), FRIEND, font=f(58), fill=INK)
    for i in range(3): d.ellipse((wx1 - 80 - i * 50, wy0 + 52, wx1 - 56 - i * 50, wy0 + 76), fill=INK)
    # 대화
    fb, ft, fd = f(54), f(30), f(32)
    y = wy0 + 170; last = None
    chat = CHAT[:-1] if mode == '--deleted' else CHAT
    for item in chat:
        if item[0] == 'date':
            tw = d.textlength(item[1], font=fd); cx = (wx0 + wx1) / 2
            d.rounded_rectangle((cx - tw / 2 - 30, y, cx + tw / 2 + 30, y + 54), 27, fill=(210, 206, 220))
            d.text((cx - tw / 2, y + 8), item[1], font=fd, fill=(90, 80, 100)); y += 86; continue
        who, text, t = item; mine = who == 'me'
        bx, by, bw, bh = bubble(d, wx1 - 50 if mine else wx0 + 50, y, text, mine, fb)
        tt = d.textlength(t, font=ft)
        tx = bx - tt - 16 if mine else bx + bw + 16
        d.text((tx, by + bh - 40), t, font=ft, fill=(120, 110, 130))
        last = (bx, by, bw, bh, tx)
        y += bh + 34
    if mode != '--deleted' and last:
        bx, by, bw, bh, tx = last  # 안 읽음 1
        d.text((tx + 10, by + bh - 86), '1', font=f(44), fill=(240, 150, 40))
    if mode == '--deleted':
        msg = '메시지를 삭제했습니다'; tw = d.textlength(msg, font=fd); cx = (wx0 + wx1) / 2
        d.rounded_rectangle((cx - tw / 2 - 30, y, cx + tw / 2 + 30, y + 58), 29, fill=(210, 206, 220))
        d.text((cx - tw / 2, y + 10), msg, font=fd, fill=(90, 80, 100))
    # 입력창
    d.rounded_rectangle((wx0 + 30, wy1 - 120, wx1 - 30, wy1 - 30), 40, fill=(255, 255, 255), outline=INK, width=6)
    if mode == '--delete' and last:
        bx, by, bw, bh, _ = last
        d.rounded_rectangle((bx - 10, by - 10, bx + bw + 10, by + bh + 10), 44, outline=(80, 140, 230), width=10)
        dx0, dy0, dx1, dy1 = (W - 1000) // 2, H // 2 - 230, (W + 1000) // 2, H // 2 + 230
        d.rounded_rectangle((dx0 + 16, dy0 + 20, dx1 + 16, dy1 + 20), 34, fill=(150, 150, 170))
        d.rounded_rectangle((dx0, dy0, dx1, dy1), 34, fill=(255, 255, 255), outline=INK, width=9)
        q = '메시지를 삭제하시겠습니까?'; tw = d.textlength(q, font=f(64))
        d.text(((W - tw) / 2, dy0 + 90), q, font=f(64), fill=INK)
        for i, (lab, col) in enumerate([('취소', (225, 222, 232)), ('삭제', (255, 120, 120))]):
            x0 = dx0 + 90 + i * 430
            d.rounded_rectangle((x0, dy1 - 170, x0 + 390, dy1 - 60), 30, fill=col, outline=INK, width=7)
            lw = d.textlength(lab, font=f(58)); d.text((x0 + (390 - lw) / 2, dy1 - 158), lab, font=f(58), fill=INK)
    # 90년대 화면 느낌: 살짝 부드럽게 + 그레인
    o = o.filter(ImageFilter.GaussianBlur(0.8))
    a = np.asarray(o).astype(np.float32) + np.random.default_rng(3).normal(0, 4, (H, W, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(sys.argv[1]); print(sys.argv[1])


if __name__ == '__main__':
    main()
