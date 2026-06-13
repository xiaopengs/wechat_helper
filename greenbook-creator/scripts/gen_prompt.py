#!/usr/bin/env python3
"""Generate detailed image prompt from article content via LLM.

Supports two API formats:
  - openai-completions  (tokenrouter / openai compatible)
  - anthropic-messages (minimax M3)

Usage:
  gen_prompt.py --article article.md --desc "what to show" --style STYLE --out prompt.txt
  gen_prompt.py --article a.md --desc "..." --style default --out p.txt \\
                --model deepseek/deepseek-v4-pro \\
                --api openai --base-url https://www.tokenrouter.tech/v1 \\
                --api-key sk-...
"""
import json, urllib.request, sys, os, argparse

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Defaults — MiniMax M3 via Anthropic Messages API
# (matches openclaw.json's agents.defaults.model.primary)
#
# API key resolution (in order):
#   1. --api-key CLI flag
#   2. GEN_PROMPT_API_KEY env var
#   3. Read from openclaw.json (the running gateway's config)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEFAULT_MODEL    = "MiniMax-M3"
DEFAULT_API      = "anthropic"   # openai | anthropic
DEFAULT_BASE_URL = "https://api.minimaxi.com/anthropic"
PROVIDER_NAME    = "minimax"     # key in openclaw.json's models.providers


def load_api_key_from_openclaw(provider=PROVIDER_NAME):
    """Read API key from OpenClaw's running config (no hardcoded secrets)."""
    cfg_paths = [
        os.path.expanduser("~/.openclaw/openclaw.json"),
        "/home/ubuntu/.openclaw/openclaw.json",
    ]
    for p in cfg_paths:
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    cfg = json.load(f)
                key = cfg.get("models", {}).get("providers", {}).get(provider, {}).get("apiKey")
                if key:
                    return key
            except Exception:
                pass
    return None


def resolve_api_key(cli_value):
    if cli_value:
        return cli_value
    env_val = os.environ.get("GEN_PROMPT_API_KEY")
    if env_val:
        return env_val
    cfg_val = load_api_key_from_openclaw()
    if cfg_val:
        return cfg_val
    raise SystemExit("ERROR: no API key. Use --api-key, set GEN_PROMPT_API_KEY, or ensure openclaw.json is readable.")

STYLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles")

SYSTEM_PROMPT = """You are an expert image prompt engineer specializing in technical infographics, architecture diagrams, and knowledge-comic style illustrations for Chinese tech blog articles published on WeChat.

Your task: Based on the provided article content and image description, generate a DETAILED, OBJECTIVE, HIGHLY SPECIFIC image generation prompt in English for gpt-image-2.

CRITICAL RULES:
1. Be EXTREMELY specific about visual elements: name every component, its color, its position, its icon, its label
2. Use CONCRETE visual descriptions, never abstract concepts. Instead of "data flow", say "blue arrows with dotted lines connecting from module A to module B"
3. For architecture diagrams: describe each layer precisely, what is in it, where it sits, what connects it to other layers, what colors distinguish it
4. For comparison charts: describe exact column widths, exact content per cell, exact icons, exact bridge/connector styles between shared features
5. For UI screenshots: describe the window chrome (rounded corners radius, traffic light buttons), each panel (width, background color), the exact content visible
6. Include specific color hex codes when relevant: tech blue #2B6CB0, coral orange #E0533D, mint green #38A169, dark gray #2D3748, light gray #E2E8F0
7. The prompt MUST be 500-1000 characters. Be concise but information-dense. STRICT 1000-character limit.
8. Output ONLY the raw prompt text. No markdown formatting, no code fences, no explanations, no quotes, no preamble.
9. All text in the prompt must be in English.
10. Use REAL product names, feature names, numbers from the article content.
11. Describe the visual style explicitly: "knowledge comic infographic style, flat illustration, clean outlines, warm cream background, soft rounded corners, professional yet approachable"
12. If the article mentions specific products (QwenPaw, OpenClaw, Tauri, Python, Node.js, AgentScope), include recognizable visual representations of their logos, icons, or brand colors.
13. For WeChat article images, optimize for readability on mobile phone screens: clear visual hierarchy, adequate spacing between elements, not too cluttered."""


def load_style(name):
    path = os.path.join(STYLE_DIR, f"{name}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def call_anthropic(base_url, api_key, model, system, user, max_tokens=2000):
    """Anthropic Messages API format. Extracts text from content[] (skipping thinking blocks)."""
    req_body = json.dumps({
        "model": model,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "max_tokens": max_tokens,
        "temperature": 0.2
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/messages",
        data=req_body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
    )

    resp = json.loads(urllib.request.urlopen(req, timeout=90).read())
    # Anthropic: content[] can have thinking blocks first, then text blocks
    for block in resp.get("content", []):
        if block.get("type") == "text":
            return block["text"].strip()
    raise RuntimeError("No text block in Anthropic response")


def enforce_length(text, max_chars=1000):
    """Truncate text to max_chars, breaking at the last sentence boundary."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    # Try to break at last sentence end (., ;, ,)
    for sep in [".", ";", ",", " "]:
        idx = truncated.rfind(sep)
        if idx > max_chars * 0.6:  # don't break too early
            return truncated[:idx + 1].strip()
    return truncated.strip()


def call_openai(base_url, api_key, model, system, user, max_tokens=2000):
    """OpenAI chat completions format."""
    req_body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=req_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    resp = json.loads(urllib.request.urlopen(req, timeout=90).read())
    return resp["choices"][0]["message"]["content"].strip()


def generate_prompt(article_text, image_desc, style_desc, model, api, base_url, api_key):
    user_prompt = f"""Article content:
{article_text}

Image needed: {image_desc}

Visual style to apply: {style_desc}

Based on this article, generate a detailed, objective, information-rich image generation prompt. Include specific product names, feature names, module names, colors, and layout details from the article. The prompt must be in English, 500-1000 characters."""

    if api == "anthropic":
        generated = call_anthropic(base_url, api_key, model, SYSTEM_PROMPT, user_prompt, max_tokens=900)
    else:
        generated = call_openai(base_url, api_key, model, SYSTEM_PROMPT, user_prompt, max_tokens=900)

    generated = enforce_length(generated, max_chars=1000)

    # Strip markdown code fences if present
    if generated.startswith("```"):
        lines = generated.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        generated = "\n".join(lines).strip()

    return generated


def main():
    parser = argparse.ArgumentParser(description="Generate image prompt from article")
    parser.add_argument("--article",  required=True, help="Article markdown file")
    parser.add_argument("--desc",     required=True, help="What the image should depict (Chinese OK)")
    parser.add_argument("--style",    default="default", help="Style preset name")
    parser.add_argument("--out",      required=True, help="Output prompt text file")

    # LLM config (defaults = MiniMax M3)
    parser.add_argument("--model",    default=DEFAULT_MODEL, help=f"LLM model id (default: {DEFAULT_MODEL})")
    parser.add_argument("--api",      default=DEFAULT_API, choices=["openai", "anthropic"], help="API format")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")
    parser.add_argument("--api-key",  default=None, help="API key (default: read from openclaw.json or $GEN_PROMPT_API_KEY)")

    args = parser.parse_args()

    api_key = resolve_api_key(args.api_key)

    with open(args.article, "r", encoding="utf-8") as f:
        article = f.read()[:8000]

    style_desc = load_style(args.style)
    image_desc = args.desc

    print(f"Article:  {len(article)} chars", file=sys.stderr)
    print(f"Image:    {image_desc[:80]}...", file=sys.stderr)
    print(f"Style:    {args.style}", file=sys.stderr)
    print(f"Model:    {args.model}", file=sys.stderr)
    print(f"API:      {args.api} @ {args.base_url}", file=sys.stderr)
    print("Calling LLM...", file=sys.stderr)

    prompt = generate_prompt(
        article, image_desc, style_desc,
        args.model, args.api, args.base_url, api_key
    )

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"Prompt:   {len(prompt)} chars -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
