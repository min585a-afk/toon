# 애니 일상 계정 (다온과 별도 · 2026-10-24 혁)
- 캐릭터: 긴 검정 웨이브 머리 · 흰 꽃핀 · 통통한 볼 · 흰 티 — `character-01-typing.jpg` (nano_banana_pro 2k · 혁 레퍼런스 그림체).
- 그림체 프롬프트: "1980s-90s retro anime style, soft cel shading, thick clean lineart, pastel warm colors, blush cheeks, big glossy eyes, film grain, lo-fi mood" + 캐릭터 그림을 참고로.
- 포맷: 8~10초 · 장면 2~3개(각 3~4초, 손 · 눈 · 머리카락만 살짝) · 말 없음, 음악 + 한 줄 글.
- 옛날 애니 느낌은 후처리(초당 8~12장 · 그레인 · 바랜 색 · 미세 흔들림, 0cr).
- 크레딧: 그림은 나노바나나 이벤트면 사이트에서 직접(무료) — API 로 만들면 크레딧 빠짐. 움직임 = Seedance fast 720p 장면당 4초 ≈ 10cr.
- 첫 편 제안 "출근한 날": 타이핑 → 머그컵 후 불기 → 창밖 노을 기지개.
- 포스터 글자 깨짐("POSTU") 있음 — 쓸 때 지우기.

## 10/24 진행 (두 번째 채팅)
- 레퍼런스 채널: kkum.byeol.ai · oldku_ku · doriverse_anime — 9:16 검정 + 위 큰 제목 + 가운데 옛날 애니 장면 + 아래 색 자막. 틀은 장르 유행이라 같이 써도 됨, **캐릭터 · 목소리 · 한국 회사 디테일 · 자막색**으로 차별.
- 캐릭터 1차(검정 웨이브 · 꽃핀)는 버리고 **새 캐릭터: 동글 아기얼굴 신입 회사원**(핑크 가디건 · 흰 카라 블라우스 · 사원증 · 아아). 혁 샘플(핀터 2장, 파란 하늘 + 핑크)이 기준 그림체.
- 모델: 나노바나나는 이 그림체를 잘 못 따라옴 → **GPT Image 2.5(quality high, 귀여움)** · **Seedream 5.0 Pro(셀화 결)** 가 샘플에 가까움. 샘플을 `--image` 로 직접 넣어야 함(글 설명만으론 안 됨).
- 재질: `tools/tv_look.py` (0cr) — SD 480줄 · 색 번짐 · 바램 · 주사선 · 그레인, 그 위에 원본 어두운 선을 다시 얹어 **배경은 뭉개고 캐릭터 테두리만 또렷**. 인자: 세기(기본 1) · 선 진하기(기본 0.7).
- 릴스 틀 시안: `v2/reel-01.jpg` — 그림은 4:3 띠(인스타 캡션 · 버튼 피함), 제목 Black Han Sans 흰색, 자막 Gothic A1 800 **노란색**(우리 색), 영어 자막 없음.
- 목소리: Higgsfield 에 TTS 있음(ElevenLabs v4 · text2speech_v2 minimax/seed_speech 등) → Seedance `audio_references` 로 입 맞춤. 시험 전.
- 다음: **캐릭터 에셋 다시 짜기**(혁 10/24) — 설정 먼저 정하고 시트(정면/옆/뒤 + 표정)로 고정.

## 캐릭터 에셋 (10/24 · Seedream 5.0 Pro)
- 설정: 입사 1~2년차 신입(26) · 아기얼굴 · 3등신 · 긴 검정 머리(잔머리, 일자 앞머리) · 연핑크 꽃핀 · 연핑크 가디건 · 흰 동그란 카라 블라우스 · 크림 치마 · 갈색 로퍼 · 남색 줄 사원증 · 상징 = 사원증 + 아아.
- 그림체: 얇은 갈색 선 · 파스텔 · 연필/수채 결 · 빗금 볼터치 (혁 핀터 샘플 기준, GPT 느낌 X).
- 기준 3장 — 장면 만들 때 늘 같이 넣기: `asset/char-v11-seedream.png`(얼굴) · `asset/sd-sheet-turnaround.png`(몸 4방향) · `asset/sd-sheet-expressions.png`(표정 6).
- 모델: **Seedream 5.0 Pro**(`seedream_v5_pro`, 2k, 약 2.5cr). GPT Image 는 너무 매끈(혁 "GPT 느낌 X"), 나노바나나는 이 그림체 못 따라옴.

## ✅ 확정 스타일 (10/24 저녁 · 혁 "오 좋은데")
- 기준 그림: `asset2/base-09-pastel-soft.png` (원본) · `asset2/base-09-pastel-soft-tv.jpg` (TV 재질 0.35) · 릴스 시안 `asset2/reel-04-pastel-soft.jpg`.
- 캐릭터: 꿈별 같은 얼굴 크기·몸 비율(동글 넓은 아이 얼굴, 큰 머리, 작은 몸) + 큰 갈색 눈 · 긴 검정 웨이브 · 일자 앞머리 · 핑크 꽃핀 · 신입 회사원(사원증).
- 그림: 90년대 TV 셀화(단색 · 딱 끊어지는 그림자 한 겹 · 진한 테두리 · 빗금 볼터치 · 각진 머리 광택).
- 색: **차분한 환상 파스텔** — 핑크 · 라벤더 · 연하늘 · 민트, 그림자 라벤더. 방울 · 반짝이 · 글로우 **없음**(혁 "효과 너무 강해").
- 재질: `tools/tv_look.py 입력 출력 0.35 0.4` (약하게).
- 만드는 순서: Seedream(장면·구도) → 나노바나나 프로 편집(셀화 + 파스텔, 이 기준 그림 넣기) → tv_look 0.35 → 릴스 틀(위 제목 흰색 Black Han Sans · 그림 4:3 · 아래 노란 자막 Gothic A1).

## 첫 영상 (10/25) — `video/reel-monday-01.mp4`
- 기준 그림 `asset2/ref7-01.png` (혁 핀터 리본/꽃핀 레퍼런스 그대로 · Seedream 5.0 Pro) — **최종 캐릭터 기준**.
- 영상 = **MiniMax H3** (`minimax_h3`, 2K · 5초 · 10cr) 첫 프레임 = 기준 그림. 프롬프트에 한국어 대사 + "1990s Korean TV dub 여자 성우 목소리"를 쓰면 **목소리 · 입 · 표정까지 영상이 직접 만듦** (레퍼런스 채널 방식: MiniMax H3 + niji/GPT Image + Suno BGM + 프리미어).
- Higgsfield TTS(text2speech_v2 · ElevenLabs v4)는 한국어 연기가 약함 → 안 씀.
- 틀: 9:16 검정 · 위 제목(흰 Gothic A1 800) · 가운데 4:3 영상 · 아래 자막 흰 기울임 + 영어 초록(#39FF14) 작게. 합성은 ffmpeg (0cr).

## 캐릭터 설정 갱신 (10/25 · 혁)
- 그림체 기준 = 혁 핀터 꼬마 레퍼런스(보라 꽃다발 · 파란 리본 · 빨간 원피스 · 고양이) — 90년대 셀 애니, 길고 풍성한 검정 웨이브, 짧은 앞머리, 색 있는 큰 눈 + 하이라이트 2, 동그란 볼터치.
- **복장 = 빨간 가디건** + 흰 동그란 카라 블라우스 + 남색 사원증 + 흰·핑크 꽃핀.
- **짝꿍 = 노랑 오리**(동글 아기 오리, 주황 부리·발, 볼터치) — 늘 같이 다님(어깨 위 등).
- 기준 그림: `asset2/kid-front-03-red-duck.png`.

## 원칙 추가 (10/25)
- **그림 톤 고정**: 기준 `asset2/kid-front-03-red-duck.png` 톤(부드럽고 살짝 바랜 색 · 동글 아기얼굴 · 얇은 선) 유지. 장면 그림은 나노바나나 편집 말고 **Seedream + 기준 그림 + 핀터 레퍼런스**로, 영상 전에 그림 먼저 확인받기.
- **옛날 애니 프레임**: 영상은 후처리로 초당 8장(또는 12장)으로 끊기 — `ffmpeg -vf "fps=8,fps=30"` (0cr). 목소리는 `rubberband=pitch=1.12:formant=preserved` + 고음·저음 깎기(입 싱크 유지).

## ✅ 최종 룩 (10/25 · 혁 "이게 낫다")
- 기준 그림 `asset2/walk-02.png` 톤(Seedream · 부드럽게 바랜 색 · 아기 얼굴) — 셀화 변환·반짝이 눈(walk-03/04)은 **안 씀**.
- 캐릭터만 또렷 + 배경 흐림: 배경 제거(`image_background_remover`, 1cr)로 마스크 → 배경 blur 7 · 채도 0.85, 캐릭터 살짝 샤픈 → `tv_look 0.45 0.75` = `asset2/walk-05-depth-tv.jpg`.
- 영상은 장면마다 이 처리(프레임별은 비쌈) 대신, 시작 그림에 적용해서 넣고 → 후처리 8fps + TV 재질.

## ✅✅ 최종 기준 얼굴 (10/25 · 혁 "이게 젤 나은 거 같은데")
- **`asset2/base-final.png`** (kid-front-03-red-duck 에서 사원증만 뺀 것 + 샤픈) — 이걸 모든 장면·영상의 첫 기준으로.
- 왜 이게 나은가: 처음부터 꽃다발 레퍼런스(kid-14)를 직접 넣고 Seedream 으로 한 번에 그려서 얼굴·눈·색이 한 덩어리로 맞음. 이후 버전들은 편집을 여러 번 겹치며 조금씩 틀어짐(어른스러워짐 · 눈 회색 · 배경 얼룩).
- 이후 바꿀 것(머리띠 리본 · 사원증 빼기 등)은 **이 그림에서 편집 1번**으로만. 편집을 겹치지 않기.

## 프리셋 · 목소리 고정 (10/26 준비 · 크레딧 충전 후 실행)
- 프리셋: `bash tools/make_presets.sh` → `presets/00-front-noduck · 01-left · 02-right · 03-up · 04-down · 05-side` (기준 `asset2/base-final.png`, 약 14.5cr). 하나만: `bash tools/make_presets.sh left`.
- 목소리 한 톤 고정: 금요일 v2 영상에서 뽑은 `voice/ref/girl-voice.wav`(주인공 3.3초) · `voice/ref/duck-voice.wav`(오리 0.8초).
  - MiniMax H3 는 `audio_references` 를 넣으려면 `start_image` 대신 `image_references` 로 그림을 줘야 함(같이 못 씀).
  - 영상 만들 때: `--image-references <장면그림> --audio-references voice/ref/girl-voice.wav` + 프롬프트에 "use the exact voice from the reference audio".
  - 후처리도 늘 같게: `rubberband=pitch=1.1:formant=preserved,highpass=f=220,lowpass=f=5500` → 톤이 편마다 같아짐.

## ▶ 이어서 하기 (10/27 최신 · 새 채팅/다른 계정은 여기부터)
- **캐릭터 에셋 완료 → `char/gyul/README.md`** (기준 얼굴 `char/gyul/face/front.png` · 도안 `char/gyul/sheet.png`). 그림 = GPT Image 2.5 + 진짜 90년대 캡처(혁이 다시 올려야 함).
- 캐릭터 = 앞 천사 / 뒤 현실 갭 · 주제 = 누구나 공감 + 엉뚱한 에피소드 · 10~20초 · 인스타 메인 (아래 '콘셉트 확장').
- **인스타 계정 = 별툰 `@byeoltoon.kr`** (10/27 혁 가입). 계정 = 채널, 그 안에 시리즈(직장 개그 · 커플 드라마 · …). 영상 제목은 시리즈 이름을 앞에.
- **기본 칠 = 25% 무드** (10/27 혁): `python3 tools/mood.py in out` — 그림자 살짝 깊게 · 비네트 · 채도 조금 낮춤 · 그레인. 완성 영상 마지막에 한 번(자막 전). 예시 `char/gyul/face/front-mood-25.png`. 극장판 칠(`front-drama-test.png`)은 너무 무거워서 안 씀.
- 릴스 틀 도구 `python3 tools/reel_frame.py 그림 out.jpg "제목" "한글" "영어" [--guide]` · 샘플 `frame/reel-ep01-sample.jpg`. 그림·영상은 4:3(2336×1744 / 1080×810) → 최종 9:16.
- **목소리 방식 바뀜 (10/27): 목소리 먼저 Seed Audio 로 한 줄씩 → 입은 코드로.** 귤이 기본 = `voice/ref/gyul-base.wav`(오디션 C3 + A 만화 톤 섞은 것 = `voice/cast4/3.wav`, 20대 중반 · 투니버스 만화 더빙 목소리) 를 항상 `@Audio1` 로, 감정은 프롬프트(+ 자주 쓰면 감정 레퍼런스 `@Audio2`). 레퍼런스 한 줄에 최대 3개 · 한 줄 0.1cr. 팀장은 빠르고 날카롭게.
- (예전) **목소리 확정 = MiniMax H3 영상 안에서 같이 생성** (10/27 혁 "괜찮았는데"). 기준 목소리: 귤이 `voice/ref/gyul-h3.wav`(9번 '팀장니이임') · 팀장 `voice/ref/boss-h3.wav`('잠깐 저 좀 볼까요?'). **다음 컷부터 `--image-references 그림 --audio-references voice/ref/<캐릭터>-h3.wav` + 프롬프트 'Use the exact same voice as the reference audio'** 로 일관성. 같은 후처리(highpass 200 · lowpass 6000).
- (예전 시험) 귤이 = `seed_audio --audio-references voice/ref/girl-voice.wav` (목소리 복제 · 한 줄 0.1cr → 편마다 같은 목소리). 팀장 = `seed_audio --voice_id <preset>` 후보 Vera/Helena 또는 `text2speech_v2 --variant minimax`. 후처리 `rubberband=pitch=1.06:formant=preserved,highpass=f=200,lowpass=f=6000`. 시험 `voice/test/voice-test-01.mp4`.
- 조연 팀장 `char/boss/` · 사무실 배경 `bg/office-desk.png`.
- **1화 = EP01 「천사와 악마」** (`ep01b/`, `EPISODES.md` 맨 위). 「팀장님의 아아」(ep01/)는 보관.
- (보관) 「팀장님의 아아」 (`EPISODES.md` 맨 위). 다음: 팀장 캐릭터 → 배경 2 → 컷 그림 → 영상.
- 영상 모델: Kling 안 씀. 다음 = **영상 1개 시험**(MiniMax H3 10cr/5초 · Seedance 2.0 Mini 5cr/5초) + **TTS 목소리 시험**(`tools/talk.py --audio` 로 입 자동).
- 정석 체크리스트 `STYLE_GUIDE.md` · 대본 `EPISODES.md`. 예전 시도 폴더(asset·asset2·asset3·presets·ep01·ep02·v2·video)는 10/27 삭제 — 필요하면 git 기록에서 되살리기. 릴스 틀 기준 `frame/`, 목소리 샘플 `voice/ref/`.
- 힉스필드 로그인: `higgsfield auth login` → 링크 승인 → 오류 페이지 주소 그대로 curl → `higgsfield workspace set <id>`.

## ▷ 예전 이어서 하기 (10/26)
- **주인공 기준 그림: `asset3/front-v11-brown.png`** (10/26 확정 · front-v7[Seedream] 에서 눈 1.15배 + 반짝이 1.4, 갈색 눈 · 0cr 도구로). 편집은 이 그림에서 1번만, 겹치지 않기. 이전 기준 front-v6.
- **색: 넣는 그림은 원본, 완성본만 보정** — 모델에 넣는 기준·컷 그림은 원본 색 그대로, 영상 완성 후(자막 전) `python3 tools/anime_grade.py … 0.7` 한 번.
- 정면 얼굴 클로즈업(오리 없음): `asset3/face-front-01.png` (Seedream 2k · 2.5cr), 보정본 `face-front-01-grade0.7.jpg`.
- 그림 모델 = Seedream 5.0 Pro(새로 그리기) · 나노바나나 프로(편집 1번) · 영상 = MiniMax H3(2cr/초). 크레딧 확인 `higgsfield generate cost …`.
- 릴스 틀 확정: `frame/reel-title-B-jua.jpg` (아래 '릴스 틀 확정' 참고). 글꼴 `tools/fonts/`.
- 톤: 공감 + 유머, 오리 = 장난꾸러기 팩폭형. 대본·프롬프트 = `EPISODES.md` (EP01 「월요일 + 카드값」 4컷).
- 입은 옛날 애니처럼 뻐끔. 과장 표정(하얀 점 눈 · 불타는 배경 · SD 개그)은 따로 그림 → 컷 전환.
- 배경은 장소별 시점 세트(정면 · 반대편 · 옆 · 책상).
- **다음 순서 (10/26 갱신)**: 그림체·캐릭터 확정 섹션 참고(기준 gyul-gpt-01 · GPT Image 2.5 + 90년대 캡처 · 앞천사/뒤직장인 갭). ① '뒤 얼굴'(화남 · 욕 · 그림자 얼굴) 시안 ② EP02 대사를 갭 캐릭터에 맞게 ③ animatic + 입 뻐끔 영상 + 목소리 + 필터4 + 자막.
- 힉스필드 로그인: `higgsfield auth login` → 링크 승인 → 오류 페이지 주소를 **대소문자 그대로** 붙여서 curl → `higgsfield workspace set <id>`.
- 혁이 보낸 레퍼런스 그림(핀터·인스타 캡처)은 남의 작품이라 저장소에 없음 — 필요하면 새 채팅에 다시 올리기.

## 색감 · 오리 눈 (10/26 혁)
- 색감은 혁 레퍼런스 2장(책 읽는 애 · 햄스터 애, 저장소엔 없음) 쪽으로: 2000년대 TV 셀화처럼 **맑고 선명한 색** · 진한 검정 머리에 남색 광택(각진 하이라이트) · 깨끗한 흰 피부에 분홍 빗금 볼터치 · 그림자는 한 겹 또렷하게 · 파란 하늘/연한 배경. 바랜 색 · 뿌연 필터는 빼기.
- 오리 눈: 작은 까만 점 → **햄스터처럼 크고 동그란 까만 눈 + 흰 하이라이트 2개(큰 거 하나 · 작은 거 하나)** + 분홍 볼터치.
- 반영: 다음 시트(주인공 · 오리 4×4) 만들 때 프롬프트에 넣기. 아직 안 돌림.

## ✅ 새 기준 그림 + 애니 색감 (10/26 혁 "그걸로 가자")
- `asset3/front-v11-brown.png` = front-v7(Seedream, 레퍼런스 색감) → `tools/eye_tweak.py` 눈 1.15배 → `tools/eye_sparkle.py` 반짝이 1.4 (전부 0cr). 파란 눈 버전(`front-v11-blue.png`)은 특별 컷(감동·개그)용으로 남김.
- 화질 = "화질이 나쁜 게 아니라 색"(혁): 레퍼런스 잰 값 — 채도 우리의 절반 · 검정 자주빛 진갈색(0.12,0.10,0.13) · 제일 밝은 색 분홍 크림(0.94,0.87,0.89). → `tools/anime_grade.py` 로 시험했지만 혁이 **원본(보정 없음)이 더 낫다**고 함 → 기본은 보정 없이.
- 다른 도구: `tools/tv_crisp.py`(SD 재질) · `tools/film_soft.py`(뭉갠 필름) — 지금은 anime_grade 가 제일 가까움.

## 캐릭터 설정 시트 v2 (10/26 · 나노바나나 프로 4k 16:9 · 4cr)
- `presets/v2/sheet-girl-model-01.png` — 기준 face-front-01 + front-v11-brown. 전신 4방향(키 가이드 줄) · 얼굴 6방향(정면 · 좌우 3/4 · 옆 · 위 · 아래) · 표정 8(웃음 · 미소 · 한숨 · 울먹 · 화남 · 놀람 · 개그 · 졸림) · 복장(빨간 가디건 · 흰 티 · 크림 주름치마 · 흰 양말 · 갈색 메리제인).
- 쓰는 법: 컷 그릴 때 이 시트를 예시(--image)로 같이 넣기. 오리 시트는 따로.
- `presets/v2/sheet-girl-model-02-kid.png` (4cr) — 혁 "너무 큰 성인 같아서 매력 없어" → **2.5~3등신 꼬마**(4살쯤 · 큰 머리 · 짧고 통통한 팔다리 · 아래로 넓은 볼 · 이목구비 낮게 · 넓은 이마). 비율은 맞았는데 그림이 납작한 벡터처럼 됨(머리 광택 · 셀 그림자 · 빗금 볼 빠짐).
- **`presets/v2/sheet-girl-model-03.png`** (Seedream 2k · 2.5cr) — 정면(face-front-01 + front-v11-brown)만 넣고 몸만 2.5~3등신으로. 얼굴·그림체 유지 + 꼬마 비율. 혁 레퍼런스(우산 꼬마)와 같은 느낌.
- `presets/v2/sheet-girl-model-04-cel.png` (2.5cr) — 시트 03 + 혁 꽃다발 꼬마(선 레퍼런스)로 셀 선 입히기 시도 → **거의 안 바뀜**(Seedream 이 첫 그림을 그대로 베낌). 첫 번째 그림 비중이 너무 큼. 한 번 더 막힘: 'toddler · body' 단어가 nsfw 오탐(크레딧 안 빠짐) → '치비 캐릭터'로 쓰기.
- **연기 시트** `presets/v2/sheet-girl-acting-01.png` (Seedream 2k · 2.5cr · 선 레퍼런스를 첫 번째로) — 옛날 애니 과장 표정 8(크게 웃음 · ^^ 반짝 · 힘줄+주먹 · 폭포 눈물 · 큰 땀방울 · 세로 줄 · 하얗게 질림 · 볼 빵빵) + 행동 8(V · 만세 · 발 구르기 · 입 가리고 키득 · 펄쩍 · 털썩 시무룩 · 달리기 · SD 버둥). 디자인 시트(03)는 고정용, 연기 시트는 컷 표정·포즈 고를 때.
- **귤이 시그니처 시안** `asset3/gyul-variants-01.png` (Seedream 2k · 2.5cr) — 혁 "2000년대 애니 치고 캐릭터 메리트 없음" → 꽃핀 대신 **귤 머리핀**(초록 잎) 고정. 1 귤핀만 · 2 + 바보털 · 3 + 큰 사원증 · 커피 · 4 전부 + 오리.
- 비율 기준(혁 핀터 레퍼런스: 리본 꼬마 · 꽃다발 꼬마 · 보라 후드 남자애): **2.5~3등신 꼬마**. 남자애 캐릭터도 같은 비율 · 같은 그림체로 만들 예정.

## 귤이 새 방향 (10/26 혁) — 아기 얼굴 + 날씬한 20대
- 혁 레퍼런스(검정 원피스 · 검정 리본 소녀, 저장소엔 없음): 동글 아기 얼굴(통통 볼 · 이목구비 낮고 작게) + 날씬한 4~4.5등신 · 단순한 까만 큰 눈(하이라이트 점 1) · 얇은 갈색 선 · 완전 단색 · 차분한 검정/크림/분홍.
- 시그니처: **귤 머리핀**(리본 없음). 빨간 가디건 + 흰 티 + 남색 사원증 + 어깨 위 오리.
- 정면 시안 `asset3/gyul-front-01.png` (Seedream 2k · 2.5cr). 꼬마 시트(presets/v2)는 개그용 SD 로 남김.

## ✅✅ 그림체 확정 (10/26 혁 "오 옛날 느낌 나는데?")
- **기준 그림: `char/gyul/face/front.png`** — GPT Image 2.5 (`gpt_image_2_5`, quality medium, 2k, 4:3 · **1cr**).
- 만드는 법(고정): `--image 기준그림 --image 진짜 90년대 애니 캡처 2~3장` + 프롬프트 "authentic early-1990s Japanese TV anime frame… bold black cel outlines, flat cel paint, one hard shadow, angular hair highlights, 90s eyes, hand-painted pastel background, film grain". 캡처(혁이 보낸 kkum.byeol · 파란 머리 · 햄스터 애)는 남의 작품이라 저장소에 없음 → 새 세션에서 다시 받기.
- 왜: Seedream 은 넣은 인물 그림을 그대로 베껴서 그림체가 안 바뀜. 요즘 핀터 AI 그림을 레퍼런스로 쓰면 요즘 그림이 나옴 → **진짜 90년대 캡처만** 레퍼런스로.
- 필터는 거의 필요 없음(원본이 이미 TV 캡처 느낌). 쓰면 아주 약하게.
- **캐릭터 에셋 v3** `char/gyul/(옛 presets/v3) sheet-gyul-model-01.png` (GPT Image 2.5 high 2k 16:9 · 2.75cr): 전신 4방향 + 키 가이드 · 얼굴 6방향 · 표정 8(앞: 반짝 천사 웃음 · ^^ · 어색한 땀 웃음 / 뒤: 그림자 진 무표정 · 핏대 분노 · 이 악문 욕 · 세로 줄 충격 · 폭포 눈물). 복장: 빨간 가디건 · 흰 티 · 남색 사원증 · 크림 주름 롱스커트 · 흰 양말 · 갈색 로퍼.

## 콘셉트 확장 (10/27 혁)
- 주제: 직장인만이 아니라 **누구나 공감하는 일상 + 엉뚱한 에피소드**. 캐릭터 갭은 그대로 "앞 천사 / 뒤 현실".
- 길이: **10~20초**, 컷 3~5개. 틀 = ① 상황(0~2초) → ② 앞 천사 → ③ 전환 → ④ 뒤 현실 펀치 → ⑤ 꼬리(오리 한마디).
- 한 편 비용 목표 5~10cr: 그림 3~5장(GPT Image 2.5, 장당 1cr) + 움직임은 대부분 animatic(0cr) + AI 영상 1컷(Kling 2cr) + TTS.
- 플랫폼: **인스타 메인**(꿈별도 인스타는 되고 쇼츠는 안 됨). 쇼츠는 같이 올리기만. 수익 = 협찬 → 캐릭터 상품(이모티콘 정책 확인 필요).
- 에피소드 후보: `EPISODES.md` '에피소드 후보'.

## 귤이 단계별 디벨롭 (10/26 혁 "한 번에 뽑지 말고 조금씩")
- 시트 한 장(v3 model-01)은 몸이 5등신으로 길어지고 얼굴 느낌이 빠짐 → **gyul-gpt-01 느낌 유지가 1순위**, 한 장에 그림 1개씩, OK 받은 그림을 다음 단계 레퍼런스로.
- 매번: GPT Image 2.5 medium 2k(1cr) · `--image char/gyul/face/front.png` + 90년대 캡처 2장.
- 1단계 전신: `char/gyul/(옛 presets/v3) gyul-step1-fullbody-01.png` (약 4등신 — 혁 "비율 괜찮아", 더 작으면 로리 오해 위험 → 3등신 이하는 개그 SD 만).
- **시대 = 2026 현재**(그림체만 옛날). 복장: 오버핏 빨간 니트 가디건 · 흰 티 · 와이드 베이지 슬랙스 · 흰 스니커즈 · 남색 사원증 · 아아(빨대 컵). `char/gyul/(옛 presets/v3) gyul-step1-fullbody-02-2026.png` (1cr). 교복처럼 보이는 주름치마 + 흰 양말 + 로퍼는 안 씀.
- **머리 = 긴 생머리 그대로**(반묶음 `gyul-step1-fullbody-03-halfup.png` 은 혁 "너무 흔해" → 안 씀). **1단계 확정 = `char/gyul/(옛 presets/v3) gyul-step1-fullbody-02-2026.png`**.
- **캐릭터 도안(콜아웃)** `char/gyul/(옛 presets/v3) gyul-callout-v1.png` — `python3 tools/callout_sheet.py out.png` (0cr). 확정 전신에서 부위를 잘라 둘레 칸에 배치 + 빨간 지시선 + 색 팔레트(원본에서 뽑은 값). 칸은 나중에 생성한 디테일 컷으로 바꿔 끼움.
  - 색: 머리 #15151A · 머리 광택 #4C4A6F · 피부 #F7C7B6 · 볼 #F69997 · 가디건 #B23E3F · 티 #F6EEEC · 슬랙스 #E2C8B8 · 사원증 줄 #2B3661
- **도안용 정면 기본형 확정**: `char/gyul/(옛 presets/v3) gyul-base-front-02.png` (흰 반팔 · 남색 반바지 · 흰 운동화 · 흰 배경 · 4등신). 턴어라운드는 이걸 기준으로 한 장씩: 좌 3/4 → 옆 → 뒤 → 우 3/4.
- 턴어라운드 v1 `char/gyul/(옛 presets/v3) gyul-turnaround-v1.jpg`: 좌 3/4 `gyul-turn-01-left34-b.png` · 정면 `gyul-base-front-02.png` · 우 3/4 `gyul-turn-04-right34-flip.png`(좌 3/4 좌우 반전, 0cr — 한쪽 장식 생기면 다시 그리기) · 옆 `gyul-turn-02-side.png` · 뒤 `gyul-turn-03-back.png`.
- **진행 순서(혁 10/27)**: 캐릭터 에셋 전부 → 영상 1개 시험 → 판단(TTS 목소리 일관성 · 영상 품질 · 그림 유지). 나중에 **따뜻한 커플 이야기(드라마형)**도 추가 예정 → 상대역 캐릭터 따로.
- 얼굴: 정면 `char/gyul/face/front.png` · 좌 3/4 `char/gyul/(옛 presets/v3) gyul-face-02-left34.png` · 옆 `gyul-face-03-side.png` (혁 "완전 그시절 애니메이션").
- 표정 7: 앞 `gyul-exp-01-angel`(반짝) · `02-hehe`(^^) / 뒤 `03-dark`(그림자 무표정) · `04-angry`(핏대) · `05-curse`(욕) · `06-shock`(세로 줄) · `07-cry`(폭포 눈물). 모음 `gyul-faces-exp-batch1.jpg` · `gyul-exp-batch2.jpg`.
- 감정 6: `08-sad` · `09-surprised` · `10-shadow`(눈 안 보이는 그림자, 번짐 → 셀 그림자로 다시 고려) · `11-shy` · `12-flutter` · `13-teary`. 모음 `gyul-exp-batch3.jpg`.
- **입 모양 3** `char/gyul/(옛 presets/v3) mouth/gyul-mouth-1-closed.png` · `2-half` · `3-open` — 다문/반은 GPT 2장(2cr) 뽑아 **입 부분만 잘라 기준 그림에 붙임**(입 말고 픽셀 동일 → 바꿔도 안 떨림). 뻐끔 시험 `mouth/mouth-flap-test.mp4`.
  - **쓰는 것 = 키운 버전 `gyul-mouth-1-closed-big.png` · `2-half-big` · `3-open-big`** (입만 1.45배, 혁 "키운 게 나은 듯" · 폰에서 잘 보임). 시험 `mouth-flap-test-big.mp4`.
- **눈 깜빡 3** `char/gyul/(옛 presets/v3) eyes/gyul-eyes-1-open.png` · `2-half` · `3-closed` — 입처럼 눈 부분만 합성(2cr). 눈·입 자리가 안 겹쳐서 눈 3 × 입 3 자유 조합. 말하기+깜빡 시험 `eyes/talk-blink-test.mp4`.
- SD 개그 3: `char/gyul/(옛 presets/v3) sd/gyul-sd-01-stomp.png`(발 구르기 · 핏대) · `02-flail`(> < 폭포 눈물 버둥) · `03-run`(도망 · 먼지) — 평소 복장, 단색 배경 (3cr).
- **캐릭터 도안 v1 `char/gyul/(옛 presets/v3) gyul-model-sheet-v1.png`** (`python3 tools/model_sheet.py out.png`, 0cr) — 평소 복장 · 턴어라운드 5 · 얼굴 3 · 입 3 · 표정 13 · SD 3.
- 영상 모델: **Kling 안 씀**(혁 "별로"). MiniMax H3 / Seedance 쪽으로 시험.
- **정석 체크리스트 `STYLE_GUIDE.md`** — 그림 · 만화 기호 · 화면 · 움직임 · 편집 · 소리.
- 다음: 2 얼굴 각도 → 3 앞 천사 표정 → 4 뒤 직장인 표정 → 5 입 모양 3 → 6 귤핀 · 오리.

## ✅ 캐릭터 확정 (10/26 혁) — 귤이 = 앞에선 천사, 뒤에선 찐 직장인
- **얼굴 고정**: `char/gyul/face/front.png` (그림체 확정 섹션) · 원래 얼굴 `asset3/gyul-front-03.png` (D · 동글 아기 얼굴 · 회갈색 큰 눈 · 긴 검정 머리 · 일자 앞머리 · 빨간 가디건 · 흰 티). 이제 그림체·얼굴 안 바꿈.
- **성격 = 갭**: 앞(사람들 앞)에선 순수하게 웃는 순정만화 주인공 → 뒤(혼자 · 돌아서면)에선 화내고 욕하고 혀 차는 찐 직장인. 이 낙차가 매 편 웃음 포인트.
  - 연출: 앞 = 반짝이 · 파스텔 · 맑은 웃음 / 뒤 = 얼굴에 그림자 · 반쯤 뜬 눈 · 핏대 · 배경 어둡게. 욕은 "삐-" 처리 또는 기호(#$%!) 자막.
- 오리 = 그 속마음을 대신 말해버리는 팩폭 담당(콤비).
- 귤핀 · 오리는 기준 그림에 편집 1번으로 나중에 추가.
- 옛날 느낌 = 그림 말고 포장으로: 필터4(anime_grade 0.7 + tv_crisp 0.6) · 4:3 레터박스 · 90년대 더빙 말투 · 초록/흰 자막 · 8fps.
- **움직임 = 옛날 리미티드 애니 방식**(AI 로 큰 동작 안 함): 멈춘 그림 + 줌/패닝 · 화면 흔들림 · 흰/빨강 번쩍 · 집중선/속도선 · 도망은 배경 흐름 + 통통 튐. `tools/animatic.py` (0cr). AI 영상은 입 뻐끔 · 눈 깜빡 · 머리카락 정도만.
- EP02 데모: `ep02/animatic-01.mp4` (0cr, 12초).

## 오리 디자인 (10/26 혁)
- 방향: 통통한 아기 오리 — 몸이 동그랗고 크림빛 연노랑 솜털, 머리 위 솜털 몇 가닥, 작은 까만 점 눈, 크게 벌린 주황 부리(웃을 때 입 안 분홍), 짧은 날개를 살짝 든 자세, 짧은 주황 발. **모자 없음.** 2등신(머리·몸 거의 한 덩어리).
- 그림체는 주인공과 같은 셀 애니(얇은 선 · 평평한 칠 · 바랜 색). 레퍼런스(혁 이미지)는 3D 인형이라 느낌만 참고, 그대로 베끼지 않음.
- 만들기: `bash tools/make_presets.sh duck` (약 2.5cr).

## 프리셋 완성 (10/26 · 4×4 그리드 2장, 나노바나나 4k, 8cr)
- `presets/sheet-girl-4x4.png` · `presets/sheet-duck-4x4.png` → 칸별로 잘라 `presets/girl-01-front.png … girl-16-neutral.png`, `duck-01-front.png … duck-16-phone.png`.
- 주인공: 각도(정면·좌·우·옆·위·아래·뒤·전신) + 표정(웃음·한숨·울먹·화남·놀람·개그·졸림·무표정).
- 오리: 각도(정면·좌·우·옆·뒤) + 동작(날개·걷기·도망) + 표정(웃음 입 벌림·평온·갸웃·식은땀·화남·울음·놀람·폰 들기).
- 장면 만들 때: 필요한 칸 2~3장만 골라 넣기. 꽃핀이 그리드에서 빠진 칸 있음 → 장면 프롬프트에 "small white-and-pink flower clip" 계속 넣기.

## 색 방향 정정 (10/26 혁)
- "흐린 게 아니야" — 2000년대 TV 애니는 **선명 · 고대비 · 진한 채도**, 그림자는 진하고 색이 들어감(피부 자두/마젠타, 머리 남색), 하이라이트는 깨끗하게. 바랜 색 · 뿌연 필터 · 블러 쓰지 않기. TV 재질(tv_look)도 빼거나 아주 약하게.
- 기준 장면: `ep01/cut1-v2.png` (Seedream + 레퍼런스: 90년대 사무실 장면 · 90년대 얼굴 클로즈업 · base-final).

## ✅ 릴스 틀 확정 (10/26 혁 "이거 좋다") — `frame/reel-title-B-jua.jpg`
- 기준 캐릭터 그림: `asset3/front-v6.png` (base-final 얼굴 · 3등신 몸 · 중간보다 긴 검정 머리 · 따뜻한 레퍼런스 색감).
- 1080×1920 검정. **영상 4:3(1080×810)을 위에서 420px**부터(세이프존 · 시선 위 1/3).
- **제목**: 주아(Jua) 120px · 노랑 #FFE45C · 영상 위 50px 띄움.
- **자막**: 한글 Gothic A1 800 66px 흰색 기울임 + 영어 40px 초록 #39FF14 기울임, 영상 바로 아래, 오른쪽 버튼 피해 30px 왼쪽.
- 세이프존: 위 220 · 아래 420 · 오른쪽 아래 140 비우기.
- 글꼴 파일: `tools/fonts/jua.ttf`, `tools/fonts/ga1-800.ttf` (OFL 무료 글꼴).

## 나중에 참고 (10/26 혁 "참고만")
- 90년대 TV 애니 개그 연출: 단색/그라데이션 배경 위에 인물 둘, 한쪽은 평범한 얼굴, 다른 쪽은 단순한 SD(꼬마)체로 확 줄어든 몸 · 뾰루퉁 얼굴 · 발 차기 같은 과장 동작. 화면 질감은 SD 방송(살짝 뭉개진 선 · 연한 색).
- 쓸 곳: 리액션 컷(화남 · 삐짐 · 당황)에서 주인공을 SD체로 바꿔 넣기, 팀장님/선배 같은 조연과 대비. 배경은 장면 대신 단색·그라데이션으로 단순화.
- 레퍼런스 이미지는 남의 작품이라 저장소에 넣지 않음.

## 조연 후보 (10/26 혁 "나중에 다른 캐릭터로 추가")
- 주인공은 그대로 `asset3/front-v6.png`.
- `asset4/alt-A-bob.png` — 단발 + 동그란 안경 + 겨자색 가디건, 무표정 담담형 (옆자리 동기/선배 후보).
- `asset4/alt-B-bun.png` — 똥머리 + 연필 + 남색 후드, 피곤한 웃음형 (야근러 동료 후보).
- 조연으로 쓸 땐 오리 빼고(오리는 주인공 짝꿍), 이름·성격 정한 뒤 정면 기준 + 4×4 시트 따로.

## 이름 · 시그니처 (10/26 혁, 나중에 반영)
- 주인공 이름: **귤이**.
- 시그니처: 귤 — 지금 꽃핀 자리를 **귤 머리핀**(작은 주황 귤 + 초록 잎 하나)으로 바꾸는 걸 1순위로. 다른 후보: 귤색 머리끈, 귤 모양 사원증 줄 장식, 가디건 단추를 귤로.
- 반영 시점: 다음 기준 그림 편집 때 front-v6 에서 편집 1번(꽃핀 → 귤핀)으로. 색은 주황 1포인트만(빨간 가디건과 겹치지 않게 연한 귤색).
