# Style Spec — 视觉规范细节

> **2026-06-19 更新**:从默认长图(自适应高度)改为 **3:4 (1080×1440) 优化版**,适配小红书/公众号长图文。其它画布(9:16 / 方形 / 手机长图)见 `canvas-specs.md` 校准。

## 颜色

| 角色 | 颜色 | 用途 |
|----|----|----|
| 底色 | `#FCF6E0` | 整页背景,所有页统一 |
| 黑块 | `#1A1A1A` | 强调块背景,配白字 `#FFFFFF` |
| 黄块 | `#FFD700` | 二级强调块背景,配黑字 `#1A1A1A` |
| 水印 | `#FCF6E0` 上叠 `rgba(26,26,26,0.06)` | 角落大写字母背景 |
| 分割线 | `#1A1A1A` 1-2px | 段落之间 |
| 半透明黄 | `rgba(255,215,0,0.08)` | 封面/收束页背景大数字 |

**绝对不用**:渐变、阴影、圆角超过 4px、玻璃拟态、emoji 装饰

## 字体(3:4 优化版)

- 字体族:无衬线(`-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif`)
- 全局对齐:左对齐(标题、正文、代码块注释)
- 字号表:

| 元素 | 3:4 字号 | 用途 |
|----|----|----|
| **H1 (`.h1`)** | 92px / 900 / line-height 1.05 | 一级标题(章节首屏大字) |
| **H2 (`.h2`)** | 56px / 900 / line-height 1.10 | 二级标题(每页主标题) |
| **H3 (`.h3`)** | 36px / 700 / line-height 1.20 | 三级标题(卡片小标) |
| **Lead (`.lead`)** | 32px / 500 / line-height 1.40 | 引文/导语(标题下第一句) |
| **Body (`.body`)** | 24px / 400 / line-height 1.45 | 正文(卡片内文) |
| **Body-sm (`.body-sm`)** | 20px / 400 / line-height 1.40 | 次要注释(灰色) |
| **Code (`.code`)** | 18px / 400 / line-height 1.55 | 代码块 |
| **Hero-title** | 104px / 900 / line-height 1.02 | 封面/金句页主标题 |
| **Hero-bg-num** | 380px / 900 / opacity 0.08 | 封面背景半透明大数字 |
| **Big-num** | 120px / 900 / line-height 1 | 卡内大数字($0 / 0% / 5.5%) |
| **Step-num** | 72px / 900 / line-height 1 | 步骤序号(01/02/03) |
| **Tier-num** | 80px / 900 / line-height 1 | 成本档位大数字 |
| **Kicker** | 14px / 700 / letter-spacing 6px | 顶部小字标签(全大写) |
| **Page-num** | 14px / 400 / 灰色 | 右下角页码 |
| **Watermark** | 140px / 900 / opacity 0.06 | 右上角大写水印(章节标识) |
| **Tool-name** | 26px / 700 | 工具列表工具名 |
| **Tool-path** | 18px / 400 / 灰色 | 工具列表路径(等宽字体) |
| **Cat-label** | 14px / 800 / letter-spacing 2px | 黄色分类标签 chip |

- 行宽:每行不超过 16 个汉字 / 32 个英文字符(便于扫读)
- 页边距:每页 60px(3:4 比 9:16 短高度,边距收紧 25%)

## 排版原则

- **对齐**:全部左对齐(标题、正文、代码块注释)
- **段落间距**:段落之间用 `<hr class="divider">` 分割线明确隔开,间距 18px
- **内容分布**:核心!固定 1440px 高 + `overflow: hidden`,内容用 `.content--spread` 配合 `.stack-lg` 让 block 自动均分到全屏
- **垂直密度**:从上到下标题 → 引文 → 3-4 个 block → 底部 page-num,均匀分布不留空

## 装饰元素

- **水印**(`.watermark`):页面右上角,放置章节关键词的大写英文(如 `PAIN` / `DEFINE` / `VALUE`),字号 140px,opacity 0.06
- **背景大数字**(`.hero-bg-num`):封面/收束页用,opacity 0.08,字号 380px
- **左侧黄色竖条**(`.hero-accent`):8px 宽,贯穿 hero 标题左侧,增强视觉锚点
- **页码**(`.page-num`):右下角 `第 N 页 / 共 M 页` 形式,字号 14px,灰色
- **chip 标签**(`.chip` / `.cat-label`):黄底黑字,大写,letter-spacing 1.5-3px
- **半透明大字引号块**:核心金句用整版黑底,中央放金句,底部放一句话注脚

## 代码/结构展示

- **目录树**:用 ASCII 风格,如:
  ```
  project/
  ├── src/
  │   ├── index.ts
  │   └── utils.ts
  └── README.md
  ```
- **代码块**:`<div class="code">`,配 `.code-comment`(灰色) / `.code-key`(蓝青色) / `.code-string`(黄色,品牌色一致)
- **关键字段**:用黄底块包住,黑字加粗
- **不要**横向滚动条(提前换行或缩小字号)

## 视觉加强技巧

| 技巧 | 用途 | 示例 |
|------|------|------|
| 黄色大数字 | 强调"是什么" | `$0` / `0%` / `5.5%` / `300+` |
| 黄色 icon 前缀 | 强调 list 项 | `+` / `−` / `→` 黄色 56px |
| 黑底反白块 | 强调对比 | `block-black` 包裹关键信息 |
| 黄色 chip | 分类小标 | `cat-label` / `chip` |
| 半透明背景大数字 | 封面装饰 | `hero-bg-num` 380px, opacity 0.08 |
| 右上角大水印 | 章节标识 | `watermark` 140px, opacity 0.06 |

## 不允许出现的元素

- 渐变色(破坏极简感)
- 多色搭配超过 3 种(严格黑白黄)
- 居中对齐(全部左对齐是核心约束)
- 圆角超过 4px(会显得"软")
- 阴影(扁平化)
- Emoji 作为视觉装饰(emoji 可在文案里偶尔出现,但不充当图标)
- 字体粗细变化超过 2 档(只 400 / 700 / 900)

## 落地到不同下游时如何映射

| 下游 | 怎么映射这套规范 |
|----|----|
| Gamma / Tome | 选 "Custom Theme",背景色 `#FCF6E0`,字号按本表缩 0.85×(Gamma 默认偏大) |
| Markdown→HTML | 复制 `wechat_helper/greenbook-creator/references/cartographer-template/` 改 `index.html`,保留 `css/styles.css` 不动 |
| Figma / 墨刀 | 做一个 1080×1440 的母版 frame,三个组件:Header / BodyBlock / QuoteBlock,替换文字即可 |
| Keynote / PPT | 设主题色 `#FCF6E0` 为主色,`#1A1A1A` 为强调色,所有文本左对齐 |
| **HTML + Playwright**(推荐) | 走 SKILL.md "模式 B" 流程,模板开箱即用 |

## 字号快查对照(2 种画布)

如果用户切到 9:16 (1080×1920),字号表改用 `canvas-specs.md` 第 9:16 行:
- H1 72px / H2 42px / H3 28px / Lead 24px / Body 18px / Body-sm 16px / Code 13px
- 整体下调 20-25%(因为 9:16 有更高垂直空间)

3:4 与 9:16 字号对照表:

| 元素 | 3:4 (1080×1440) | 9:16 (1080×1920) |
|----|----|----|
| H1 | 92px | 72px |
| H2 | 56px | 42px |
| H3 | 36px | 28px |
| Lead | 32px | 24px |
| Body | 24px | 18px |
| Body-sm | 20px | 16px |
| Code | 18px | 13px |
| Big-num | 120px | 96px |
| Step-num | 72px | 56px |
| Tier-num | 80px | 72px |
| Hero-title | 104px | 96px |
| Hero-bg-num | 380px | 480px |
| Slide padding | 60px | 80px |
| 行距 | 1.40-1.45 | 1.50-1.60 |