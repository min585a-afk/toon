# 귤이 캐릭터 에셋 (최종)

앞에선 천사, 뒤에선 현실 · 90년대 TV 셀 애니 · 2026 오피스룩 · 약 4등신. 한눈에: `sheet.png` (`python3 tools/model_sheet.py char/gyul/sheet.png`).

| 폴더 | 내용 | 쓸 때 |
|---|---|---|
| `face/` | `front.png`(**기준 얼굴**) · `left34.png` · `side.png` | 새 그림 만들 때 항상 `front.png` 를 첫 레퍼런스로 |
| `base/` | `outfit-2026.png`(평소 복장 전신, 기준) · `design-front.png`(도안용 반팔·반바지) | 전신 장면 레퍼런스 |
| `turn/` | `1-left34` · `2-front` · `3-right34`(좌우 반전) · `4-side` · `5-back` | 돌아서기 · 옆/뒤 장면 |
| `exp/` | 01 천사 반짝 · 02 ^^ · 03 그림자 무표정 · 04 핏대 · 05 욕 · 06 충격 · 07 폭포 눈물 · 08 슬픔 · 09 놀람 · 10 눈 가린 그림자 · 11 수줍음 · 12 설렘 · 13 눈물 맺힘 · 14 멍때림(혼) · 15 졸림 · 16 삐짐 · 17 실눈 의심 | 표정 컷 · 장면 레퍼런스 |
| `sd/` | `01-stomp` · `02-flail` · `03-run` | 개그 리액션 |
| `talk/` | 웃는 입 3(`smile-mouth-1~3`) · 무표정 입 3(`neutral-mouth-1~3`) · 눈 `eyes-1-open` · `eyes-2-half` · 감은 눈 2종(`smile-eyes-3-closed` ^^ 모양 / `neutral-eyes-3-closed` 처진 모양) | 대사 컷 (`tools/talk.py`) |
| `test/` | 말하기 · 깜빡임 시험 영상 | |

## 대사 컷 만들기 (0cr)
```
python3 tools/talk.py out.mp4 --set smile --audio 목소리.wav     # 소리 크기로 입 자동
python3 tools/talk.py out.mp4 --set neutral --seconds 6          # 말 없이 자연스러운 깜빡임만
```
- 입·눈은 기준 얼굴에서 **그 부분만 합성** → 나머지 픽셀이 같아서 바꿔도 안 떨림.
- 깜빡임 2.5~5.5초 불규칙, 가끔 두 번 연속.

## 새 그림 만드는 법
GPT Image 2.5 (medium 2k, 1cr) · `--image char/gyul/face/front.png` + 진짜 90년대 캡처 2장(저장소엔 없음, 혁이 다시 올림) + 필요한 에셋 1장.

## 나중에
- 머리 스타일 변형(묶은 머리 · 헝클어진 아침 머리 등)은 장면 만들 때 필요할 때 1cr씩.
- 귤핀 · 오리 · 장면 배경 · 엔딩 컷.
