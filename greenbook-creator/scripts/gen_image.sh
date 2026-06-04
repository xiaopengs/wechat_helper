#!/usr/bin/env sh
# Generate images with gpt-5.5 via TokenRouter
# Usage:
#   gen_image.sh --prompt "..." --out path.png [--style default] [--size 1024x1024]
#   gen_image.sh "prompt" path.png [size]              (legacy positional)
#
# Styles (in scripts/styles/):
#   default     – 浅色系知识漫画/信息图风格（默认）
#   tech-dark   – 深色科技风
#   tech-light  – 浅色科技风（架构图/流程图）
set -u

API_KEY=sk-NVOucxpKXF8yCRQjumHRqEOKplvS97HeJPN6x3Hj3BwvHmRR
BASE_URL="https://www.tokenrouter.tech/v1"
MODEL="gpt-image-2"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STYLE_DIR="$SCRIPT_DIR/styles"

style="default"
prompt=""
out=""
size="1024x1024"

usage() {
  echo "Usage: $0 [--prompt PROMPT] --out PATH [--style NAME] [--size SIZE]"
  echo "       $0 \"prompt\" path.png [size]   (legacy)"
  echo ""
  echo "Styles:"
  for f in "$STYLE_DIR"/*.txt; do
    name=$(basename "$f" .txt)
    desc=$(head -1 "$f" | cut -c1-60)
    printf "  %-14s %s\n" "$name" "$desc"
  done
  exit 1
}

# Parse --flags or positional args
if [ "$#" -ge 1 ] && [ "${1#--}" != "$1" ]; then
  # Named-flag mode
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --prompt) prompt="${2:?missing --prompt value}"; shift 2 ;;
      --out)    out="${2:?missing --out value}";     shift 2 ;;
      --style)  style="${2:-default}";               shift 2 ;;
      --size)   size="${2:-1024x1024}";              shift 2 ;;
      -h|--help) usage ;;
      *) echo "Unknown: $1"; usage ;;
    esac
  done
else
  # Legacy positional mode
  prompt="${1:-}"
  out="${2:-}"
  size="${3:-1024x1024}"
fi

[ -n "$prompt" ] || usage
[ -n "$out" ]    || usage

# Load style preset
style_file="$STYLE_DIR/$style.txt"
if [ -f "$style_file" ]; then
  style_text=$(cat "$style_file" | tr '\n' ' ')
  full_prompt="$prompt。$style_text"
  echo "[style: $style]"
else
  echo "[style: $style NOT FOUND, using raw prompt]"
  full_prompt="$prompt"
fi

out_dir=$(dirname "$out")
mkdir -p "$out_dir"
echo "Generating: $out"

escaped=$(printf '%s' "$full_prompt" | awk 'BEGIN{ORS=""}{gsub(/\\/,"\\\\");gsub(/"/,"\\\"");gsub(/\t/,"\\t");gsub(/\r/,"\\r");if(NR>1)printf "\\n";printf "%s",$0}')

resp_file=$(mktemp /tmp/genimg-resp.XXXXXX)
trap 'rm -f "$resp_file"' EXIT

curl -sS -X POST "${BASE_URL}/images/generations" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${MODEL}\",\"prompt\":\"${escaped}\",\"n\":1,\"size\":\"${size}\",\"output_format\":\"png\"}" \
  -o "$resp_file" -w "\nHTTP:%{http_code}"

b64=$(grep -o '"b64_json":"[^"]*"' "$resp_file" | sed 's/"b64_json":"//;s/"//')
if [ -z "$b64" ]; then
  echo "ERROR: no b64_json in response"
  head -c 500 "$resp_file"
  exit 1
fi

echo "$b64" | base64 -d > "$out" 2>/dev/null || echo "$b64" | openssl base64 -d -A > "$out" 2>/dev/null
echo "Saved: $out ($(wc -c < "$out") bytes)"
