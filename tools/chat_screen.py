"""모니터 메신저 화면 (우리만의 디자인 · 셀 애니 느낌) — 크레딧 0. 글씨가 안 깨지게 그림 대신 편집으로.
usage: python3 tools/chat_screen.py out.png [--delete]   (--delete: 마지막 말풍선 선택 + '삭제하시겠습니까?' 창)
       [--deleted]  (마지막 말풍선 없이 '메시지를 삭제했습니다' 안내)
       python3 tools/chat_screen.py out.mp4 --typing  (TYPE_FROM 번째부터 입력창에 한 글자씩 쳐서 전송하는 영상)
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
    ('me', '어우 졸려...', '오전 10:00'),
    ('me', '퇴사 마렵다..', '오전 10:00'),
]
UNREAD = 2      # 끝에서 몇 개가 안 읽은 내 메시지(옆에 1)
TYPE_FROM = 6   # --typing: CHAT 에서 이 번호부터 직접 타자
W, H = 2336, 1744
F = 'tools/fonts/ga1-800.ttf'
INK = (40, 30, 40)
f = lambda s: ImageFont.truetype(F, s)


def bubble(d, x, y, text, mine, font):
    tw = d.textlength(text, font=font); pad = 34
    w, h = tw + pad * 2, font.size + pad * 1.4
    if mine: x = x - w
    d.rounded_rectangle((x, y, x + w, y + h), 38, fill=(255, 196, 200) if mine else (255, 255, 255), outline=INK, width=6)
    d.text((x + pad, y + h / 2), text, font=font, fill=INK, anchor='lm')  # 말풍선 세로 가운데
    return x, y, w, h


def draw(chat_src=CHAT, mode='', typing='', caret=False):
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
    d.text((wx0 + 140, wy0 + 66), FRIEND, font=f(58), fill=INK, anchor='lm')
    for i in range(3): d.ellipse((wx1 - 80 - i * 50, wy0 + 52, wx1 - 56 - i * 50, wy0 + 76), fill=INK)
    # 대화
    fb, ft, fd = f(54), f(30), f(32)
    y = wy0 + 170; last = None
    chat = chat_src[:-1] if mode == '--deleted' else chat_src
    unread = {id(x) for x in CHAT[-UNREAD:]}
    for item in chat:
        if item[0] == 'date':
            tw = d.textlength(item[1], font=fd); cx = (wx0 + wx1) / 2
            d.rounded_rectangle((cx - tw / 2 - 30, y, cx + tw / 2 + 30, y + 54), 27, fill=(210, 206, 220))
            d.text((cx, y + 27), item[1], font=fd, fill=(90, 80, 100), anchor='mm'); y += 86; continue
        who, text, t = item; mine = who == 'me'
        bx, by, bw, bh = bubble(d, wx1 - 50 if mine else wx0 + 50, y, text, mine, fb)
        tt = d.textlength(t, font=ft)
        tx = bx - tt - 16 if mine else bx + bw + 16
        d.text((tx, by + bh - 8), t, font=ft, fill=(120, 110, 130), anchor='ld')  # 말풍선 아래 선에 맞춤
        last = (bx, by, bw, bh, tx)
        if id(item) in unread: d.text((tx + 4, by + bh - 46), '1', font=f(44), fill=(240, 150, 40), anchor='ld')  # 안 읽음
        y += bh + 34
    if mode == '--deleted':
        msg = '메시지를 삭제했습니다'; tw = d.textlength(msg, font=fd); cx = (wx0 + wx1) / 2
        d.rounded_rectangle((cx - tw / 2 - 30, y, cx + tw / 2 + 30, y + 58), 29, fill=(210, 206, 220))
        d.text((cx, y + 29), msg, font=fd, fill=(90, 80, 100), anchor='mm')
    # 입력창
    d.rounded_rectangle((wx0 + 30, wy1 - 120, wx1 - 30, wy1 - 30), 40, fill=(255, 255, 255), outline=INK, width=6)
    tx0, iy = wx0 + 70, wy1 - 75; d.text((tx0, iy), typing, font=fb, fill=INK, anchor='lm')  # 입력창 세로 가운데
    if caret:
        cx = tx0 + d.textlength(typing, font=fb) + 6; d.rectangle((cx, iy - 30, cx + 6, iy + 30), fill=INK)
    if mode == '--delete' and last:
        bx, by, bw, bh, _ = last
        d.rounded_rectangle((bx - 10, by - 10, bx + bw + 10, by + bh + 10), 44, outline=(80, 140, 230), width=10)
        dx0, dy0, dx1, dy1 = (W - 1000) // 2, H // 2 - 230, (W + 1000) // 2, H // 2 + 230
        d.rounded_rectangle((dx0 + 16, dy0 + 20, dx1 + 16, dy1 + 20), 34, fill=(150, 150, 170))
        d.rounded_rectangle((dx0, dy0, dx1, dy1), 34, fill=(255, 255, 255), outline=INK, width=9)
        q = '메시지를 삭제하시겠습니까?'; tw = d.textlength(q, font=f(64))
        d.text((W / 2, dy0 + 140), q, font=f(64), fill=INK, anchor='mm')
        for i, (lab, col) in enumerate([('취소', (225, 222, 232)), ('삭제', (255, 120, 120))]):
            x0 = dx0 + 90 + i * 430
            d.rounded_rectangle((x0, dy1 - 170, x0 + 390, dy1 - 60), 30, fill=col, outline=INK, width=7)
            d.text((x0 + 195, dy1 - 115), lab, font=f(58), fill=INK, anchor='mm')
    # 90년대 화면 느낌: 살짝 부드럽게 + 그레인
    o = o.filter(ImageFilter.GaussianBlur(0.8))
    return o


def grain(o, seed=3):
    a = np.asarray(o).astype(np.float32) + np.random.default_rng(seed).normal(0, 4, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def typing_video(out, fps=24, size=(1080, 810)):
    """옛날 애니처럼 초당 8번만 바뀜: 한 글자 = 3프레임(0.125초), 전송 전후 잠깐 멈춤."""
    import os, subprocess, tempfile
    tmp = tempfile.mkdtemp(); frames = []
    def hold(img, n): frames.extend([img] * n)
    shown = CHAT[:TYPE_FROM]
    hold(draw(shown, caret=True), 12)
    for item in CHAT[TYPE_FROM:]:
        text = item[1]
        for k in range(1, len(text) + 1):
            hold(draw(shown, typing=text[:k], caret=True), 3)
        hold(draw(shown, typing=text, caret=True), 8)
        shown = shown + [item]
        hold(draw(shown, caret=True), 14)
    hold(draw(shown, caret=False), 12)
    cache = {}
    for i, img in enumerate(frames):
        k = id(img)
        if k not in cache: cache[k] = grain(img, i // 3).resize(size, Image.LANCZOS)
        cache[k].save(f'{tmp}/{i:05d}.jpg', quality=92)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(fps), '-i', f'{tmp}/%05d.jpg', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', out], check=True)
    print(out, round(len(frames) / fps, 1), 's')


def main():
    out = sys.argv[1]
    if '--typing' in sys.argv: return typing_video(out)
    mode = '--delete' if '--delete' in sys.argv else '--deleted' if '--deleted' in sys.argv else ''
    grain(draw(mode=mode)).save(out); print(out)


if __name__ == '__main__':
    main()
