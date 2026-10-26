#!/usr/bin/env bash
# 캐릭터 프리셋 6장 — 기준 asset2/base-final.png 에서 출발 (크레딧 충전 후 실행)
# 예상: 오리 없는 정면 2cr(나노바나나 편집) + 각도 5장 × 2.5cr(Seedream) ≈ 14.5cr
# 사용: bash tools/make_presets.sh            (전부)
#       bash tools/make_presets.sh left up    (골라서)
set -e
cd "$(dirname "$0")/.."
BASE=asset2/base-final.png
NODUCK=presets/00-front-noduck.png
KEEP='Exactly the same girl and the exact same soft retro anime drawing style, line weight and color tone as the reference image: same round baby face, same big violet-brown eyes with two highlights, rosy round blush, tiny dot nose, long fluffy wavy black hair with bangs, small white-and-pink flower clip, red cardigan over a plain white tee, no lanyard, no badge, NO duck. Plain soft light-blue background, head and shoulders, square frame, crisp clean lines. No text, no letters, no logos.'
gen_edit(){ u=$(higgsfield generate create nano_banana_2 --prompt "$2" --image "$3" --aspect_ratio 1:1 --resolution 2k --wait 2>&1|tail -1); curl -sS -o "$1" "$u"; echo "$1"; }
gen_new(){ u=$(higgsfield generate create seedream_v5_pro --prompt "$2 $KEEP" --image "$3" --aspect_ratio 1:1 --resolution 2k --wait 2>&1|tail -1); curl -sS -o "$1" "$u"; echo "$1"; }
want(){ [ $# -eq 0 ] && return 0; for w in $ARGS; do [ "$w" = "$1" ] && return 0; done; return 1; }
ARGS="$*"
want front && gen_edit $NODUCK 'Edit this image. Remove the yellow duckling completely and fill that area with her hair and the plain light-blue sky. Keep everything else exactly the same. No text.' $BASE
REF=$NODUCK; [ -f $REF ] || REF=$BASE
want left  && gen_new presets/01-left.png  'Three-quarter view: her head and body turned toward the viewer'"'"'s LEFT, looking left, gentle smile.' $REF
want right && gen_new presets/02-right.png 'Three-quarter view: her head and body turned toward the viewer'"'"'s RIGHT, looking right, gentle smile.' $REF
want up    && gen_new presets/03-up.png    'Front view, her face tilted UP, looking up at the sky with a happy open-mouth smile, chin raised.' $REF
want down  && gen_new presets/04-down.png  'Front view, her head tilted DOWN, looking down with soft half-closed eyes and a small smile, chin lowered, bangs falling forward.' $REF
want duck  && { u=$(higgsfield generate create seedream_v5_pro --prompt 'Character sheet of a cute chubby baby duckling companion, drawn in exactly the same soft retro 1990s cel anime style, line weight and faded color tone as the reference image: a round plump body and head almost one shape, fluffy pale cream-yellow down with a few fluffy tufts on top of the head, tiny black dot eyes, small pink cheeks, a wide open happy orange beak showing a pink mouth, short little wings raised happily, short orange feet. NO hat. Front view standing, centered, plain soft light-blue background, square frame. No text, no letters.' --image $BASE --aspect_ratio 1:1 --resolution 2k --wait 2>&1|tail -1); curl -sS -o presets/06-duck.png "$u"; echo presets/06-duck.png; }
want side  && gen_new presets/05-side.png  'Clean side profile view facing left, calm small smile.' $REF
python3 - <<'P'
# 기준 톤 맞춤 + 살짝 샤픈 (무료)
import glob
from PIL import Image, ImageFilter
for f in sorted(glob.glob('presets/0*.png')):
    Image.open(f).convert('RGB').filter(ImageFilter.UnsharpMask(radius=2,percent=60,threshold=3)).save(f)
P
echo done
