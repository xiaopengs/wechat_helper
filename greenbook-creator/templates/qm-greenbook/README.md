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
│   ├── card_1.html ~ card_8.html    # 8 张完整示例:Superset 拆解实例
│   └── card_template_1.html ~ card_template_8.html  # 8 张空白骨架,复用作起点
├── scripts/
│   ├── render.py                # thin wrapper → ../_lib/render.py（参数化 Playwright 截图）
│   └── send_qq.mjs              # thin wrapper → ../_lib/send_qq.mjs（参数化 QQ bot 推送）
├── config.json                  # ✅ openid + cover_text + captions（改这个,不用动 .mjs）
└── images/
    └── card_1.png ~ card_8.png  # 渲染产物（2160×2880,2x retina）
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

## 🎨 设计要点

### 视觉语言
| 元素 | 风格 |
| --- | --- |
| 底色 | 纯白 `#FFFFFF` + 极淡网格 40px（透明度 0.6） |
| 角色块 | 圆角 24px + 4px 黑色描边 + 8px 偏移硬阴影 |
| 主标题 | 86px / 68px 粗体中文（Noto Sans SC 900）|
| 等宽小字 | 22px JetBrains Mono（标签/页码/banner 头）|
| 装饰 | 右下 / 左下 480×480 弧形大色块,30% 透明 |
| 水印 | 右下角"贴图号 · 品牌名",灰色 22px |

### 配色变量（base.css :root 可改）
```css
--pink:    #FFB6C1;   --pink-d:    #FF8FA3;
--yellow:  #FFE066;   --yellow-d:  #FFD43B;  --ylight: #FFF7C2;
--green:   #B4E876;   --green-d:   #6CC24A;
--blue:    #6FD8E5;   --blue-d:    #4FB6C8;
--purple:  #C8A8E9;   --purple-d:  #9F7AD1;
--orange:  #FF9966;   --orange-d:  #E8744A;
--red:     #FF6B6B;
--ink:     #111111;   --ink-2: #555;   --ink-3: #999;
```

> 改主题色只需替换这些变量值,不用动其他 CSS。

### 配色码（参考图取值,可继承）

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

## 🧩 CSS class 速查

### 容器
- `.card` — 1080×1440 内容容器,padding 64px 72px

### Header
- `.header` / `.label-tag` (`.pink|.green|.blue|.purple|.orange` 5 色前缀) / `.page-num`

### Chip（顶部小药丸标签）
- `.chip` (`.green|.pink|.yellow|.purple|.orange|.blue`)

### 标题
- `.title` (86px) / `.title-sm` (68px) / `.title .hl` (黄底高亮)

### 色块 / Banner
- `.block` + `.block-pink|.block-yellow|.block-green|.block-blue|.block-purple|.block-orange|.block-white`
- `.block-title` (32px Mono 900) / `.block-title-2` (28px Mono 900)
- `.block-sub` (22px 描述)
- `.banner` (白底/可换 ylight) / `.banner-label` (22px Mono)

### 数据展示
- `.grid-3` / `.grid-4` / `.grid-5` / `.row` / `.col`
- `.compare-cell` (含 `.check` 绿 ✓ / `.cross` 红 ✗ / `.warn` 橙 ⚠)
- `.compare-label` (18px 维度名)
- `.tag-chip` (18px 小药丸)

### 流程连接
- `.arrow-down` (36px 黑线 + 三角箭头)
- `.pill` (圆角 999px 节点胶囊)

### 适用 / 不适用
- `.yes-col` (绿虚线边框 + 浅绿底) / `.no-col` (红虚线边框 + 浅红底)
- `.col-head.yes|.no` (含 `.badge` 圆角色块)
- `.list-item` (虚线分隔项 + `.marker` 标记)

### 警告
- `.warn-row` (白底 + 黑描边 + 阴影) / `.warn-icon` (黄底小方块) / `.warn-text` (含 `.warn-text b` 橙色加粗关键词)

### 代码块
- `.code` (深灰 #1E1E1E 底 + 等宽)
- `.code .k` 关键字橙 / `.code .s` 字符串绿 / `.code .c` 注释灰斜体 / `.code .p` 标点青

### 页脚
- `.footer` (绝对定位底部 64px) / `.tagline` (26px 含 `.accent` 黄底高亮) / `.watermark` + `.watermark-icon` (28px 圆点)

## 🚀 复用步骤（详细版）

### 1. 复制项目骨架
```bash
cp -r ~/.openclaw/workspace/wechat_helper/greenbook-creator/templates/tie-tu-hao-monkey-notes \
      ~/.openclaw/workspace/<your-topic>-greenbook/
cd ~/.openclaw/workspace/<your-topic>-greenbook
rm -rf images/*    # 清空旧图
rm html/card_*.html  # 删示例(非 template_*),只留骨架
```

### 2. 改主题色（可选）
编辑 `html/base.css` 的 `:root` 变量,全局生效。

### 3. 改 8 张卡的内容
编辑 `html/card_template_*.html`,搜索 `TODO` 标记,逐项替换:
- `TODO · 顶部英文标签` → `PRODUCT POSITIONING` / `WHAT IT DOES` 等
- `TODO · 一句话定位主标题` → 你的核心 hook
- `TODO · 关键短语` → 高亮短语（包 `<span class="hl">`）
- 数据/对比/代码/警告内容同理

### 4. 渲染
```bash
cd scripts && python3 render.py
# 输出:../images/card_1.png ~ card_8.png (2160×2880 PNG, ~300KB/张)
```

### 5. 推送（QQ bot 场景）
```bash
# 改项目根的 config.json:openid / cover_text / captions
node scripts/send_qq.mjs
# 只重发某一张（例如第 8 张上次失败）:
node scripts/send_qq.mjs --only 8
```

## ⚠️ 注意事项

1. **Playwright 依赖**:沙箱已装 `playwright + chromium`,本地若无要先装:
   ```bash
   pip install playwright && playwright install chromium
   ```

2. **send_qq.mjs 必须用底层 API**:`openclaw message send --media` 返回的 `Message ID` 为空字符串 = 没真发。
   直接 `import` `/usr/lib/node_modules/openclaw-qqbot/dist/src/api.js` 调 `sendC2CImageMessage`。

3. **图片大小**:1080×1440 渲染 → 2160×2880 PNG ≈ 300KB,每张都 < 1MB,可直接发 QQ / 微信。

4. **小绿书尺寸**:发「贴图/海报」用 3:4 比例正好（1080×1440 → 微信 1080×1440 实际显示完美）。

5. **网页字体**:沙箱加载 Google Fonts 会偶尔失败（限速）。如果首屏白字,可改本地字体:
   ```bash
   # 下载到 html/fonts/, 改 base.css import 为相对路径
   curl -fsSL https://fonts.googleapis.com/css2?... -o html/fonts/noto.css
   ```

## 渲染产物

- 8 张 2160×2880 PNG(2x retina,1080×1440 视觉等效)
- 单张 276-371KB(均 <1MB,微信公众号正文图可直接发)
- 渲染耗时 ~5s/张

## 推送注意事项

`config.json` 里的 `openid` **必须改** —— 当前是 Superset 案例的用户 openid。
其他参数按需调整:
- `img_dir` — PNG 输出目录（默认 `images`）
- `cover_text` — 封面引导文
- `captions` — 8 段配文数组

## 已知约束

- AI 生图(tokenrouter gpt-image-2)中文渲染失败 → **必须用 HTML + Playwright**
- 沙箱已装 `playwright` (Python) + `chromium` → **直接可用,无需安装**
- Node 端无 playwright/puppeteer → **必须走 Python 端渲染**
- CLI `openclaw message send --media` 在 QQ bot 上 messageId 为空 = **没真发**,必须用底层 `import openclaw-qqbot/dist/src/api.js`

## 复用沉淀（v3 · 2026-08-02）

- **v1** (2026-07-30): 首次沉淀,Superset 拆解实例 + base.css + 8 张 card
- **v2** (2026-07-30): 重构对齐「贴图号·猴子AI笔记」风,引入弧形装饰 / drop-shadow / 等宽 Mono
- **v3** (2026-08-02): 模板化升级,新增 8 张 `card_template_*.html` 空白骨架 + 详细 README
  - 主题色集中在 `:root`,改一套换整套图风格
  - 复用流程文档化（5 步: 复制骨架 → 改配色 → 替换 TODO → 渲染 → 推送）
  - CSS class 速查 + Playwright / 字体 / send_qq 注意事项齐全

- 首次沉淀项目:Superset(AI Coding Agents 编排型 IDE)
- 沉淀人:OpenClaw main agent
- 沉淀位置:`wechat_helper/greenbook-creator/templates/tie-tu-hao-monkey-notes/`
- 后续主题:只需改 `card_template_*.html` 的 TODO + 配色变量,无需重写 CSS