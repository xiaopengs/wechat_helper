# color-block-greenbook · 色块模板（1080×1440 × N 页）

> **设计哲学**:米黄底 + 复古网格 + 黑黄强调 + 色块标签 + 硬阴影描边。「清单式选型 / 盘点 / 对比」类内容的默认模板。
> **素材源**:由公众号「问一问·小克碎碎谈」《推荐 10 个 Codex 国产平替》系列 10 页视觉风格沉淀而来。
> **首次沉淀项目**:Codex 国产平替 10 选（10 页完整示例已填好）。

---

## 🟨 色块 · 触发词 / 何时用

> **一句话**：复古米黄底 + 黑黄强调色的「色块清单」风，适合选型盘点 / 工具对比 / 清单类内容。用户说「色块模板」「色块风」「米黄复古风」即触发本模板。

| 场景 | 该不该用 color-block-greenbook |
|---|---|
| 你要做 **选型清单 / 工具盘点 / 对比表**（10 选、5 款、Top N） | ✅ **用色块模板** |
| 你要「推荐 / 平替 / 怎么选」类内容，页数灵活（5-12 页） | ✅ **用色块模板** |
| 你要米黄 + 黑黄强调 + 复古网格的编辑感 | ✅ **用色块模板** |
| 你要拆 GitHub 项目（封面/WHAT/ARCH/FEATURES/VS...） | ❌ 改用 `qm-greenbook` / `tie-tu-hao-monkey-notes` |
| 你要拆架构图 / 流程图，担心 LLM 截断 | ❌ 改用 `architecture-ocr-greenbook` |
| 你要 6 页 Pillow 数据风 | ❌ 改用 `repo-overview` |

**触发关键词**（用户在 QQ/微信说这些词时自动匹配本模板）：
- **「色块」「色块模板」「色块风」「米黄复古」「复古网格」**（昵称触发）
- 「做一套选型图」「10 个平替」「国产工具盘点」「怎么选」
- 「小克碎碎谈那种风格」（素材来源昵称）

---

## 🚀 一句话复用（3 行）

```bash
cp -r templates/color-block-greenbook <新主题>-greenbook
sed -i 's/Codex 国产平替/<新主题>/g' <新主题>-greenbook/html/card_*.html
python3 <新主题>-greenbook/scripts/render.py && node <新主题>-greenbook/scripts/send_qq.mjs
```

---

## 模板结构

```
color-block-greenbook/
├── config.json          # openid / cover_text / captions（配文数组）
├── html/
│   ├── base.css         # 设计系统：米黄底 + 网格 + 黑黄强调 + 全部组件 class
│   └── card_1~10.html   # 10 张示例卡（Codex 国产平替），复制改内容即可
├── scripts/
│   ├── render.py        # thin wrapper → templates/_lib/render.py
│   └── send_qq.mjs      # thin wrapper → templates/_lib/send_qq.mjs
└── images/              # render.py 输出 card_N.png（2160×2880 retina）
```

## 设计系统速查（base.css :root 可改）

| 变量 | 值 | 用途 |
|---|---|---|
| `--bg` | `#F8F4E9` | 米黄底 |
| `--grid` | `#E7DFC8` | 复古网格线 |
| `--ink` | `#1A1A1A` | 近黑文字 |
| `--yellow` | `#EBCB64` | 强调黄（标签/色块/高亮） |
| `--yellow-d` | `#D9B23C` | 深黄（结论框左边条） |
| `--ylight` | `#F6ECC9` | 浅黄高亮 |
| `--red` | `#C93A2B` | 警示红（金句） |
| `--green` | `#6FA85B` | 勾选绿 |

**组件 class 速查**：
- `.label-tag` + `.page-num` — 顶部分类标签 + 页码
- `.title` + `.hl` / `.hl-yellow` — 大标题 + 高亮词
- `.intro` — 引言段（黑框硬阴影）
- `.tag-grid` + `.tag` — 色块标签（10 色：yellow/sand/green/teal/blue/purple/pink/orange/red/gray）
- `.block` + `.block-*` — 色块卡片（黄色/浅黄/白/绿/青/蓝/紫/粉/橙/沙/黑）
- `.tool-box` + `.t-*` — 工具盒（顶条色带 + 工具名 + 公司 chip + 描述）
- `.pair-row` — 工具 → 公司 对照行
- `.check-list` + `.check-item` — 勾选清单
- `.num-item` + `.num-badge` — 编号要点
- `.conclusion` + `.accent` — 结论框
- `.quote` — 金句框（红字强调）
- `.pick-row` + `.pick-chip` — 选择建议表
- `.deco-*` — 右上角黄色几何装饰（三角/黑条/红圆）

## 5 步详细复用流程

### 1. 复制骨架
```bash
cp -r ~/.openclaw/workspace/wechat_helper/greenbook-creator/templates/color-block-greenbook \
      ~/.openclaw/workspace/<your-topic>-greenbook/
cd ~/.openclaw/workspace/<your-topic>-greenbook
rm -rf images/*    # 清空旧图
```

### 2. 改 config.json（必改 2 处）
```json
{
  "openid": "你的 QQ openid",
  "cover_text": "封面引导文",
  "captions": ["P1 配文", ..., "PN 配文"]  // 数量必须和 card_N.html 一致
}
```

### 3. 改卡 HTML（card_1.html ~ card_N.html）
直接编辑 `html/card_*.html`：
- 改 `.label-tag` 分类标签 + `.page-num` 页码（**页码要同步改成 N/总页数**）
- 改 `.title` 标题 + `.subtitle` / `.intro`
- 内容区按信息类型选组件：清单→`tag-grid`、痛点→`grid-2x2`+`block`、公司→`pair-row`、工具→`tool-box`、场景→`check-list`、要点→`num-item`、建议→`pick-row`、金句→`quote`
- 结尾统一用 `.conclusion` 结论框
- 页数增减：加页就复制 card_N.html 改内容，删页直接删文件（render.py 自动按 card_*.html 数量渲染）

### 4. 渲染
```bash
python3 scripts/render.py    # → images/card_1~N.png（1080×1440 retina 2160×2880）
```

### 5. 发送
```bash
node scripts/send_qq.mjs              # 全发
node scripts/send_qq.mjs --only 3     # 只重发第 3 张
```

## 10 页示例结构（Codex 国产平替 · 可作选型类内容的标准骨架）

| 页 | 章节 | 组件 | 信息类型 |
|---|---|---|---|
| 01 | 封面 | title + intro + tag-grid | 10 个候选清单 |
| 02 | 痛点 | grid-2x2 + block | 为什么需要（4 件事） |
| 03 | 背景 | pair-row ×10 | 分别是谁家的 |
| 04 | 编程主力 | tool-box ×3 | 主推候选 |
| 05 | 日常提效 | tool-box ×2 + conclusion | 补充候选 |
| 06 | 办公 Agent | tool-box ×2 + check-list | 场景类候选 |
| 07 | 平台型 Agent | tool-box ×2 + block | 平台类候选 |
| 08 | 对照 | num-item ×5 | 特例深讲（QClaw=OpenClaw） |
| 09 | 选择建议 | pick-row ×5 | 按场景选型表 |
| 10 | 最后提醒 | check-list + quote | 收尾金句 |

## 注意事项

- **页码必须手改**：`<div class="page-num"><strong>02</strong> / 10</div>` 的 `/10` 要跟随总页数
- **复制到 output/ 后必须改 wrapper 绝对路径**（2026-08-14 踩坑）：`templates/` 里的 `scripts/render.py` / `send_qq.mjs` 用相对路径找 `_lib/`，模板内能跑；但 `cp -r` 到 workspace 根或 `output/` 下后 `parent.parent.parent` 指向错位 → 报 `can't open file .../_lib/render.py`。**复制后把两个 wrapper 改成指向 `templates/_lib/` 的绝对路径**（参照 output/dsh-greenbook 的写法）
- **字体**：Noto Sans SC + JetBrains Mono（Google Fonts），首次渲染需联网；沙箱限速时可能白字，可本地化
- **对比模板**：qm-greenbook 是白底圆角卡通风（多色块），色块模板是米黄底复古网格风（黑黄强调）——两者组件 class 不通用，别混用
- **配文与图的关系**：图给清单/结构/对比，配文给解读/钩子/引导，不要重复
