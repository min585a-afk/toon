# EP01 「두 얼굴」 전체 콘티 (10/27 혁 피드백 반영판)

한 줄: 팀장이 일 던짐 → 앞에선 천사 "넵!" → 뒤돌자 정색 빠직 → 팀장 확 돌아봄 → 0.1초 만에 천사 미소 → 신나게 타자 → 메모장 凸凸凸.
길이 약 20초 (인트로 6초 + 본편 약 14초) · 4:3 그림을 9:16 릴스 틀 안에 · 마지막에 무드 25%.

---
## 0. 모든 컷에 공통으로 들어가는 것

### 그림 프롬프트 공통 꼬리 (STY) — 새 그림은 항상 끝에 붙임
```
Early-1990s Japanese TV cel anime frame: characters with BOLD solid black outlines, flat saturated cel colors,
one hard shadow, exactly the face and line style of the reference characters; soft hand-painted pastel office
background with no outlines. Film grain. 4:3 frame. No text, no letters, no logos.
```
- 모델: **GPT Image 2.5 · medium · 2k · 4:3** (1cr). 레퍼런스 순서 = 캐릭터 기준 그림 → 옷 → 배경/이전 컷.
- 편집은 기준 그림에서 1번만. 바꿀 곳만 말하고 "Keep everything else pixel-identical".
- 부분만 바뀌어야 하면 편집본에서 그 부분(머리·얼굴 등)만 오려서 원본에 합침(나머지 흔들림 방지).

### 팀장 묘사 (B) — 팀장 나오는 컷마다 그대로
```
the strict female team manager (exactly as in the manager reference: tall slim woman in her 40s, sleek sharp
black bob, thin rectangular glasses with white glint, cold expressionless face, navy suit and pencil skirt)
```
레퍼런스: `char/boss/face/front-full.png` · `char/boss/base/outfit.png`. **표정은 처음부터 끝까지 냉정한 무표정.**

### 귤이
기준 `char/gyul/face/front.png`. 앞 천사(반짝 눈·볼 빗금·활짝) / 뒤 찐 직장인(정색·그림자). 빨강 니트 가디건 · 흰 티 · 목걸이 명찰.

### 연출 규칙
| 항목 | 규칙 |
|---|---|
| 카메라 | **컷으로만 넘김.** 줌인·줌아웃 없음 (인트로 틸트 업만 예외) |
| 움직임 | 초당 8장(3코마) 기본, 빠른 동작만 12장. 대사 중엔 몸 멈추고 입·눈만 |
| 충격 | 흰 번쩍 1장 · 화면 살짝 흔들 2~3장 |
| 효과 글자 | **손글씨 `brand/sfx/ppajik.png`(빠직)만** 화면에 씀. 휙·반짝 같은 글자는 넣지 않음 (혁 10/27) |
| 반짝이 | 글자가 아니라 **효과**: 세로로 긴 4갈래 별 + 금빛 번짐 + 흰 중심, 커졌다 작아지며 깜빡 (`build_c6.py` `star()`) |
| 효과음 | 장면에 딱 맞게 · `tools/sfx_sound.py` (sparkle · bloom · rage · whoosh · ting) |
| 마무리 | 전체 이어붙인 뒤 `tools/mood.py` 25% → `tools/reel_frame.py` (제목 **두 얼굴** · 자막 한글+영어) |

### 대사 영상 공통 (MiniMax H3 · 5초 10cr)
```
higgsfield generate create minimax_h3 --prompt "<대사 프롬프트> $VSTY" \
  --image-references <그림> --audio-references voice/ref/<gyul|boss>-h3.wav --duration 5 --wait
```
```
VSTY = Use the exact same voice as the reference audio. Keep the exact drawing style, character design and
colors of the reference image: early-1990s Japanese TV cel anime, bold black outlines, flat cel colors. Simple
limited animation like an old TV cartoon, the mouth opens and closes while talking, small natural blinks.
Camera completely still. No music, no text, no subtitles.
```
후처리: `fps=8,fps=24` (옛날 애니 끊김) · `highpass=f=200,lowpass=f=6000` · 대사 끝나면 바로 자름.

---
## 컷별 콘티

### 컷 0 · 인트로 (6.0초) ✅
- **화면**: 회사 앞, 반투명 동글 실루엣 출근 인파 오감 → 빌딩 위로 틸트 업(12fps 끊김) → 제목 「두 얼굴」 + TWO FACES (나눔명조, 얇은 테두리만 · 그림자 없음, EP 표기 없음) → 컷 → 팀장이 서류 들고 통로 따라 걸어옴.
- **그림**: `bg/office-building-tall.png` · `ep01b/c0-boss-walk.png`
  - c0 프롬프트: `long shot down the office aisle of the SECOND image: B walks straight TOWARD the viewer down the aisle between desks, carrying a thick stack of documents in her arms, firm determined stride` + STY (ref: outfit, c3-boss-leave, front-full)
- **소리**: 발소리 · 제목 "딩~" · 또각또각
- **만들기**: `python3 ep01b/build_intro.py` → `ep01b/intro.mp4`

### 컷 1 · 팀장 "이것 오늘까지 좀 부탁해요." (약 2.3초) ⬜ H3 10cr
- **화면**: 책상 옆에서 서류 뭉치를 두 손으로 내미는 팀장, 냉정한 무표정, 안경 하얗게 번쩍.
- **그림**: `ep01b/c1-boss-papers.png` ✅
  - 프롬프트: `Medium shot in the office of the office reference: B stands next to the desk facing the viewer, holding out a thick stack of documents with both hands, cold and expressionless, as if handing over a big task.` + STY
- **대사 프롬프트(H3)**: `The stern female team manager holds out the documents with a cold expressionless face, her glasses glint, and says in Korean in a sharp, cutting, cold and precise voice — clipped, each syllable crisp like a blade, picky and authoritative, not loud: "이것 오늘까지 좀 부탁해요." Voiced like a strict, intimidating female boss in a 1990s Korean TV anime dub.` + VSTY · ref `voice/ref/boss-h3.wav`
- **효과/소리**: 서류 내밀 때 "툭" (종이 소리) · 효과 글자 없음
- **자막**: 이것 오늘까지 좀 부탁해요. / Could you get this done by today?

### 컷 2 · 귤이 천사 "네 알겠습니다!" (약 2.0초) ⬜ H3 10cr
- **화면**: 흰 번쩍 → 활짝 천사 웃음, 꽃이 하나씩 빙글 피어나고 금빛 별 반짝반짝.
- **그림**: `char/gyul/exp/01-angel-clean.png` ✅ (꽃·반짝이 뺀 판 — 효과는 영상 위에 직접 얹음)
- **대사 프롬프트(H3)**: `The girl smiles brightly with sparkling eyes and says in Korean in a bright, cheerful, high and lively voice, eager and overly sweet: "네 알겠습니다!" Voiced like a cheerful young heroine in a 1990s Korean TV anime dub.` + VSTY · ref `voice/ref/gyul-h3.wav`
- **효과**: H3 영상 위에 `build_c6.py` 의 꽃 피기 + 금빛 별 그대로 얹기 (꽃 8송이 2프레임 간격, 0 → 0.35 → 0.7 → 1.15 → 1.0 크기로 빙글 돌며 피고 멈춤, 필 때 옆에서 별 반짝)
- **소리**: 꽃 필 때마다 종소리 한 음씩 올라감 + 반짝 쉬머 (`ss.bloom`) — 대사 밑에 작게
- **자막**: 네 알겠습니다! / Yes, understood!

### 컷 3 · 팀장 뒤돌아 감 (약 1.2초) ✅그림 · ⬜편집 0cr
- **화면**: 통로 따라 멀어지는 팀장 뒷모습. 몸은 멈춘 그림, 컷 길이로만.
- **그림**: `ep01b/c3-boss-leave.png`
  - 프롬프트: `Full shot in the same office: B seen from BEHIND walking away down the aisle between desks, back straight, heels clicking, empty-handed.` + STY
- **소리**: 또각또각 (멀어지며 작아짐)

### 컷 4 · 정색 빠직 (1.6초) ✅
- **화면**: 웃음 싹 사라지고 정색 — 눈은 짙은 그림자로 가림, 입 일자. 뒤에서 만화식 불꽃 솟음 · 빨간 깜빡임(8fps) · 흔들림 · 머리 끝 일렁임 · 이마에 핏대(빨간 4갈래) 툭 · 왼쪽 위에 손글씨 **빠직** 툭 튀어나옴(커졌다 제자리).
- **그림**: `ep01b/c4-devil.png` (+ 배경 뺀 `c4-devil-cut.png`)
  - 프롬프트: `Edit the FIRST image (our own character …). Change her into a cold, dead-serious deadpan face: a deep solid dark shadow covers the entire upper half of her face from the bangs down to the nose so her eyes are completely hidden (like the SECOND image), mouth a flat tight straight line, no smile, no teeth, head slightly lowered, an ominous silent mood. Background replaced with a plain flat very dark red-black color (empty, so effects can be added later). Hair still hanging normally. Film grain. 4:3 frame. No text, no letters, no flames.` (ref: face/front, exp/10-shadow)
- **빠직 글자**: `brand/sfx/ppajik.png` — 혁 예시(번쩍) 스타일, GPT Image 2장에서 "빠"·"직"을 따로 골라 합침, 빠를 직 크기로. 흰 + 굵은 검정 테두리 + 진한 그림자.
- **소리**: 빠직 뜨는 순간 "쿵"(낮은 충격) + 날카로운 "빡" → "화르륵" 불 솟음 → 불티 타닥 (`ss.rage`)
- **만들기**: `python3 tools/rage_fx.py ep01b/c4-devil.png ep01b/c4-rage-fx.mp4 1.6`

### 컷 5 · 팀장 확 돌아봄 (2.0초) ✅
- **화면**: 귤이 자리 시점(앞에 모니터·책상 살짝), 통로 멀리 팀장이 등 돌리고 서 있음(0.67초) → **1장 번짐(머리 쪽 가로 블러 + 흰 속도선)** → 어깨 너머로 확 돌아본 얼굴 + 화면 살짝 흔들 + 안경 번쩍. 글자 없음.
- **그림**: 뒤통수 `ep01b/c5-boss-back.png` / 돌아봄 `ep01b/c5-boss-turn.png`
  - 돌아봄 프롬프트: `POV from the girl's desk: in the near foreground at the bottom-left, the edge of her computer monitor and desk with papers. Further away down the office aisle, SMALL in the frame, B is walking away with her BACK to the viewer, and she has stopped mid-step to sharply turn ONLY her head back over her shoulder, glaring at the viewer with a suspicious cold look, her glasses flashing white.` + STY
  - 뒤통수 프롬프트(편집): `Edit this exact image. Change ONLY the woman's head: she is looking straight ahead, away from the viewer, so we see only the back of her head — glossy black bob haircut seen from behind, no face, no glasses. Keep everything else pixel-identical.` → 머리 부분만 원본에 합침
- **소리**: "휙"(바람 가르는 소리) → 돌아보는 순간 "띵"(안경)
- **만들기**: `python3 ep01b/build_c5.py`

### 컷 6 · 0.1초 만에 천사 미소 (1.6초 → 편집 때 1.0~1.2초) ✅
- **화면**: 흰 번쩍 1장 → 천사 미소. 꽃이 머리 둘레에서 하나씩 빙글 피어나고 금빛 별(세로 긴 4갈래 + 금빛 번짐)이 커졌다 작아지며 반짝반짝. 글자 없음.
- **그림**: `char/gyul/exp/01-angel-clean.png`
  - 편집 프롬프트: `Edit this exact image. Remove ALL the pink cherry blossom flowers and ALL the white/gold sparkle stars and glowing dots floating around her. Fill those spots with the plain background and hair that would be behind them. Keep the girl, her face, the sparkles INSIDE her eyes … pixel-identical.` → 얼굴은 원본 그대로 합침
- **소리**: 꽃 필 때마다 종소리 한 음씩 올라감 + 반짝반짝 쉬머 (`ss.bloom`)
- **만들기**: `python3 ep01b/build_c6.py ep01b/c6-angel.mp4`

### 컷 6b · 천사 미소로 신나게 타자 (약 1.5초) ✅그림 · ⬜편집 0cr
- **화면**: 옆모습, 눈 감은 행복 웃음으로 키보드 타닥타닥. 머리 둘레 금빛 별 몇 개 반짝(컷 6 와 같은 `star()`).
- **그림**: `ep01b/c6b-type-angel.png`
  - 프롬프트: `Same composition as the FIRST image (side view at her desk typing on the keyboard in front of the monitor), but the girl now has a sweet angelic sparkling smile with eyes closed into happy curves, little sparkles around her head, typing cheerfully. Keep everything else the same.` (ref: ep01/cut01-work-v9, exp/01-angel)
- **소리**: 경쾌한 타닥타닥 (빠르게)

### 컷 7 · 메모장 凸凸凸 (약 3초) ✅ — 끝
- **화면**: 모니터 메모장 화면, 凸凸凸 3줄이 타닥타닥 쳐짐. 마지막 줄에서 0.8초 멈추고 끝.
- **만들기**: `tools/notepad_screen.py` → `ep01b/c7-notepad.mp4`
- **소리**: 타닥타닥 (한 글자마다 딸깍) · 마지막 엔터 "탁" · 귤이 음흉한 웃음 "흐흐흐흐…" `voice/ep01/c7-gyul-laugh.wav`

---
## 목소리 파일 (확정 · 0cr 로 재사용)
- 컷 1 팀장 `voice/ep01/c1-boss.wav` "이것 오늘까지 좀 부탁해요." · 컷 2 귤이 `voice/ep01/c2-gyul.wav` "네 알겠습니다!" · 컷 7 귤이 웃음 `voice/ep01/c7-gyul-laugh.wav`
- 대사 컷은 H3 대신 목소리 먼저 + 입은 코드 (`tools/talk.py`). 고정 설정은 `CONTINUITY.md`.

## 남은 일 (순서대로)
1. 컷 1 · 컷 2 H3 대사 영상 (약 20cr, 돌리기 전 `higgsfield generate cost minimax_h3 …` 로 확인하고 말하기) → 컷 2 위에 꽃·별 효과 얹기
2. 컷 3 · 6b 편집 (0cr: 정지 그림 + 소리 + 반짝)
3. 전체 이어붙이기 (컷마다 소리 포함) → 무드 25% → 릴스 틀(제목 · 자막)
