#!/usr/bin/env bash
# 生成封面右侧讽刺插画底图（1:1），主题：AI 替代人
# 用法: bash gen_cover_satire.sh [输出文件名]
set -e
cd "$(dirname "$(readlink -f "$0")")"
export MINIMAX_API_KEY="$(python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.openclaw/provider-auth.json')))['minimax']['api_key'])")"
export MINIMAX_API_BASE="https://api.minimaxi.com/v1"
PROMPT='Minimalist light line-art illustration on pure white background, thin black outlines, sparse and clean. Perfectly square composition where the subjects are drawn LARGE and fill the frame edge to edge with only a small even margin, no big empty areas. A deadpan satirical cartoon about AI replacing human workers, drawn as plain stick figures. Scene: in the upper part, four square-headed robot stick figures (thin antenna on head, rectangular torso) sit in a row busily typing at open laptops behind a desk; in the lower left a human stick figure stands holding a large round approval stamp; at the lower right another human stick figure walks away carrying a cardboard box of personal belongings. Understated absurd office satire. Only two accent colors allowed and used sparingly: light blue #1a73e8 and soft orange #ff6b35 for the laptop screens. No text, no letters, no words, no numbers, no labels, no captions, no speech bubbles anywhere. Flat vector sketch style, editorial tech illustration.'
OUT="${1:-cover_satire_raw.png}"
python3 /home/ubuntu/.openclaw/skills/frontend-dev/scripts/minimax_image.py "$PROMPT" -o "$OUT" --ratio 1:1
python3 -c "
from PIL import Image
im=Image.open('$OUT'); print('raw size', im.size)
"
