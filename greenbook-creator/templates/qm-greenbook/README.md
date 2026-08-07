# qm-greenbook · 通用 8P 精简骨架（1080×1440 × 8P）

> **定位**：规格 3 HTML/Playwright 8 张信息图的**最简骨架**——8 张已填好的示例卡片 + base.css + scripts/wrapper + config.json，**没有 data/YAML 也没有 prompts/**。
> **设计哲学**：极简 · 改 HTML 就完事 · 适合「想自己掌控每一处内容」的人。
> **素材源**：从 tie-tu-hao-monkey-notes 拆分出来的精简版（卡通信息图风格一致，但去掉 LLM 工作流）。
> **首次沉淀项目**：Superset（AI Coding Agents 编排型 IDE）。

---

## 🌿 小清新 · 触发词 / 何时用

> **一句话**：同款卡通视觉的精简版，手写 HTML 最快上手，无 YAML。用户说「用小清新」「小清新风格」「精简版」即触发本模板。

| 场景 | 该不该用 qm-greenbook |
|---|---|
| 你要**自己手写** 8 张卡片内容（HTML 一行行改），不想配 data YAML | ✅ **用 qm-greenbook** |
| 你要**让 LLM 自动生成**配文（喂 README/AGENTS.md 就出图） | ❌ 改用 `tie-tu-hao-monkey-notes` |
| 你要拆**架构图 / 流程图**或担心 LLM 输出截断 | ❌ 改用 `architecture-ocr-greenbook` |
| 你只要 **6 页**精简版（Pillow 出图） | ❌ 改用 `repo-overview` |
| 你要**马上跑通**，不要配任何东西 | ✅ **用 qm-greenbook**（这是最快的入门） |

**触发关键词**（用户在 QQ/微信说这些词时自动匹配本模板）：
- **「小清新」「小清新风格」「精简版」**（昵称触发）
- 「做 8 张小绿书」「做一套信息图」「做轮播图」+ **要快速上手 / 手写内容 / 不要 LLM**
- 「qm 风格」「最简单的小绿书」
- 「把 X 项目做成 8 张图」+ **不要 YAML 流程**

---

## 🚀 一句话复用（3 行）

```bash
cp -r templates/qm-greenbook <新主题>-greenbook
sed -i 's/Superset/<新主题>/g' <新主题>-greenbook/config.json <新主题>-greenbook/html/card_*.html
python3 <新主题>-greenbook/scripts/render.py && node <新主题>-greenbook/scripts/send_qq.mjs
```

---

## 📋 5 步详细复用流程

### 1. 复制骨架
```bash
cp -r ~/.openclaw/workspace/wechat_helper/greenbook-creator/templates/qm-greenbook \
      ~/.openclaw/workspace/<your-topic>-greenbook/
cd ~/.openclaw/workspace/<your-topic>-greenbook
rm -rf images/*    # 清空旧图
```

### 2. 改 config.json（必改 3 处）
```json
{
  "openid": "你的 QQ openid（不是 Superset 的）",
  "cover_text": "封面引导文（≤50 字）",
  "captions": ["P1 配文", "P2 配文", ..., "P8 配文"]  // 必须 8 项
}
```

### 3. 改 8 张卡 HTML（card_1.html ~ card_8.html）
直接编辑 `html/card_*.html`，**不需要 data YAML**。Superset 示例内容：
- 卡片 1（封面）：产品定位 + 核心数据 + 多色块并列
- 卡片 2（WHAT IT DOES）：5 步工作流节点 + 药丸连接
- 卡片 3（RUNTIME ARCHITECTURE）：三层架构图
- 卡片 4（KEY FEATURES）：5 大特性色块
- 卡片 5（VS OTHERS）：对比表
- 卡片 6（INSTALLATION）：5 步上手 + 代码色块
- 卡片 7（USE CASES）：适用 vs 不适用
- 卡片 8（GOTCHAS）：6 条避坑

### 4. 改主题色（可选）
编辑 `html/base.css` 的 `:root` 变量，全局生效。

### 5. 渲染 + 推送
```bash
python3 scripts/render.py    # → images/card_*.png (2160×2880 PNG)
node    scripts/send_qq.mjs  # → QQ bot 推送（OPENID 从 config.json 读）
```

只重发某一张：`node scripts/send_qq.mjs --only N`

---

## 模板结构

```
templates/qm-greenbook/
├── README.md                  # 本文件
├── html/
│   ├── base.css               # 卡通信息图风（粉/黄/绿/蓝/紫/橙）
│   └── card_1.html ~ card_8.html    # 8 张已填好的示例（Superset 拆解实例）
├── scripts/
│   ├── render.py              # thin wrapper → ../_lib/render.py
│   └── send_qq.mjs            # thin wrapper → ../_lib/send_qq.mjs
├── config.json                # ✅ openid + cover_text + captions
└── images/                    # 渲染产物（2160×2880 PNG）
```

> **对比 tie-tu-hao-monkey-notes**：本模板**没有** `data/superset.yaml` 和 `prompts/`，所有内容都在 `html/card_*.html` 里写死。想用 LLM 自动生成配文的请去 tthm。

---

## 🎨 设计要点（卡通信息图风）

| 元素 | 风格 |
|---|---|
| 底色 | 纯白 `#FFFFFF` + 极淡网格 40px |
| 角色块 | 圆角 24px + 4px 黑色描边 + 8px 偏移硬阴影 |
| 主标题 | 86px / 68px 粗体中文（Noto Sans SC 900） |
| 等宽小字 | 22px JetBrains Mono |
| 装饰 | 右下 / 左下 480×480 弧形大色块，30% 透明 |
| 水印 | 右下角「贴图号 · 品牌名」灰色 22px |

**配色变量**（`html/base.css :root`）：
```css
--pink: #FFB6C1;  --yellow: #FFE066;  --green: #B4E876;
--blue: #6FD8E5;  --purple: #C8A8E9;  --orange: #FF9966;
--ink: #111;  --ink-2: #555;  --ink-3: #999;
```

---

## 🧩 CSS class 速查

### 容器
- `.card` — 1080×1440 内容容器，padding 64px 72px

### Header
- `.header` / `.label-tag` (`.pink|.green|.blue|.purple|.orange`) / `.page-num`

### Chip / 标题
- `.chip` (6 色前缀) / `.title` (86px) / `.title-sm` (68px) / `.title .hl`（黄底高亮）

### 色块 / Banner
- `.block` + `.block-pink|.block-yellow|.block-green|.block-blue|.block-purple|.block-orange|.block-white`
- `.block-title` (32px Mono) / `.block-sub` (22px 描述)

### 数据展示
- `.grid-3` / `.grid-4` / `.grid-5` / `.row` / `.col`
- `.compare-cell` (`.check` / `.cross` / `.warn`)

### 流程连接 / 警告 / 代码
- `.arrow-down` / `.pill` / `.warn-row` / `.code`（深灰底 + 等宽）

### 页脚
- `.footer` / `.watermark` + `.watermark-icon`

---

## ⚠️ 注意事项

1. **Playwright 依赖**：沙箱已装 `playwright + chromium`，本地跑要先 `pip install playwright && playwright install chromium`

2. **send_qq.mjs 必须用底层 API**：`openclaw message send --media` 返回的 `Message ID` 为空字符串 = 没真发。
   直接 `import` `/usr/lib/node_modules/openclaw-qqbot/dist/src/api.js` 调 `sendC2CImageMessage`

3. **图片大小**：1080×1440 → 2160×2880 PNG ≈ 300KB，每张 < 1MB，公众号正文图可直接发

4. **小绿书尺寸**：发「贴图/海报」用 3:4 比例正好

5. **网页字体**：沙箱加载 Google Fonts 偶发限速，首屏白字可改本地字体（详见 tie-tu-hao-monkey-notes/README 注意事项）

---

## 已知约束

- **qm-greenbook 没有 data YAML**——所有内容写死在 HTML 里，改起来没 tthm 那么结构化
- 适合「一次性出图、不需要 LLM 重复生成」的场景
- **要 LLM 自动化**请去 `tie-tu-hao-monkey-notes`

---

## 复用沉淀（v2 · 2026-08-07）

- **v1**（2026-07-30）：首次沉淀，Superset 拆解实例 + base.css + 8 张 card
- **v2**（2026-08-07）：
  - 修正 README（之前错误地标为 tthm 内容）
  - 加「触发词 / 何时用」决策表
  - 加「一句话复用」3 行命令
  - 明确「无 data YAML、无 prompts/」定位，与 tthm 区分

- 沉淀人：OpenClaw main agent
- 沉淀位置：`wechat_helper/greenbook-creator/templates/qm-greenbook/`
- 后续主题：直接改 `html/card_*.html` + `config.json`，无需重写 CSS