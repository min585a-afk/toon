# 에피소드 대본 (공감 + 유머 · 10~20초)

## ★ EP01 「팀장님의 아아」 (확정 1화 · 10/27 혁 스케치 · 약 20~22초 · 12장면)
뒤에서 욕하던 귤이가 냉정한 팀장의 아아 한 잔에 무너지는 반전 → 번뜩 → 카톡 삭제 끄덕끄덕.
- 배경 2곳: **사무실(귤이 자리)** `bg/office-desk.png` · **탕비실**(팀장이 데려간 곳, 만들 것).
- 팀장 표정은 **처음부터 끝까지 냉정한 무표정**(아아 줄 때도). 그 무표정과 귤이 리액션 대비가 웃음 포인트.

| # | 장소 | 화면 | 대사 / 자막 | 만드는 법 |
|---|---|---|---|---|
| 1 | 사무실 | **벽시계 10:00 클로즈업(초침 째깍) → 줌 아웃 → 타닥타닥 열일 → 모니터로 들어감** | (째깍 · 타자 소리) | `ep01/cut01-work-v9.png` + `ep01/build_opening.py` → `ep01/opening.mp4` (장면 1~2, 11초) |
| 2 | 사무실 | 모니터 메신저 화면(10:00) — 어제: "잘 들어갔어?" "응" / 오늘: "아.. 출근했어.." "나도..." "일하기 싫다.." "아 퇴사하고 싶다.. 증말.. 다들 일만 줘" → 옆에 **1** | 화면 글씨 | `tools/chat_screen.py --typing` 0cr — "일하기 싫다.." · "아 퇴사하고 싶다.." 는 입력창에 직접 타자 → 전송 (`ep01/cut02-typing.mp4`, 6.8초) |
| 3 | 사무실 | 1번 그대로 + 뒤에 팀장 뒷모습 · 귤이 머리 위 빨간 "!" | | 새 그림 1cr |
| 4 | 사무실 | 팀장 정면(냉정) | 팀장: "잠깐 나 좀 봐요." | 팀장 에셋 + 입 2단계 0cr |
| 5 | 사무실 | 귤이 클로즈업 세로 줄 충격 | (속마음) "나 뭐 잘못했나?…" | `exp/06-shock` 0cr |
| 6 | 탕비실 | 근엄하게 서 있는 팀장(아아는 등 뒤로 숨김) | | 새 그림 1cr |
| 7 | 탕비실 | 귤이 땀 삐질 | | 새 그림 1cr |
| 8 | 탕비실 | 팀장이 아아 툭 건넴(무표정) | 팀장: "이거 마시면서 해요." | 새 그림 1cr · AI 영상 후보 |
| 9 | 탕비실 | 귤이 하트 눈 뿅뿅 감동 | "팀장님…♡" | 새 그림 1cr |
| 10 | 탕비실 | 번뜩! (카톡 생각남) 입 크게 · 번개 | (속마음) "아 맞다 카톡!!" | 새 그림 1cr |
| 11 | 사무실 | 메신저 "삭제하시겠습니까?" + **1** 아직 안 읽음 → 귤이 미친 듯이 끄덕끄덕 | | 화면 편집 + 귤이 1장 1cr · 끄덕임은 효과 |
| 12 | 사무실 | 삭제 완료 · "휴…" | 자막: "…메시지를 삭제했습니다" | 편집 0cr |
- 예상: 배경 1 + 그림 8 = 9cr · AI 영상 1컷 5~10cr.

---
## (예전 초안 · 옛 그림체 기준 — 참고만)

## 톤 (10/26 혁)
- 공감 또는 유머. 평범한 직장인 순간 → 오리가 팩폭/장난 → 주인공 과장된 애니 리액션(배경 불타기 · 하얀 점 눈 · 세로줄 등).
- 오리 = 장난꾸러기 팩폭형. 주인공 = 해맑은데 늘 당하는 신입.
- 입은 옛날 애니처럼 뻐끔뻐끔(입모양 안 맞춤). 목소리는 대사 전체를 한 톤으로 먼저 만들고 영상에 얹기.

## (옛) 「월요일 + 카드값」 (약 15초 · 4컷) — 10/26 혁 타임라인 수정
| 컷 | 길이 | 화면 | 대사 / 자막 | 프리셋 |
|---|---|---|---|---|
| 1 | 3초 | 책상에 턱 괴고 "후우…" 길게 한숨, 어깨 축 | 주인공: "후우…" / *Sigh…* | 정면 + 아래 보기 |
| 2 | 4초 | 오리가 어깨 위에서 고개 갸웃 → 주인공 시무룩하게 오리 쪽으로 | 오리: "왜? 거울 봤어?ㅠ" / *Why? Looked in the mirror?* → 주인공: "아니… 오늘 월요일이잖아…" / *No… it's Monday…* | 우 3/4 |
| 3 | 4초 | 오리 "흐음…" 하더니 날개로 폰을 들어 보여줌 → 폰 화면 클로즈업: 카드값 ₩2,000,000 (글자는 편집에서) | 오리: "흐음…" / *Hmm…* | 오리 단독 + 정면 |
| 4 | 4초 | 주인공 뒤 배경 활활 불타며 눈에 불꽃, 미친 듯이 키보드 타자(불태우며 일함) · 옆으로 오리가 종종걸음으로 도망 | 주인공: "으아아아!!" / *AAAAH!!* | 정면 (개그 얼굴) |
- 제목(위): **월요일 아침의 진실**
- 비용 예상: 장면 그림 4장 ≈ 9cr · 영상 3~4초×4 ≈ 30cr → **약 39cr**
- 메모: 카드 화면 글자는 빈 화면으로 뽑고 편집에서 "카드값 ₩2,000,000". 컷4 불길은 영상 + 편집 빨간 깜빡임·흔들림, 오리 도망은 같은 컷 안에서.

### EP01 실제 프롬프트

**고정 블록 (모든 장면 그림 앞에 붙임 · CHAR)**
> Exactly the same girl and the exact same soft retro 1990s anime drawing style, line weight and color tone as the reference images: a little girl with a very round baby face, big violet-brown eyes with two white highlights, rosy round blush, tiny dot nose, long fluffy wavy black hair with bangs, a small white-and-pink flower clip, red cardigan over a plain white tee, no lanyard, no badge. Her companion is a small round yellow duckling with an orange beak and pink cheeks. Flat cel colors, soft shadows, thin dark lines, slightly faded colors, gentle grain. 4:3 landscape frame. No text, no letters, no logos.

**배경 블록 (BG)**
> A small cozy office in soft daylight: her desk by a window, a cream retro computer monitor and keyboard, an iced americano, a small potted plant, softly blurred background, warm muted colors.

| 컷 | 그림 (Seedream · 넣을 이미지: 프리셋) | 영상 (MiniMax H3 · 첫 장면 = 그림) |
|---|---|---|
| 1 | CHAR + BG + `She sits at her desk with her chin resting on one hand, shoulders slumped, eyes half-closed, letting out a long tired sigh. The duckling sits on her shoulder.` · 정면, 아래보기 | `She lets out a long slow sigh, shoulders dropping, eyes half-closed. Hair sways slightly. Simple limited animation, mouth flaps open and closed simply like an old TV cartoon. Camera still. No music.` |
| 2 | CHAR + BG + `The duckling on her shoulder tilts its head at her curiously; she turns her face toward the duckling with a gloomy pout.` · 우 3/4, 오리 | `The duckling tilts its head and talks, then the girl answers gloomily. Both mouths simply flap open and closed while talking, old TV cartoon style. Small head movements only. Camera still. No music.` |
| 3 | CHAR + BG + `Close-up: the duckling holds up a smartphone with its wing toward her; the phone screen shows a plain bright blank screen. The girl leans in to look.` · 오리, 정면 | `The duckling goes "hmm", then slowly lifts the smartphone up to show the screen. The girl leans in, freezes. Simple limited animation. Camera slowly pushes in to the phone. No music.` |
| 4 | CHAR + `Comedic anime gag shot: the girl typing furiously on the keyboard with fierce determined burning eyes, a huge wall of cartoon flames blazing behind her, her hair flying up; on the side, the little duckling is running away in tiny quick steps with a sweat drop.` · 정면 | `Comedic anime gag: she types furiously at super speed, cartoon fire roaring and flickering behind her, papers flying; the duckling scurries out of frame on tiny legs. Fast limited animation, screen shake. Mouth wide open yelling. No music.` |

- 목소리: 대사 4줄을 한 톤으로 먼저 만들고(주인공 · 오리 따로), 영상 위에 얹음. 영상 프롬프트에는 대사 안 넣음(입만 뻐끔).
- 편집에서 얹을 것: 폰 화면 "카드값 ₩2,000,000", 컷4 빨간 깜빡임 · 흔들림, 자막, 제목, 초당 8장, TV 재질.

## (옛) 「월요일이 나타났다」 (약 12초 · 4컷) — 10/26 혁
| 컷 | 길이 | 화면 | 대사 |
|---|---|---|---|
| 1 | 3초 | 복도, 검은 실루엣 뒷모습 너머로 주인공이 멍하게 바라봄 | 주인공: "넌… 누구야?.." |
| 2 | 3초 | 실루엣 정면 · 하얀 눈 번쩍 · 허리에 손 · 빨강/노랑 집중선 + 번개 | 실루엣: "난! 난! 월요일이다!!" (편집에서 만화 글자 "월요일") |
| 3 | 2초 | 주인공 클로즈업 · 하얗게 질림 · 세로 줄 · 눈물 · 손으로 막기 | 주인공: "안 돼… 저리 가!" |
| 4 | 4초 | 주인공 바퀴 다리로 도망 · 먼지 · 속도선 · 실루엣은 가만히 바라봄 | 주인공: "으아아앙!!" |
- 그림: `ep02/cut1.png`(= shadow-01) · `cut2.png` · `cut3.png` · `cut4.png` (Seedream 2k 4:3, 장당 2.5cr). 모아보기 `ep02/cuts-01.jpg`.
- 주인공 기준 = `asset3/gyul-front-04-tv.png`(D 얼굴). 귤핀 · 오리는 아직 없음.
- 마무리: 영상 → 8fps → `anime_grade 0.7` + `tv_crisp 0.6`(필터4) → 자막 · 제목.

## 에피소드 후보 (10/27 · 10~20초 · 앞 천사 → 뒤 현실)
| # | 제목 | 앞 → 뒤 |
|---|---|---|
| 1 | 월요일이 나타났다 | "넌 누구야?" → 월요일인 걸 알고 전력 도주 (EP02) |
| 2 | 약속 취소 문자 | "어머 괜찮아~ 다음에 보자!" → 이불 속 만세 |
| 3 | 다이어트 첫날 | "오늘부터 샐러드만!" → 밤 11시 치킨 앞 오열 |
| 4 | 카톡 읽씹 | "바쁜가 보다~" → 1분마다 확인하며 폭발 |
| 5 | 미용실 | "와 너무 마음에 들어요!" → 집 거울 앞 절규 |
| 6 | 알람 | "5분만 더…" → 40분 지남 |
| 7 | 엄마 전화 | "응 밥 잘 먹고 있지~" → 라면 국물만 남은 냄비 |
| 8 | 택배 | 상자 앞 천사 미소 → 사이즈 실패 |
| 9 | 월급날 | 월급 반짝 → 3초 뒤 카드값 |
| 10 | 단톡방 | "ㅋㅋㅋ 너무 웃기다" → 무표정 타자 |
