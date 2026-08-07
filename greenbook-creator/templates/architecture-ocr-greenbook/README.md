# architecture-ocr-greenbook · 架构图拆解（1080×1440 × 8P）

> **核心创新**：分节提取协议 — 不让 LLM 一次描述整张图，**枚举区块 → 逐块结构化提取 → 校验缺失字段再补**，永不截断。
> **设计哲学**：工程蓝图风 · 6 节章节卡 · 内容垂直居中 · 底部留白有底。
> **数据源**：架构图 OCR / README + AGENTS.md / 两者混合 — 同一套 8 卡模板全部消化。

---

## 📐 蓝图 / 结构化美学 · 触发词 / 何时用

> **一句话**：工程冷灰风 + 强色块章节卡，拆架构图/文档的专用模板，分节提取协议永不截断。用户说「用蓝图」「结构化美学」「拆架构图」即触发本模板。

| 场景 | 该不该用 architecture-ocr-greenbook |
|---|---|
| 你要拆 **架构图 / 流程图**（PNG/JPG OCR 提取） | ✅ **用本模板** |
| 你要拆 **README + AGENTS.md**（长文档提取） | ✅ **用本模板** |
| 之前 LLM 拆架构图**在「≥50 lines」处被截断** | ✅ **用本模板**（根因解药） |
| 你想要 **工程蓝图风**（冷灰底 + 黑色硬阴影 + 章节色块） | ✅ **用本模板** |
| 你要拆 GitHub 项目但只要 **8P 卡通风** | ❌ 改用 `tie-tu-hao-monkey-notes` |
| 你想 **手写 HTML 不想要分节协议** | ❌ 改用 `qm-greenbook`（精简版） |
| 你只要 **6 页** Pillow 出图 | ❌ 改用 `repo-overview` |

**触发关键词**（用户在 QQ/微信说这些词时自动匹配本模板）：
- **「蓝图」「蓝图风」「结构化美学」「工程蓝图」**（昵称触发）
- 「拆架构图」「拆流程图」「OCR 这张架构图」「把架构图做成小绿书」
- 「拆 README」「拆 AGENTS.md」「拆项目文档」「拆长文」
- 「工程蓝图风」「冷灰底」「分节提取协议」「不截断」「永不截断」
- 「OCR Review 风格」「earendil-works/pi 风格」「6 节章节卡」

---

## 🚀 一句话复用（3 行）

```bash
cp -r templates/architecture-ocr-greenbook <新主题>-greenbook
cp data/ocr-review.yaml data/<新主题>.yaml && # 按 prompts/section-enumerate.md 改 YAML
python3 <新主题>-greenbook/scripts/render.py && node <新主题>-greenbook/scripts/send_qq.mjs
```

---

## 🚀 快速上手（3 步）

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ① 复制模板骨架                                              │
│     cp -r architecture-ocr-greenbook <新主题>-greenbook      │
│     cd <新主题>-greenbook && rm -rf images/*                 │
│                                                              │
│  ② 跑分节提取协议（生成 data/<topic>.yaml）                  │
│     Stage 1 · 视觉枚举  → prompts/section-enumerate.md       │
│     Stage 2 · 逐块提取  → prompts/section-extract.md         │
│     Stage 3 · 校验字段  → 缺哪个只重跑那段                  │
│                                                              │
│  ③ 渲染推送                                                  │
│     python3 scripts/render.py    # → images/card_*.png       │
│     node    scripts/send_qq.mjs  # → QQ bot                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

> **3 步完事。YAML 是唯一需要改的数据源；HTML 是骨架；CSS 永远不动。**

---

## 为什么这个模板存在

拆解一张架构图时最常见的坑：让 LLM「用自由文本描述整张图」→ 单次输出超 token 限制 → **在某个句子中间嘎断**（最经典症状：「≥50 lines」）。截断是**静默**的 — 你不知道丢了什么段落，丢的内容要不要紧。想修只能重跑整张图。

**这套模板的做法：把"整段描述"切成"逐区块独立提取"**。

| 旧做法（坏） | 新做法（好） |
|--------------|--------------|
| "Describe this architecture diagram in detail" | Stage 1 → Stage 2 → Stage 3 → Stage 4 |
| 单次 ~2000 tokens，超模型限制后嘎断 | 每段 ≤ 300 tokens，6 段总和 ≤ 1800 |
| 截断是静默的 — 不知道丢了什么 | 校验 `count == expected`，缺了就重跑 |
| 整张图必须重跑才能修 | 只重跑缺失 section |

**实测**：OCR Review 原图描述在「≥50 lines」处被截断（约第 4 节中段）。本模板 6 个 section 字段全部完整 ✓。

---

## 模板结构

```
templates/architecture-ocr-greenbook/
├── README.md                  # 本文件
├── _schema.yaml               # 数据 schema + 字段约束
├── html/
│   ├── base.css               # 工程蓝图风（1080×1440 通用样式，flex 垂直居中）
│   ├── card_template_1.html ~ card_template_8.html   # 8 张空白骨架
│   ├── card_1.html ~ card_8.html                     # OCR Review 填好的实例
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
├── images/                    # 渲染产物（2160×2880 retina PNG）
└── examples/
    └── pi/                    # 第二实例：earendil-works/pi 验证用
```

---

## 八页固定结构

| 页 | 主题 | 数据字段 | 视觉要素 |
|---|---|---|---|
| 1 | 封面 | `meta` + `cover` | 中央节点 + 4 侧节点 + 3-4 chip + 收束条 |
| 2 | 全局视角 | `overview` | 流水线（5-6 节点）+ Key Path + 6 节 deck |
| 3-8 | 章节卡 × 6 | `sections[0..5]` | 章节色卡 + bullets + sub-blocks（颜色循环 green→blue→purple→orange→red→cyan） |
| 8 末尾 | 输出三件套 | `output_trio` + `closing` | 3 件套 trio + 收束条 |

**关键**：6 个 section 是固定的，对应 P3-P8。原图有多少个视觉区块，模板就拆多少 section。如果图只有 5 个区块，把最后一张合成"输出三件套"；如果有 7+ 个，合并相邻章节。

---

## 8 卡中第 8 张的特殊设计 · 「使用三件套」

P8 是「**使用方法卡**」——讲分节提取协议 + 3 步使用，而不是讲被拆解项目的输出。这样整套 8 张图天然包含「教会读者怎么复用本模板」的能力。

P8 结构（两个实例都是）：
```
[标题] 使用三件套 · 3 步拆任意架构图
[章节卡 · cyan]  分节提取协议 · 截断根因解药
                 · Stage 1 · 枚举所有视觉区块（≤12 项 JSON）
                 · Stage 2 · 逐区块独立提取（每段 ≤300 tokens）
                 · Stage 3 · 校验字段长度 / 数量，缺哪个只重跑那段
                 · Stage 4 · 合并为 YAML 数据文件
[trio]  ① 复制模板 / ② 跑协议 / ③ 渲染推送
[closing] 分节提取协议 · 无截断 · 可重试
```

---

## 两种数据源都支持

模板的设计是**数据源无关**的 — 只关心「图/文档里有几个独立区块，每个区块有什么字段」，不关心来源。

**数据源 A：架构图 OCR（OCR Review 实例）**
- 输入：架构图 PNG/JPG
- 提取协议：Stage 1 视觉识别 + Stage 2 结构化提取
- 适用：技术博客、架构分享、白皮书里的图

**数据源 B：README + AGENTS.md（pi 验证实例）**
- 输入：项目 README + AGENTS.md 文本
- 提取协议：Stage 1 按章节切分（标题/列表/代码块）+ Stage 2 抽取要点
- 适用：GitHub 项目架构文档

两种数据源走同一个 `_schema.yaml`，同一套 8 卡 HTML，同一个 `_lib/render.py` 渲染。

---

## 数据 schema 摘要

```yaml
meta:        { name, kicker, stars_text, version, source, source_date, source_kind }
cover:       { tagline_left, tagline_right, subline, central_node_*, side_nodes[4] }
overview:    { title, description, flow_steps[5-6], key_path }
sections:    [{ section_index, title_en, title_zh, color, bullets[3-5],
                details, sub_blocks[0-6] }, ...]    # 必填 6 项
output_trio: [{ label, sub, color }, ...]          # 必填 3 项
closing:     { one_liner, protocol_note }
footer_label: "项目名 · 2026.08"
```

完整 schema 见 `_schema.yaml`。

---

## 复用流程（5 步详细版）

### 1. 复制模板骨架
```bash
cp -r ~/.openclaw/workspace/wechat_helper/greenbook-creator/templates/architecture-ocr-greenbook \
      ~/.openclaw/workspace/<你的主题>-greenbook
cd <你的主题>-greenbook
rm -rf images/*         # 清空旧渲染
```

### 2. 用分节提取协议生成 YAML
```bash
# Stage 1: 枚举图中区块
#   把图片丢给 vision LLM（gpt-4v / Claude / Gemini 任意），用 prompts/section-enumerate.md
#   输出 ~12 项 JSON 数组

# Stage 2: 逐区块独立提取
#   对每项 JSON 单独调用 LLM，用 prompts/section-extract.md
#   每段输出 100-300 tokens，永远不会被截断

# Stage 3: 校验（人工目测 或 脚本自动）
#   - 每段 bullets 3-5 条
#   - 每段 details 10-30 字
#   - 每段 title_zh 4-12 字
#   缺哪个字段就只重跑那段

# Stage 4: 写到 YAML
#   对照 _schema.yaml，把校验通过的 JSON 段合并成 data/<topic>.yaml
```

### 3. 改 8 张卡 HTML
编辑 `html/card_*.html`，按 YAML 内容填字段。**注意**：如使用 examples/ 这种嵌套子目录，CSS 路径要写对（默认 `../../html/base.css`；examples/pi 应是 `../../../html/base.css`）

### 4. 改 config.json
- `openid` — 收件人 QQ bot openid
- `cover_text` — 公众号首图说明
- `captions` — 8 段配文数组（必须 8 项）

### 5. 渲染 + 推送
```bash
python3 scripts/render.py       # → images/card_*.png (2160×2880 PNG, ~5s/张)
node    scripts/send_qq.mjs     # → QQ bot 推送
```

---

## 注意事项

1. **Playwright 依赖**：沙箱已装 `playwright` + `chromium`；本地跑要先 `pip install playwright && playwright install chromium`

2. **send_qq.mjs 必须用底层 API**：`openclaw message send --media` 在 QQ bot 上 messageId 为空 = 没真发，必须 `import` `/usr/lib/node_modules/openclaw-qqbot/dist/src/api.js`

3. **嵌套目录的 CSS 路径**：examples/ 这种比模板多 1 层目录的子实例，CSS href 要 `../../../html/base.css`（不是 `../../html/base.css`，少写一层会让 CSS 加载失败 — **已踩坑，2026-08-07**）

4. **截断问题严格遵守**：任何新 prompt 要遵循"分段 + 校验 + 重试"，不要让模型一次输出整图描述

5. **section 数量固定 6**：模板假设图里有 6 个独立区块。如果原图只有 4 个区块，把最后 2 张合成"输出三件套"；7+ 个区块合并相邻章节

6. **垂直居中**：base.css 的 `.card` 用 flex + center 让内容垂直居中，留白上下平衡；P3/P5 这种内容少的章节卡上下等量留白（不要试图把它们贴顶，那会破坏节奏）

---

## 渲染产物示例

- **OCR Review**（架构图 OCR 数据源）— 8 张 2160×2880 retina PNG，~290KB/张
- **pi**（README+AGENTS 数据源）— 8 张 2160×2880 retina PNG，~280KB/张
- 渲染耗时 ~5s/张
- 两个实例都已跑通 → 模板对两种数据源都验证 ✓

---

## 复用沉淀（v1 → v2 · 2026-08-07）

**v1**: 首次沉淀。OCR Review 实例验证（架构图 OCR 提取） + pi 验证（README+AGENTS 文档提取）

**v2 · 排版优化（用户反馈后）**：
- `.card` 加 `display: flex; flex-direction: column; justify-content: center` 垂直居中
- padding 从 56px 减到 32px，整体留白更平衡
- P8 改造为「使用三件套」卡（讲分节提取协议 + 3 步使用）—— 替换内容即可复用
- README 加居中的"快速上手（3 步）"块，去掉冗余空白行

- 沉淀人: OpenClaw main agent
- 沉淀位置: `wechat_helper/greenbook-creator/templates/architecture-ocr-greenbook/`
- 后续主题: 只需填 YAML + 改 HTML 卡内容，无需重写 CSS