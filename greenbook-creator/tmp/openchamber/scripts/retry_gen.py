#!/usr/bin/env python3
"""Retry-based direct TokenRouter gpt-image-2 generation for cards 4-8."""
import base64
import json
import os
import sys
import time
import urllib.request

BASE = "https://www.tokenrouter.tech/v1/images/generations"
KEY = "sk-NVOucxpKXF8yCRQjumHRqEOKplvS97HeJPN6x3Hj3BwvHmRR"
PROMPTS_DIR = "/home/ubuntu/.openclaw/workspace/wechat_helper/greenbook-creator/tmp/openchamber/prompts"
OUT_DIR = "/home/ubuntu/.openclaw/workspace/wechat_helper/greenbook-creator/tmp/openchamber/images"
STYLE = "浅色系配色（米白/奶油白底色，柔和天蓝、薄荷绿、珊瑚橙、淡紫等低饱和度点缀色）。知识漫画/信息图风格，扁平化设计，线条干净利落，构图清晰有层次，图要有信息量，适合知识科普类公众号配图。整体明亮、清爽、专业，不暗沉。"


def load_prompt(card: int) -> str:
    base = open(os.path.join(PROMPTS_DIR, "base_prompt.txt")).read().strip()
    block = open(os.path.join(PROMPTS_DIR, f"card_{card}_content_block.txt")).read().strip()
    return f"{base}\n{block}。{STYLE}"


def gen(card: int, max_attempts: int = 6) -> bool:
    prompt = load_prompt(card)
    out_path = os.path.join(OUT_DIR, f"card_{card}.png")
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1536",
        "quality": "auto",
        "output_format": "png",
    }
    data = json.dumps(payload).encode()
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(
            BASE, data=data, method="POST",
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()[:400]
            print(f"  card_{card} attempt {attempt}: HTTP {e.code} {err_body}", flush=True)
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(15 * attempt)
                continue
            return False
        except Exception as e:
            print(f"  card_{card} attempt {attempt}: {e}", flush=True)
            time.sleep(15)
            continue

        img = None
        if "data" in body and body["data"]:
            item = body["data"][0]
            if "b64_json" in item:
                img = base64.b64decode(item["b64_json"])
            elif "url" in item:
                with urllib.request.urlopen(item["url"], timeout=120) as r:
                    img = r.read()
        if img is None:
            print(f"  card_{card}: no image in response: {str(body)[:300]}", flush=True)
            return False
        with open(out_path, "wb") as f:
            f.write(img)
        print(f"  card_{card} OK -> {out_path} ({len(img)} bytes)", flush=True)
        return True
    return False


if __name__ == "__main__":
    cards = [int(c) for c in sys.argv[1:]] if len(sys.argv) > 1 else [4, 5, 6, 7, 8]
    ok, fail = 0, []
    for c in cards:
        print(f"=== card_{c} ===", flush=True)
        if gen(c):
            ok += 1
        else:
            fail.append(c)
    print(f"DONE ok={ok} fail={fail}", flush=True)
