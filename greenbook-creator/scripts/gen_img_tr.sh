#!/usr/bin/env sh
# Wrapper: delegates to gen_image.sh (now with URL fallback + auto-compress built in)
exec "$(dirname "$0")/gen_image.sh" "$@"
