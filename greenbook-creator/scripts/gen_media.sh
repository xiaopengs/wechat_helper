#!/usr/bin/env sh
# gen_media.sh — Unified image & video generation via TokenRouter (www.juaiapi.com / tokenrouter.tech)
#
# Subcommands:
#   gen_media.sh generate --prompt "..." --out path.png [--model gpt-image-2] [--style default] ...
#   gen_media.sh edit     --prompt "..." --image src.png --out path.png [--model gpt-image-2] ...
#   gen_media.sh video    --prompt "..." --out path.mp4 [--model doubao-seedance-2.0-fast] ...
#   gen_media.sh models                         # list supported models + price
#   gen_media.sh groups                         # list available groups for current key
#
# Auth (priority):
#   1) env TOKENROUTER_API_KEY  /  OPENAI_API_KEY
#   2) ~/.openclaw/provider-auth.json → tokenrouter.api_key
#
# Compatible with `wechat_helper/greenbook-creator/scripts/gen_image.sh` via thin wrapper.
set -u

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Defaults
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STYLE_DIR="$SCRIPT_DIR/styles"
AUTH_FILE="${TOKENROUTER_AUTH_FILE:-$HOME/.openclaw/provider-auth.json}"
BASE_URL="${TOKENROUTER_BASE_URL:-https://www.tokenrouter.tech/v1}"
LLM_MODEL="deepseek/deepseek-v4-flash"

# Models (image)
DEFAULT_MODEL_IMG="gpt-image-2"
DEFAULT_MODEL_VID="doubao-seedance-2.0-fast"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Model registry (synced with /api/pricing; hardcoded as fallback)
#   model:                model name to call
#   type:                 image | video
#   group_base_price:     model_price (per image, or per second for video)
#   group:                cheapest group known to host it
#   sizes:                supported sizes (image only)
#   note:                 human note
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODEL_REGISTRY='[
  {"model":"gpt-image-2","type":"image","group_base_price":1,"group":"GPT-image-2","sizes":["1024x1024","1024x1536","1536x1024","auto"],"note":"OpenAI 图像,0.2 元/张(在 GPT-image-2 组)"},
  {"model":"gemini-2.5-flash-image","type":"image","group_base_price":0.2,"group":"Gemini","sizes":["1024x1024"],"note":"Google 图像,需 Gemini 组 key"},
  {"model":"gemini-3.1-flash-image-preview","type":"image","group_base_price":0.3,"group":"Gemini","sizes":["1024x1024"],"note":"Google 图像,需 Gemini 组 key"},
  {"model":"gemini-3-pro-image-preview","type":"image","group_base_price":0.5,"group":"Gemini","sizes":["1024x1024","2K","4K"],"note":"Google 图像,最高质量,需 Gemini 组 key"},
  {"model":"doubao-seedance-2.0-fast","type":"video","group_base_price":0,"group":"seedance","note":"字节方舟视频,快,需 seedance 组 key"},
  {"model":"doubao-seedance-2.0","type":"video","group_base_price":0,"group":"seedance","note":"字节方舟视频,高质量,需 seedance 组 key"}
]'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
info() { printf '  %s\n' "$*"; }

usage() {
  cat <<'USAGE'
gen_media.sh — TokenRouter 统一生图/生视频

Subcommands:
  generate   图像生成
  edit       图像编辑 (gpt-image-2 / gemini-*)
  video      视频生成 (doubao-seedance-*)
  models     列出支持的模型 + 价格
  groups     列出当前 key 可用的 group(检测凭据够用哪些模型)

generate 选项:
  --prompt TEXT         直接 prompt
  --prompt-file PATH    从文件读 prompt
  --out PATH            输出图片
  --model NAME          默认 gpt-image-2
  --size WxH            默认 1024x1024
  --quality low|medium|high|auto
  --n COUNT             生成数量(1-4),默认 1
  --style NAME          default | tech-dark | tech-light
  --from-article PATH   从文章 + LLM 生成 prompt
  --image-desc TEXT     (--from-article 配合) 描述图要画什么
  --force               覆盖已存在文件
  --dry-run             只打印请求,不真发

edit 选项:
  --prompt TEXT         编辑指令
  --image PATH          源图(可多次指定多图)
  --mask PATH           蒙版
  --out PATH            输出图
  --model NAME          默认 gpt-image-2
  --size WxH
  --force
  --dry-run

video 选项:
  --prompt TEXT
  --out PATH            输出 mp4
  --model NAME          默认 doubao-seedance-2.0-fast
  --seconds N           视频时长,默认 5
  --ratio 16:9|9:16|1:1
  --dry-run

USAGE
}

# Resolve API key
resolve_api_key() {
  if [ -n "${TOKENROUTER_API_KEY:-}" ]; then
    printf '%s' "$TOKENROUTER_API_KEY"; return 0
  fi
  if [ -n "${OPENAI_API_KEY:-}" ]; then
    printf '%s' "$OPENAI_API_KEY"; return 0
  fi
  if [ -f "$AUTH_FILE" ]; then
    # extract tokenrouter.api_key via grep+sed (no jq dep)
    sed -n 's/.*"tokenrouter"[^}]*"api_key"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$AUTH_FILE" | head -n 1
  fi
}

# Detect which groups a key belongs to (probe /api/user/self or fallback to /api/user/pricing with auth)
probe_groups() {
  api_key=$1
  # new-api / one-api style: GET /api/user/self
  resp=$(curl -sS --max-time 10 -H "Authorization: Bearer $api_key" \
    "${BASE_URL%/v1}/api/user/self" 2>/dev/null)
  if printf '%s' "$resp" | grep -q '"success":true'; then
    printf '%s' "$resp" | python3 -c "
import json, sys
try:
  d = json.load(sys.stdin)
  for g in d.get('data', {}).get('groups', []):
    ratio = d.get('data', {}).get('group_ratio', {}).get(g, '?')
    print(f'  {g}  (ratio={ratio})')
except Exception:
  pass
" 2>/dev/null
    return 0
  fi
  warn "无法探测 group(/api/user/self 未授权或不可用),将按模型直接尝试调用"
}

# Filter models by type and current key's groups (best-effort)
list_models() {
  type_filter=${1:-all}
  api_key=$(resolve_api_key)
  groups=$(probe_groups "$api_key" 2>/dev/null)
  printf '%s\n' "$MODEL_REGISTRY" | python3 -c "
import json, sys
models = json.loads(sys.stdin.read())
tf = '$type_filter'
groups = '''$groups'''.strip().splitlines()
group_names = {g.split()[0] for g in groups}
for m in models:
  if tf != 'all' and m['type'] != tf:
    continue
  available = '✓' if (not group_names or m['group'] in group_names) else '✗'
  print(f\"  {available}  {m['model']:35}  type={m['type']:5}  base={m['group_base_price']:5}  group={m['group']:14}  {m['note']}\")
"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Argument parsing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
command_name="${1-}"
if [ "$#" -gt 0 ]; then shift; fi

if [ -z "$command_name" ] || [ "$command_name" = "-h" ] || [ "$command_name" = "--help" ] || [ "$command_name" = "help" ]; then
  usage; exit 0
fi

case "$command_name" in
  models)
    type_filter="${1:-all}"
    api_key=$(resolve_api_key)
    if [ -z "$api_key" ]; then
      die "no API key found. set TOKENROUTER_API_KEY or write provider-auth.json"
    fi
    echo "━━━ Available groups for current key ━━━"
    groups=$(probe_groups "$api_key")
    if [ -z "$groups" ]; then
      echo "  (探测失败,以下展示所有模型:✓ 表示无需换 key 即可调)"
    else
      printf '%s\n' "$groups"
    fi
    echo
    echo "━━━ Models (${type_filter}) ━━━"
    list_models "$type_filter"
    exit 0
    ;;
  groups)
    api_key=$(resolve_api_key)
    [ -n "$api_key" ] || die "no API key"
    probe_groups "$api_key"
    exit 0
    ;;
  generate|edit|video) ;;
  *) usage >&2; die "unknown subcommand: $command_name" ;;
esac

# Common
prompt=""
prompt_file=""
out=""
model=""
size=""
quality=""
n="1"
style="default"
from_article=""
image_desc=""
force="0"
dry_run="0"
seconds="5"
ratio="16:9"
images=""
mask=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --prompt)        prompt="${2:?}"; shift 2 ;;
    --prompt-file)   prompt_file="${2:?}"; shift 2 ;;
    --out)           out="${2:?}"; shift 2 ;;
    --model)         model="${2:?}"; shift 2 ;;
    --size)          size="${2:?}"; shift 2 ;;
    --quality)       quality="${2:?}"; shift 2 ;;
    --n)             n="${2:?}"; shift 2 ;;
    --style)         style="${2:-default}"; shift 2 ;;
    --from-article)  from_article="${2:?}"; shift 2 ;;
    --image-desc)    image_desc="${2:?}"; shift 2 ;;
    --force)         force="1"; shift ;;
    --dry-run)       dry_run="1"; shift ;;
    --seconds)       seconds="${2:?}"; shift 2 ;;
    --ratio)         ratio="${2:?}"; shift 2 ;;
    --image)         images="${images:+${images}\n}${2:?}"; shift 2 ;;
    --mask)          mask="${2:?}"; shift 2 ;;
    -h|--help)       usage; exit 0 ;;
    *) die "unknown option: $1" ;;
  esac
done

# Validate
[ -n "$out" ] || die "--out required"
if [ "$force" != "1" ] && [ -f "$out" ] && [ "$dry_run" != "1" ]; then
  die "file exists (use --force to overwrite): $out"
fi

# Resolve prompt
read_prompt() {
  if [ -n "$prompt" ] && [ -n "$prompt_file" ]; then
    die "use --prompt or --prompt-file, not both"
  fi
  if [ -n "$prompt_file" ]; then
    [ -f "$prompt_file" ] || die "prompt file not found: $prompt_file"
    cat "$prompt_file"
  else
    printf '%s' "$prompt"
  fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Image generation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
do_generate() {
  model=${model:-$DEFAULT_MODEL_IMG}
  size=${size:-1024x1024}

  # Step 1 (optional): LLM-generated prompt from article
  if [ -n "$from_article" ]; then
    [ -n "$image_desc" ] || die "--image-desc required with --from-article"
    [ -f "$from_article" ] || die "article not found: $from_article"
    echo "━━━ Step 1: LLM → prompt ━━━"
    info "article: $from_article"
    info "desc:    $image_desc"
    info "style:   $style"
    tmp_prompt=$(mktemp /tmp/genmedia-prompt.XXXXXX)
    if ! python3 "$SCRIPT_DIR/gen_prompt.py" \
        --article "$from_article" --desc "$image_desc" \
        --style "$style" --out "$tmp_prompt" 2>&1; then
      rm -f "$tmp_prompt"
      die "LLM prompt generation failed"
    fi
    prompt=$(cat "$tmp_prompt")
    out_dir=$(dirname "$out")
    mkdir -p "$out_dir"
    cp "$tmp_prompt" "${out}.prompt.txt"
    rm -f "$tmp_prompt"
    info "prompt saved: ${out}.prompt.txt"
  fi

  # Resolve final prompt
  base_prompt=$(read_prompt)
  [ -n "$base_prompt" ] || die "missing prompt (--prompt or --from-article)"

  # Append style preset
  style_file="$STYLE_DIR/$style.txt"
  if [ -f "$style_file" ]; then
    style_text=$(tr '\n' ' ' < "$style_file")
    full_prompt="${base_prompt}。${style_text}"
  else
    full_prompt="$base_prompt"
  fi

  mkdir -p "$(dirname "$out")"
  echo "━━━ Step 2: Image Generation ━━━"
  info "model:  $model"
  info "out:    $out"
  info "size:   $size"
  info "n:      $n"
  info "style:  $style"

  # Build JSON body
  json_body=$(json_object \
    "model" "$model" \
    "prompt" "$full_prompt" \
    "n" "$n" \
    "size" "$size" \
    "output_format" "png")
  if [ -n "$quality" ]; then
    json_body=$(json_insert "$json_body" "quality" "$quality")
  fi

  if [ "$dry_run" = "1" ]; then
    echo "[DRY-RUN] POST $BASE_URL/images/generations"
    echo "[DRY-RUN] body:"
    echo "$json_body" | python3 -m json.tool 2>/dev/null || echo "$json_body"
    return 0
  fi

  resp_file=$(mktemp /tmp/genmedia-resp.XXXXXX)
  trap 'rm -f "$resp_file"' EXIT

  # Retry loop: TokenRouter 上游 OpenAI moderation 偶尔 429/502,自动重试 3 次(指数退避)
  max_retries=3
  retry_delay=8
  http_code="000"
  for attempt in $(seq 1 $((max_retries + 1))); do
    http_code=$(curl -sS --max-time 180 -X POST "$BASE_URL/images/generations" \
      -H "Authorization: Bearer $(resolve_api_key)" \
      -H "Content-Type: application/json" \
      -d "$json_body" \
      -o "$resp_file" -w "%{http_code}")
    if [ "$http_code" = "200" ]; then
      break
    fi
    # Only retry on transient moderation errors
    if grep -qE "moderation service unavailable|moderation response status=(429|502|503|504)" "$resp_file"; then
      if [ "$attempt" -le "$max_retries" ]; then
        warn "moderation 上游 $http_code 限流/异常,$retry_delay s 后重试 (attempt $attempt/$max_retries)..."
        sleep "$retry_delay"
        retry_delay=$((retry_delay * 2))
        continue
      fi
    fi
    break
  done

  if [ "$http_code" != "200" ]; then
    echo "HTTP $http_code"
    head -c 600 "$resp_file"; echo
    # Friendly error if model not in default group
    if grep -q "No available channel" "$resp_file"; then
      echo
      warn "当前 key 不在 ${model} 所在 group。"
      warn "去 juaiapi.com 控制台 → 用户组,把 key 加到对应 group。"
      warn "  模型 ${model} 需要的 group: $(printf '%s' "$MODEL_REGISTRY" | python3 -c "import json,sys;m=[x for x in json.load(sys.stdin) if x['model']=='$model'];print(m[0]['group'] if m else '?')")"
    fi
    exit 1
  fi

  save_media_response "$resp_file" "$out" "image"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Image edit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
do_edit() {
  model=${model:-$DEFAULT_MODEL_IMG}
  size=${size:-1024x1024}
  [ -n "$images" ] || die "--image required for edit"
  base_prompt=$(read_prompt)
  [ -n "$base_prompt" ] || die "missing prompt"
  [ -n "$mask" ] || mask=""

  mkdir -p "$(dirname "$out")"
  echo "━━━ Image Edit ━━━"
  info "model: $model"
  info "out:   $out"
  info "size:  $size"

  if [ "$dry_run" = "1" ]; then
    echo "[DRY-RUN] multipart POST to $BASE_URL/images/edits"
    echo "[DRY-RUN] image(s):"; printf '  %s\n' $images
    echo "[DRY-RUN] prompt: $base_prompt"
    return 0
  fi

  # Build multipart with curl -F
  args="-sS --max-time 180 -X POST $BASE_URL/images/edits \
    -H \"Authorization: Bearer $(resolve_api_key)\" \
    -F \"model=$model\" \
    -F \"prompt=$base_prompt\" \
    -F \"size=$size\" \
    -F \"n=$n\""
  for img in $images; do
    [ -f "$img" ] || die "image not found: $img"
    args="$args -F \"image=@$img\""
  done
  if [ -n "$mask" ]; then
    [ -f "$mask" ] || die "mask not found: $mask"
    args="$args -F \"mask=@$mask\""
  fi

  resp_file=$(mktemp /tmp/genmedia-resp.XXXXXX)
  trap 'rm -f "$resp_file"' EXIT

  http_code=$(eval "curl $args -o $resp_file -w '%{http_code}'")

  if [ "$http_code" != "200" ]; then
    echo "HTTP $http_code"
    head -c 600 "$resp_file"; echo
    exit 1
  fi

  save_media_response "$resp_file" "$out" "image"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Video generation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
do_video() {
  model=${model:-$DEFAULT_MODEL_VID}
  base_prompt=$(read_prompt)
  [ -n "$base_prompt" ] || die "missing prompt"
  mkdir -p "$(dirname "$out")"
  echo "━━━ Video Generation ━━━"
  info "model:   $model"
  info "out:     $out"
  info "seconds: $seconds"
  info "ratio:   $ratio"

  json_body=$(json_object \
    "model" "$model" \
    "prompt" "$base_prompt" \
    "seconds" "$seconds" \
    "ratio" "$ratio")

  if [ "$dry_run" = "1" ]; then
    echo "[DRY-RUN] POST $BASE_URL/video/generations"
    echo "[DRY-RUN] body:"
    echo "$json_body" | python3 -m json.tool 2>/dev/null || echo "$json_body"
    return 0
  fi

  resp_file=$(mktemp /tmp/genmedia-resp.XXXXXX)
  trap 'rm -f "$resp_file"' EXIT

  # Retry on transient upstream errors
  max_retries=2
  retry_delay=10
  http_code="000"
  for attempt in $(seq 1 $((max_retries + 1))); do
    http_code=$(curl -sS --max-time 600 -X POST "$BASE_URL/video/generations" \
      -H "Authorization: Bearer $(resolve_api_key)" \
      -H "Content-Type: application/json" \
      -d "$json_body" \
      -o "$resp_file" -w "%{http_code}")
    if [ "$http_code" = "200" ] || [ "$http_code" = "202" ]; then
      break
    fi
    if grep -qE "moderation|rate.?limit|temporarily" "$resp_file"; then
      if [ "$attempt" -le "$max_retries" ]; then
        warn "video 上游 $http_code 异常,$retry_delay s 后重试 (attempt $attempt/$max_retries)..."
        sleep "$retry_delay"
        retry_delay=$((retry_delay * 2))
        continue
      fi
    fi
    break
  done

  if [ "$http_code" != "200" ] && [ "$http_code" != "202" ]; then
    echo "HTTP $http_code"
    head -c 600 "$resp_file"; echo
    if grep -q "No available channel" "$resp_file"; then
      warn "${model} 需要 seedance 组 key"
    fi
    exit 1
  fi

  # Video response: try b64 first, then URL (could be polling URL, warn)
  save_media_response "$resp_file" "$out" "video"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JSON helpers (no jq dep) + media save
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
json_object() {
  # arg pairs: key value key value ...
  python3 -c "
import json, sys
d = {}
args = sys.argv[1:]
for i in range(0, len(args), 2):
  k = args[i]; v = args[i+1]
  if v == '': continue
  # auto-cast numbers
  try:
    d[k] = int(v) if v.lstrip('-').isdigit() else (float(v) if v.replace('.','',1).lstrip('-').isdigit() else v)
  except Exception:
    d[k] = v
print(json.dumps(d, ensure_ascii=False))
" "$@"
}

json_insert() {
  # insert key=value into existing JSON object (string-replace via python)
  body=$1; key=$2; value=$3
  python3 -c "
import json, sys
d = json.loads('''$body''')
d['$key'] = '''$value'''
print(json.dumps(d, ensure_ascii=False))
"
}

save_media_response() {
  resp_file=$1; out=$2; kind=$3
  # Try b64_json
  b64=$(grep -o '"b64_json":"[^"]*"' "$resp_file" | head -1 | sed 's/"b64_json":"//;s/"$//')
  if [ -n "$b64" ]; then
    printf '%s' "$b64" | base64 -d > "$out" 2>/dev/null \
      || printf '%s' "$b64" | openssl base64 -d -A > "$out" 2>/dev/null
    info "saved (b64): $(wc -c < "$out") bytes"
  else
    # Try direct url
    url=$(grep -oE '"url":"[^"]+"' "$resp_file" | head -1 | sed 's/"url":"//;s/"$//')
    # Some APIs nest { data: [{ url: ... }] }
    if [ -z "$url" ]; then
      url=$(grep -oE '"video_url":"[^"]+"' "$resp_file" | head -1 | sed 's/"video_url":"//;s/"$//')
    fi
    if [ -n "$url" ]; then
      curl -sS --max-time 120 -o "$out" "$url"
      info "saved (url): $(wc -c < "$out") bytes"
    else
      echo "ERROR: no b64_json/url in response"
      head -c 800 "$resp_file"; echo
      exit 1
    fi
  fi

  # Image post-process: WeChat compression
  if [ "$kind" = "image" ]; then
    if command -v python3 >/dev/null 2>&1; then
      python3 -c "from PIL import Image; i=Image.open('$out'); print(f'  Dimensions: {i.size[0]}x{i.size[1]}')" 2>/dev/null || true
      size_bytes=$(wc -c < "$out")
      if [ "$size_bytes" -gt 950000 ]; then
        info "size ${size_bytes} bytes > 950KB, optimizing..."
        python3 -c "
from PIL import Image
import os
img = Image.open('$out')
orig = os.path.getsize('$out')
m = img.mode if img.mode in ('RGB','RGBA','P') else 'RGB'
if m == 'RGBA': img.save('$out','PNG',optimize=True)
else: img.save('$out','PNG',optimize=True)
new_sz = os.path.getsize('$out')
print(f'  PNG optimize: {orig//1024}KB -> {new_sz//1024}KB')
if new_sz > 950000:
  img = Image.open('$out')
  if img.mode == 'RGBA':
    img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
  elif img.mode == 'RGB':
    img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
  img.save('$out','PNG',optimize=True)
  final = os.path.getsize('$out')
  print(f'  Quantize 256c: {new_sz//1024}KB -> {final//1024}KB')
  if final > 950000:
    img = Image.open('$out')
    if img.mode == 'RGBA':
      bg = Image.new('RGB', img.size, (255,255,255))
      bg.paste(img, mask=img.split()[3])
      img = bg
    img.save('$out','JPEG',quality=92,optimize=True)
    final2 = os.path.getsize('$out')
    print(f'  JPEG q92: {final//1024}KB -> {final2//1024}KB')
" 2>/dev/null
      fi
    fi
  fi

  info "done: $out"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dispatch
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
case "$command_name" in
  generate) do_generate ;;
  edit)     do_edit ;;
  video)    do_video ;;
esac
