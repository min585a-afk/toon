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
- 대사 Seed Audio 0.1cr (`@Audio1` = `voice/ref/gyul-base.wav` / `boss-base.wav`) → 끝 딸깍 잘라내고 말소리 -16dB 로 맞춤.
- 흥얼: Seed Audio 자연 흥얼 → `tools/hum_psola.py --retune in out G4 0.7` (박자 그대로 음만 고정). 코드로 음절 이어붙이기는 기계음 → 안 씀.
- 배경음 `brand/bgm/daily-comedy.m4a` 3~15.5초 구간 (Sonilo).

## 레퍼런스 장면 (그림 · 영상)
- `ep01b/*.png` 컷 그림 · `ep01b/video/*-h3.mp4` H3 영상 · 최종 `frame/ep01-full.mp4`.
