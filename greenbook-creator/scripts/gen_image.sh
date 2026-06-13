#!/usr/bin/env sh
# gen_image.sh — Backward-compatible wrapper for gen_media.sh generate
#
# This is a thin shim. New code should use `gen_media.sh` directly:
#   gen_media.sh generate  — image generation (multi-model)
#   gen_media.sh edit      — image edit (gpt-image-2 / gemini-*)
#   gen_media.sh video     — video generation (doubao-seedance-*)
#   gen_media.sh models    — list supported models + price
#   gen_media.sh groups    — list available groups for current key
#
# Original interface (preserved for backward compat):
#   gen_image.sh --prompt "..." --out path.png [--style default] [--size 1024x1024]
#   gen_image.sh --from-article article.md --image-desc "..." --out path.png
#   gen_image.sh "prompt" path.png [size]   (legacy positional)
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WRAPPER="$SCRIPT_DIR/gen_media.sh"

[ -x "$WRAPPER" ] || { echo "ERROR: gen_media.sh not found at $WRAPPER" >&2; exit 1; }

# Translate legacy positional args
if [ "$#" -ge 1 ] && [ "${1#--}" = "$1" ]; then
  # positional: prompt out [size]
  prompt="$1"; out="$2"; size="${3:-1024x1024}"
  set -- --prompt "$prompt" --out "$out" --size "$size"
fi

# Force generate subcommand + gpt-image-2 default for full backward compat
exec "$WRAPPER" generate --model gpt-image-2 "$@"
