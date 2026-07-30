# tie-tu-hao-monkey-notes · 贴图号·猴子AI笔记（1080×1440 × 8P）

> **设计哲学**:中文信息图 + 极淡网格底纹 + 多色块流程 + 超粗黑体标题 + 圆角药丸连接 + 弧形装饰 + 右下水印。
> **素材源**:由「贴图号·猴子AI笔记」公众号出品的视觉风格沉淀而来,适合 AI 工具 / 开源项目 / 知识科普类小绿书。
> **首次沉淀项目**:Superset(AI Coding Agents 编排型 IDE)。

## 模板结构

```
templates/tie-tu-hao-monkey-notes/
├── README.md                    # 本文件
├── html/
│   ├── base.css                 # 共享样式（色码/字号/水印/弧形装饰,3KB）
│   └── card_1.html ~ card_8.html  # 8 张内容块,只换 innerHTML
├── scripts/
│   ├── render.py                # Playwright 截图脚本（2160×2880,2x retina）
│   └── send_qq.mjs              # QQ bot 推送脚本（用底层 API,CLI 不可靠）
├── data/
│   └── superset.yaml            # ✅ Superset 示例配置（已验证可跑通）
├── prompts/
│   ├── captions.md              # P1–P8 单图配文模板
│   └── cover-text.md            # 封面引导文模板
└── images/
    └── card_1.png ~ card_8.png  # Superset 示例产物（参考效果）
```

## 八页固定结构

| 页 | 主题 | 视觉要素 |
|---|---|---|
| 1 | **封面** | 一句话定位 + 核心数据 + 多色块并列 |
| 2 | **WHAT IT DOES** | 5 步工作流（节点 + 药丸连接） |
| 3 | **RUNTIME ARCHITECTURE** | 三层架构图（多入口 → 编排 → 执行） |
| 4 | **KEY FEATURES** | 5 大特性色块卡片 |
| 5 | **VS OTHERS** | vs Cursor / 纯 CLI 等色块对比表 |
| 6 | **INSTALLATION** | 5 步上手 + 代码色块 |
| 7 | **USE CASES** | 适用 vs 不适用 漫画分镜 |
| 8 | **GOTCHAS** | 6 条避坑（彩色警示牌） |

## 怎么用（一句话）

```bash
# 1. 复制一份卡片 HTML（8 张）
cp -r html html-myproject
# 2. 编辑每张 card_N.html 的 innerHTML（标题/色块/标签条）
# 3. 渲染
python3 scripts/render.py html-myproject/ images-myproject/
# 4. 推送（改 OPENID + IMG_DIR）
node scripts/send_qq.mjs
```

## 风格规范（base.css 关键 class）

| Class | 用途 | 关键属性 |
|---|---|---|
| `.tag-bar` | 顶部浅灰标签条 | `display:flex; padding:24px;` + 圆角药丸 + 右上"NN/08"页码 |
| `.title-h1` | 超大粗体中文标题 | `font-size:84px; font-weight:900;`（可包 `<span class="hl">` 高亮） |
| `.subtitle` | 灰色小字段落 | `color:#666; font-size:28px;` |
| `.color-card` | 圆角色块 | `border-radius:32px; border:3px solid #111; box-shadow:0 6px 0 #111;` |
| `.pill-conn` | 节点间连接圆角药丸 | `background:#fff; border:2px solid #111; border-radius:999px;` |
| `.deco-arc` | 右下/左下弧形大色块 | `border-radius:50%; opacity:0.3;` |
| `.watermark` | 右下角灰色水印 | `position:absolute; bottom:36px; right:48px; color:#999;` |

## 配色码（参考图取值,可继承）

| 用途 | 颜色 | 取值 |
|---|---|---|
| 粉 | TUI 入口 | `#FFB6C1` |
| 黄 | IDE / 高亮底 | `#FFEB99` |
| 绿 | CI / 成功 | `#B4E876` |
| 深绿 | SESSION | `#6CC24A` |
| 蓝 | LEADER / 主色 | `#6FD8E5` |
| 紫 | MODEL / 思考 | `#C8A8E9` |
| 橙 | TOOLS / 警示 | `#FF9966` |
| 文字 | 主文字 | `#111` |
| 辅文 | 次要文字 | `#666` |
| 底纹 | 网格底 | `#FAFAFA` |

## 渲染产物

- 8 张 2160×2880 PNG(2x retina,1080×1440 视觉等效)
- 单张 276-371KB(均 <1MB,微信公众号正文图可直接发)
- 渲染耗时 ~5s/张

## 推送注意事项

`scripts/send_qq.mjs` 里的 `OPENID` **必须改** —— 当前是 Superset 案例的用户 openid。
其他参数按需调整:
- `IMG_DIR` — PNG 输出目录
- `COVER_TEXT` — 封面引导文
- `CAPTIONS` — 8 段配文

## 已知约束

- AI 生图(tokenrouter gpt-image-2)中文渲染失败 → **必须用 HTML + Playwright**
- 沙箱已装 `playwright` (Python) + `chromium` → **直接可用,无需安装**
- Node 端无 playwright/puppeteer → **必须走 Python 端渲染**
- CLI `openclaw message send --media` 在 QQ bot 上 messageId 为空 = **没真发**,必须用底层 `import openclaw-qqbot/dist/src/api.js`

## 复用沉淀

- 首次沉淀时间:2026-07-30(Superset 案例)
- 沉淀人:OpenClaw main agent
- 沉淀位置:`wechat_helper/greenbook-creator/templates/tie-tu-hao-monkey-notes/`
- 后续主题:只需改 8 个 card 的 innerHTML,无需重写 CSS