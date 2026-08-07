# architecture-ocr-greenbook · 架构图拆解（1080×1440 × 8P）

> **设计哲学**：工程蓝图风 · 6 节章节卡 · 截断问题的根因解药。
> **核心创新**：分节提取协议 — 不让 LLM 一次描述整张图，而是**枚举区块 → 逐块结构化提取 → 校验缺失字段再补**，永远不会在 "≥50 lines" 处嘎断。
> **数据源**：架构图（OCR）/ README + AGENTS.md（文档） / 两者混合 — 同一套 8 卡模板全部消化。

## 为什么这个模板存在

拆解一张架构图时，最容易踩的坑：

1. 让 LLM「用自由文本描述这张架构图」→ 单次输出超 token 限制 → **在某个句子中间嘎断**（最常见的就是 "≥50 lines" 那里）
2. 截断是**静默**的 — 你不知道丢了什么段落，丢的内容要不要紧
3. 想修只能重跑整张图，又得重新数 token

**这套模板的做法：把"整段描述"切成"逐区块独立提取"**。

```
旧做法：  Describe this image in detail
新做法：
  Stage 1:  List every visible block as JSON       (≤ 12 项)
  Stage 2:  Extract structured content per block  (per 段 ≤ 300 tokens)
  Stage 3:  Validate fields; retry only missing   (脚本可机器校验)
  Stage 4:  Merge into YAML data file
```

每次输出 token 上限 ≤ 300，6 段总和 ≤ 1800 远低于模型上限。**永远不会截断，永远知道哪一段没填满，可重试**。

## 模板结构

```
templates/architecture-ocr-greenbook/
├── README.md                  # 本文件
├── _schema.yaml               # 数据 schema + 字段约束
├── html/
│   ├── base.css               # 工程蓝图风（1080×1440 通用样式）
│   ├── card_template_1.html ~ card_template_8.html   # 8 张空白骨架
│   ├── card_1.html ~ card_8.html                     # OCR Review 填好的实例（canonical 示例）
├── data/
│   └── ocr-review.yaml        # OCR Review 架构图拆解数据
├── prompts/
│   ├── section-enumerate.md   # Stage 1 · 枚举所有视觉区块
│   ├── section-extract.md     # Stage 2 · 逐区块独立提取
│   └── captions.md            # P1-P8 单图配文模板
├── scripts/
│   ├── render.py              # thin wrapper → ../_lib/render.py
│   └── send_qq.mjs            # thin wrapper → ../_lib/send_qq.mjs
├── config.json                # openid + cover_text + captions（OCR Review 实例）
├── images/
│   └── card_1.png ~ card_8.png  # 渲染产物（2160×2880 retina PNG）
└── examples/
    └── pi/                    # 第二实例：earendil-works/pi 验证用
        ├── data/pi.yaml       # pi 架构拆解数据（README + AGENTS.md 提取）
        ├── html/card_*.html   # 填好的 8 张
        ├── scripts/           # 同上 thin wrapper
        ├── config.json
        └── images/            # pi 渲染产物
```

## 八页固定结构

| 页 | 主题 | 数据字段 | 视觉要素 |
|---|---|---|---|
| 1 | 封面 | `meta` + `cover` | 中央节点 + 4 个侧节点 + 3-4 个数据 chip + 收束条 |
| 2 | 全局视角 | `overview` | 流水线（5-6 节点 + 箭头）+ Key Path 卡 + 6 节 deck |
| 3-7 | 章节卡 × 5 | `sections[0..4]` | 章节色卡 + bullets + sub-blocks（颜色循环 green/blue/purple/orange/red） |
| 8 | 章节卡 6 + 输出 | `sections[5]` + `output_trio` | 章节色卡（cyan）+ 3 件套 trio + 收束条 |

**6 个 section 是关键**：原图有多少个视觉区块，模板就拆多少 section 对应 P3-P8。如果图只有 5 个区块，把最后一张合成"输出三件套"；如果有 7+ 个，合并相邻章节即可。

## 截断问题的根因分析

| 旧做法（坏） | 新做法（好） |
|--------------|--------------|
| "Describe this architecture diagram in detail" | "List every visible block as JSON, no prose" |
| 单次输出 ~2000 tokens，超模型限制后嘎断 | 每次 ≤ 12 项 JSON 对象 / 每段 ≤ 300 tokens |
| 截断是静默的 — 不知道丢了什么 | 校验 `count == expected`，缺了就重跑 |
| 整张图必须重跑才能修 | 只重跑缺失 section |

**实测**：OCR Review 原图描述在 "≥50 lines" 处被截断（约第 4 节中段）。本模板 6 个 section 字段全部完整 ✓。

## 两种数据源都支持

模板的设计是**数据源无关**的 — 只关心「图/文档里有几个独立区块，每个区块有什么字段」，不关心来源。

### 数据源 A：架构图 OCR（OCR Review 实例）
- 输入：架构图 PNG/JPG
- 提取协议：Stage 1 视觉识别 + Stage 2 结构化提取
- 适用：技术博客、架构分享、白皮书里的图

### 数据源 B：README + AGENTS.md（pi 验证实例）
- 输入：项目 README + AGENTS.md 文本
- 提取协议：Stage 1 按章节切分（标题/列表/代码块）+ Stage 2 抽取要点
- 适用：GitHub 项目架构文档

两种数据源走同一个 `_schema.yaml`，同一套 8 卡 HTML，同一个 `_lib/render.py` 渲染。

## 数据 schema 摘要

```yaml
meta:        { name, kicker, stars_text, version, source, source_date, source_kind }
cover:       { tagline_left, tagline_right, subline, central_node_*, side_nodes[4] }
overview:    { title, description, flow_steps[5-6], key_path }
sections:    [{ section_index, title_en, title_zh, color, bullets[3-5],
                details, sub_blocks[0-6] }, ...  # 必填 6 项
output_trio: [{ label, sub, color }, ...]       # 必填 3 项
closing:     { one_liner, protocol_note }
footer_label: "项目名 · 2026.08"
```

完整 schema 见 `_schema.yaml`。

## 配色变量（base.css :root）

```css
--green / --blue / --purple / --orange / --red / --cyan    # 6 节章节色（按视觉区块顺序循环）
--green-d / --blue-d / --purple-d / ...                    # 深色（band 标题栏用）
--green-l / --blue-l / --purple-l / ...                    # 浅色（section-card 背景用）
--bg / --ink / --ink-2 / --ink-3 / --grid                  # 底色与墨色
--border / --shadow-hard / --shadow-soft                   # 描边与阴影
```

> 改主题色只换 `:root` 变量值即可，所有 section-card / pipeline / trio 自动跟随。

## CSS class 速查

### 容器
- `.card` — 1080×1440 内容容器，padding 56px 64px

### Header
- `.label-tag` (`.green|.blue|.purple|.orange|.red|.cyan|.pink|.gray` 8 色前缀)
  - 含 `.dot` 小圆点（带颜色）
- `.page-num` — 右上角页码徽章（深底白字）

### 主标 / 副标
- `.title` (86px / 92px) / `.title-sm` (64px) — 主标题
- `.title .hl` — 黄/绿底高亮短语（用 `::after` 实现色块底）
- `.subtitle` (30px) — 副标灰字

### Chip / 数据徽章
- `.chip` (`.green|.blue|.purple|.orange|.red|.cyan`) — 圆角药丸
  - 含 emoji / 简短文字

### 章节主卡（最常用）
- `.section-card` (`.green|.blue|.purple|.orange|.red|.cyan|.gray` 7 色)
  - `.band` — 顶部色块标题栏（深色字）
    - 含 `<span class="num">` 编号圈
  - `.body` — 内容区
    - `<h3>` 主标题（38px）
    - `.zh` 中文副标（26px 灰）
    - `<ul class="bullet-list">` 列表
    - `.details` 灰色细节条
- `.sub-grid` (`.cols-2|.cols-3|.cols-4`) — 子块网格
- `.sub-block` — 子块（带 `.label` + `.desc`）

### 流水线
- `.pipeline` — 横向 flex 容器
- `.pipeline .node` (`.green|.blue|.purple|.orange|.red|.cyan`)
  - `.n` 编号（16px 灰）+ `.lbl` 标签（18px 粗体）
- `.pipeline .arrow` — 节点间黑箭头

### 收束条 / Trio
- `.closing` — 底部黑底白字收束条（带绿色圆点 + `<b>` 加粗）
- `.trio` — 3 列网格
- `.trio .cell` (`.blue|.orange|.purple|.green|.cyan|.red`) — 单格
  - `.lab` 标签 / `.sub` 描述

### 列表
- `.bullet-list` (`.green|.blue|.purple|.orange|.cyan`) — 带彩色方块 bullet
- `.warn-row` — 警告条（含 `.icon` + `.text`）

### 等宽 / 装饰
- `.mono` — JetBrains Mono 等宽字
- `.central-node` — 封面中央节点
- `.side-node` (`.green|.blue|.purple|.orange`) — 封面四角侧节点

### Footer
- `.footer` — 绝对定位底部（48px）
- `.footer .source` — 来源（等宽字 18px）
- `.footer .label` — 右下标签（含绿色圆点 `.icon`）

## 🚀 复用流程（5 步）

### 1. 复制模板骨架
```bash
cp -r ~/.openclaw/workspace/wechat_helper/greenbook-creator/templates/architecture-ocr-greenbook \
      ~/.openclaw/workspace/<你的主题>-greenbook
cd <你的主题>-greenbook
rm -rf images/*  # 清空旧渲染
```

### 2. 用分节提取协议生成 YAML

```bash
# Stage 1: 枚举图中区块
# 把图片丢给 vision LLM（gpt-4v / Claude / Gemini 任意），用 prompts/section-enumerate.md 提示词
# 输出 ~12 项 JSON 数组

# Stage 2: 逐区块独立提取
# 对每项 JSON 单独调用 LLM，用 prompts/section-extract.md 提示词
# 每段输出 100-300 tokens，永远不会被截断

# Stage 3: 校验（人工目测 或 脚本自动）
# - 每段 bullets 3-5 条
# - 每段 details 10-30 字
# - 每段 title_zh 4-12 字
# 缺哪个字段就只重跑那段

# Stage 4: 写到 YAML
# 对照 _schema.yaml，把校验通过的 JSON 段合并成 data/<topic>.yaml
```

### 3. 改 8 张卡 HTML
编辑 `html/card_*.html`，按 YAML 内容填字段：
- `card_1.html` → meta + cover 字段
- `card_2.html` → overview 字段
- `card_3.html ~ card_7.html` → sections[0..4] 字段
- `card_8.html` → sections[5] + output_trio + closing 字段

**注意**：如使用 examples/ 这种嵌套子目录，CSS 路径要写对（默认是 `../../html/base.css`；examples/pi 应是 `../../../html/base.css`）

### 4. 改 config.json
- `openid` — 收件人 QQ bot openid
- `cover_text` — 公众号首图说明
- `captions` — 8 段配文数组（必须 8 项）

### 5. 渲染 + 推送
```bash
python3 scripts/render.py       # → images/card_*.png (2160×2880 PNG, ~5s/张)
node    scripts/send_qq.mjs     # → QQ bot 推送（先用 --dry-run? 暂未实现）
```

## ⚠️ 注意事项

1. **Playwright 依赖**：沙箱已装 `playwright` + `chromium`；本地跑要先 `pip install playwright && playwright install chromium`

2. **send_qq.mjs 必须用底层 API**：`openclaw message send --media` 在 QQ bot 上 messageId 为空 = 没真发，必须 `import` `/usr/lib/node_modules/openclaw-qqbot/dist/src/api.js`

3. **嵌套目录的 CSS 路径**：examples/ 这种比模板多 1 层目录的子实例，CSS href 要 `../../../html/base.css`（不是 `../../html/base.css`，少写一层会让 CSS 加载失败 — **已踩坑，2026-08-07**）

4. **截断问题严格遵守**：任何新 prompt 要遵循"分段 + 校验 + 重试"，不要让模型一次输出整图描述

5. **section 数量固定 6**：模板假设图里有 6 个独立区块。如果原图只有 4 个区块，把最后 2 张合成"输出三件套"；7+ 个区块合并相邻章节

## 渲染产物示例

### OCR Review（架构图数据源）
- 8 张 2160×2880 retina PNG
- 单张 ~290KB（< 1MB，公众号正文图可直接发）
- 渲染耗时 ~5s/张

### pi（README+AGENTS 数据源）
- 8 张 2160×2880 retina PNG
- 单张 ~280KB
- 渲染耗时 ~5s/张

两个实例都已跑通 → 模板对两种数据源都验证 ✓。

## 复用沉淀（v1 · 2026-08-07）

- v1: 首次沉淀。OCR Review 实例验证（架构图 OCR 提取） + pi 验证（README+AGENTS 文档提取）
- 沉淀人: OpenClaw main agent
- 沉淀位置: `wechat_helper/greenbook-creator/templates/architecture-ocr-greenbook/`
- 后续主题: 只需填 YAML + 改 HTML 卡内容，无需重写 CSS