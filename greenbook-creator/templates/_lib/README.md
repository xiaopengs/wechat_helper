# _lib — Shared scripts for greenbook HTML card templates

`render.py` 和 `send_qq.mjs` 是所有「HTML/Playwright 8 张卡」模板的共用脚本（参数化版本）。
各项目模板（`qm-greenbook/`、`tie-tu-hao-monkey-notes/`、`repo-overview/` 的 HTML 卡分支等）通过 `scripts/render.py` 和 `scripts/send_qq.mjs` 的 thin wrapper 调用这两个脚本，避免重复实现。

## 为什么放 _lib/

- 早期每个项目自带的 `scripts/render.py` 是硬编码副本（`BASE_DIR = /home/ubuntu/.openclaw/workspace/output/<name>`），改 bug 要 N 处同步
- QQ 收件人 `OPENID` 以前散落在多个 `.mjs` 里
- `output/<name>/scripts/send_qq_card8_only.mjs` 这种补丁脚本证明主脚本需要 `--only N` 重发能力

## render.py — HTML → PNG

```bash
# 项目目录下跑（最常见用法）
python3 ../_lib/render.py --base-dir .

# 或在任意位置
python3 _lib/render.py --base-dir /path/to/project
```

参数：
- `--base-dir PATH`  — 项目根（含 html/ + images/）
- `--html-dir NAME`  — HTML 源目录，默认 `html`
- `--out-dir NAME`   — PNG 输出目录，默认 `images`
- `--width N` / `--height N` — 默认 1080×1440
- `--dpr N`          — device_scale_factor，默认 2（输出 2160×2880 retina PNG）

依赖：`playwright` + Chromium（`pip install playwright && playwright install chromium`）。

## send_qq.mjs — PNG → QQ bot C2C

```bash
# 项目目录下
node ../_lib/send_qq.mjs --config config.json

# 只重发第 8 张（覆盖前次失败）
node ../_lib/send_qq.mjs --config config.json --only 8

# 指定图片目录（CI / 临时输出）
node ../_lib/send_qq.mjs --config config.json --img-dir /tmp/out
```

依赖：项目根有 `config.json`（openid / cover_text / captions），`~/.openclaw/openclaw.json` 的 `channels.qqbot.{appId, clientSecret}`，且 `openclaw-qqbot` npm 已全局装。

## 项目模板里怎么用

每个模板目录下：
```
qm-greenbook/
├── config.json         ← openid + cover_text + captions
├── html/               ← card_1.html ... card_8.html + base.css
├── images/             ← 渲染产物（gitignore，不入库）
├── scripts/
│   ├── render.py       ← thin wrapper
│   └── send_qq.mjs     ← thin wrapper
└── README.md
```

两个 wrapper 的内容（仅几行）：

**scripts/render.py**:
```python
#!/usr/bin/env python3
"""Render <project> HTML cards via shared _lib/render.py."""
import subprocess, sys
from pathlib import Path
LIB = Path(__file__).resolve().parent.parent.parent / "_lib" / "render.py"
PROJ = Path(__file__).resolve().parent.parent
sys.exit(subprocess.call(
    [sys.executable, str(LIB), "--base-dir", str(PROJ)] + sys.argv[1:]
))
```

**scripts/send_qq.mjs**:
```js
// Send <project> cards via shared _lib/send_qq.mjs
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
const __dirname = dirname(fileURLToPath(import.meta.url));
const LIB     = resolve(__dirname, "..", "..", "_lib", "send_qq.mjs");
const CONFIG  = resolve(__dirname, "..", "config.json");
execFileSync("node", [LIB, "--config", CONFIG, ...process.argv.slice(2)], { stdio: "inherit" });
```

## 新建一个 HTML 卡项目（5 步）

```bash
# 1. 复制精简模板
cp -r templates/qm-greenbook output/<my-topic>-greenbook
cd output/<my-topic>-greenbook

# 2. 改 html/base.css :root 配色变量
$EDITOR html/base.css

# 3. 改 html/card_*.html 的内容（8 张）
$EDITOR html/card_{1..8}.html

# 4. 改 config.json 的 cover_text + captions
$EDITOR config.json   # openid 一般不变

# 5. 渲染 + 发送
python3 scripts/render.py
node    scripts/send_qq.mjs
```

## 跨模板改一处生效

`render.py` / `send_qq.mjs` 改动后，**所有 wrapper 自动跟着新**（subprocess 调用）。
无需修改各项目副本，git diff 只看 `_lib/` 即可。

## 历史

- 2026-08-05：从 `output/qm-greenbook/` 和 `templates/tie-tu-hao-monkey-notes/` 提取共用的 render.py + send_qq.mjs，参数化（`--base-dir` / `--config` / `--only` / `--img-dir`）