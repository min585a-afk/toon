# 재활용 · 레퍼런스 모음 (EP01 「직장인의 스킬」에서 만든 것, 10/29)

다음 화 만들 때 여기서 꺼내 씀. 새로 잘 나온 것도 여기 추가.

## 릴스 틀 · 자막
- 이어붙이기 `python3 tools/assemble.py ep01b/full.json out.mp4` — 컷별 자막 · 효과음 · 배경음 바닥(`bed`: 곡 좋은 구간 이어 깔기 + 대사 컷에서만 살짝 낮춤) · 제목 두 색(`"직장인의 |스킬"` + `title_color`) · 워터마크(`watermark`) · `no_title`(끝 화면) · 컷 소리 크기(`vol`) · -14 LUFS.
- 제목 86px(80%) · 자간 -5 · 영상과 간격 약 60px / 자막 영상 아래 +52 · 영어 +126 / 워터마크 `@byeoltoon` 반투명. 세이프존: 위 220 · 아래 450 · 오른쪽 140 안 걸림.
- 끝 화면 `ep01b/build_end.py` (검정 '끝' + END).
- 이름 자막 `tools/name_card.py` · 메모장 글자 `tools/notepad_text.py --at "시작:시간 ..."`(노래·흥얼 박자에 맞춤) · 凸 연타 `tools/notepad_screen.py` · 화면은 `tools/cel_look.py` 로 셀 필터.

## 연출 기법
- 표정 바꾸기: 기준 그림에서 1번 편집 → 바뀐 곳만(차이 마스크) 프레임마다 위치 맞춰 덮기 (`ep01b/build_e7.py` 그림자 얼굴 · 핏대 따로 떼서 두근두근).
- 고개 돌리기: 머리만 원래 프레임에 합성 (`ep01b/build_e4.py`, `*-fix.png`).
- 분노 끝 멈춤 + 뒤 불만 계속 일렁임 (`ep01b/build_e3.py` FIRE_M).
- 꽃 피기 · 반짝 루프 (`ep01b/build_e1.py`, `build_e5.py`) · 안경 번쩍 (`build_c3why.py`) · 물음표 (`tools/qmark.py`).
- 컷 템포: 대사 뒤 머묾 0.5~1초 · 반응 컷 0.2~0.5초 여유 (혁 10/29 피드백).

## 소리
- 효과음 코드 합성 `tools/anime_sfx.py` → 목록 `sfx/lib/README.md` (확정: 키랑 · 물음표 · 키라키라 · 두근두근 · 화르륵 · 삐킷 · 휙 · 띠링).
- 대사 Seed Audio (`@Audio1` = `voice/ref/gyul-base.wav` / `boss-base.wav` / `butter-base.wav`) · **짧은 프롬프트 0.6~0.8cr** (긴 영어 프롬프트는 2~3cr) · 끝에 꼭 `Finish the last word fully, then one second of silence.` (안 넣으면 끝 글자 잘림) → `tools/voice_clean.py 원본 out [빠르기]` (앞 무음 · 끝 딸깍 자름 · 여운 0.3초 · -16dB · 버터 1.15배).
- 흥얼: Seed Audio 자연 흥얼 → `tools/hum_psola.py --retune in out G4 0.7` (박자 그대로 음만 고정). 코드로 음절 이어붙이기는 기계음 → 안 씀.
- 배경음 `brand/bgm/daily-comedy.m4a` 3~15.5초 구간 (Sonilo).

## 레퍼런스 장면 (그림 · 영상)
- `ep01b/*.png` 컷 그림 · `ep01b/video/*-h3.mp4` H3 영상 · 최종 `frame/ep01-full.mp4`.

## EP02 「눈치 게임」에서 더한 것 (10/30)
### 한 편 만드는 순서 (이대로)
1. 콘티(`ep0X/CONTI.md`) → 혁 확인 → 그림(GPT Image, 혁 확인) → 움직이는 컷만 H3 (10cr) — **한 편 200cr 이하, 목표 50~80**.
2. 장면 하나씩 만들고 그 장면까지 이어 붙인 미리보기로 혁 확인 (`assemble.py` 에 앞 컷 몇 개만 넣은 json).
3. 대사: 후보 1~2개 · 길이 재고 → 입 맞춤 (아래) · 대사가 컷 안에서 끝나게.
4. 효과음 · 배경음(앞 7초만) → 전체 → **`tools/qa_check.py` 통과** → 보냄 → 캡션(`ep0X/CAPTIONS.md`) · 썸네일.
### 입 맞춤 (대사 ↔ H3 영상)
- 프레임 시트로 입 벌린/다문 구간 눈으로 찾고 → `ep02/build_keyed.py 영상 '[[출력초,원본프레임],…]' 길이 out [--butter]` : 말할 땐 입 구간, 쉴 땐 다문 입·고개 동작 (멈추면 끊겨 보임).
- 말하는 구간만 대사 길이로 압축 (`build_s4.py` · `build_s6.py`) · 마디별 키 (`build_s9.py`).
- 그림 한 장 컷: 입 3단계(벌림 · 반 · 다묾=피부로 덮고 웃는 선)를 목소리 크기로 (`build_s8.py`) + 웃음마다 어깨 들썩(워프).
### 연출 · 그림 효과
- 시계 `ep02/build_s1.py 시 분 초 길이 out [--speed 2.5] [--flash]` — 똑·딱 번갈아 · 첫 소리 +0.05초 · `--flash` = 분침이 1분마다 딱 넘어감 + 6:00 땡(쇠종) · 땡 뒤에도 초침 계속.
- 물음표 그림 `ep02/fx/qmark.png` (GPT Image 셀 재질 · 리본 오른쪽에 따라붙음, `build_s5.py`) · 이빨 반짝(영상에 박힌 반짝 지우고 별 한 번, `build_s9.py`) · 반짝이 `ep02/fx.py star`.
- 은서 컷에 버터 뒷모습 얹기 (`--butter` · `ep02/s3-butter-back2*.png`) · 멈춘 그림은 천천히 줌 (`build_s3.py`).
- **끝 = 한 문장 펀치라인** (`ep02/build_end.py`, 글자 subset 은 Google Fonts `?text=`).
### 소리
- 새 효과음: 똑 `tik` · 딱 `tok` · 뾰로롱 `pyororong`(버터 등장·느끼) · 땡 `ttaeng` · 바람 `wind`(3초) · 하테나 `hatena` · 키랑 `kiran`.
- 배경음: 1화처럼 `['brand/bgm/daily-comedy.m4a', 첫컷, 0, 0.14, 7.0, 0.5, 1.6, 3.0]` 앞 7초만.
- `assemble.py` 끝에 리미터 (피크 -1.9dB) · 제목·자막 정가운데 (`reel_frame.py slanted` 30px 밀림 고침 10/30).
