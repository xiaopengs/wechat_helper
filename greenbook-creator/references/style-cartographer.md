# 知识图解 (Cartographer) 设计系统

> 米黄 + 黑 + 黄的 editorial 编辑感。**适用 6-12 页长图文知识图解**（区别于 ≤6 页小绿书图文消息）

## 适用场景 vs 不适用

| ✅ 适合 | ❌ 不适合 |
|--------|----------|
| 12 页技术拆解（OpenRouter × Coding Agents 案例） | 朋友圈单图海报 |
| 概念地图 / 信息清单 / 步骤教程 | ≤6 页短图文消息（用 default 即可） |
| 公众号长文配图 | 表情包、梗图、卡通 |
| 「一张图讲清一件事」的精确排版 | 抽象艺术、插画、3D 渲染 |

## 色板（黑白黄三色系统）

| Token | 值 | 用途 |
|-------|----|----|
| `--bg-cream` | `#FCF6E0` | 主底色（米黄） |
| `--bg-black` | `#1A1A1A` | 反白块、强调块、code 块 |
| `--bg-yellow` | `#FFD700` | 强调色（数字、icon、tag） |
| `--text-white` | `#FFFFFF` | 黑底上的白字 |
| `--text-black` | `#1A1A1A` | 主文字 |
| `--text-muted` | `rgba(26,26,26,0.55)` | 次要文字 |
| `--text-muted-inv` | `rgba(255,255,255,0.55)` | 黑底上的次要文字 |
| `--divider` | `rgba(26,26,26,0.12)` | 浅色分割线 |

**绝对不用**：渐变、阴影、圆角超过 4px、玻璃拟态、emoji 装饰

## 排版尺度（3:4 = 1080×1440）

```css
/* 标题层级 - 比 default 上调 20-30% 补足 3:4 短高度 */
.h1  { font-size: 92px; font-weight: 900; line-height: 1.05; }
.h2  { font-size: 56px; font-weight: 900; line-height: 1.10; }
.h3  { font-size: 36px; font-weight: 700; line-height: 1.20; }

/* 正文 */
.lead { font-size: 32px; line-height: 1.40; font-weight: 500; }
.body { font-size: 24px; line-height: 1.45; font-weight: 400; }
.body-sm { font-size: 20px; line-height: 1.40; color: var(--text-muted); }

/* 代码 */
.code { font-size: 18px; line-height: 1.55; padding: 18px 22px; }

/* 数字 - 必须大！ */
.big-num { font-size: 120px; font-weight: 900; }
.step-num { font-size: 72px; font-weight: 900; }
.tier-num { font-size: 80px; font-weight: 900; }
.hero-title { font-size: 104px; font-weight: 900; line-height: 1.02; }

/* slide 容器 */
.slide {
  width: 1080px;
  height: 1440px;
  padding: 60px 60px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
```

## 布局模式

### 1. 封面 / 金句页（hero）
```html
<section class="slide slide--black slide--hero">
  <div class="content">
    <div class="kicker">KNOWLEDGE · 12 PAGES · 3:4</div>
    <div class="cat-label">第 01 章 · 引子</div>
  </div>
  <div class="hero-center">
    <div class="hero-accent"></div>          <!-- 左侧 8px 黄色竖条 -->
    <div class="hero-bg-num">300+</div>       <!-- 半透明大背景数字 -->
    <h1 class="hero-title">一把 Key<br />接住 300+ 模型</h1>
    <p class="hero-sub">副标题说明</p>
  </div>
  <div class="content" style="display:flex; justify-content:space-between;">
    <div class="foot">@knowledge-cartographer</div>
    <div class="foot">01 / 12</div>
  </div>
</section>
```

### 2. 内容页（content--spread 关键）
```html
<section class="slide">
  <div class="watermark">PAIN</div>          <!-- 右上角半透明大水印 -->
  <div class="content content--spread">       <!-- 关键 class -->
    <div>
      <div class="kicker">第 02 章 · 痛点</div>
      <h2 class="h2">标题</h2>
      <p class="lead">引文</p>
    </div>
    <div class="stack-lg">                   <!-- 内部 space-between 自填满 -->
      <div class="block-black">...</div>
      <div class="block-black">...</div>
      <div class="block-black">...</div>
    </div>
  </div>
  <div class="page-num">02 / 12</div>
</section>
```

**`content--spread` 的关键 CSS**（让 3-4 个 block 自动均分到全屏）：
```css
.content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
}
.content--spread > .stack,
.content--spread > .stack-lg,
.content--spread > .stack-xl {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
```

### 3. Q&A 块（FAQ 页）
```html
<div>
  <div class="qa-q">Q · 每个工具要单独 Key 吗?</div>
  <div class="qa-a">A · 不。一把 sk-or-... 全通。</div>
</div>
```
- Q 用黄底黑字，padding 14×20，font-size 24px
- A 用黑底白字，padding 14×20，font-size 20px
- QA 块之间 margin-bottom: 14px

### 4. 成本档位卡（数字对比页）
```html
<div class="tier tier-free">    <!-- 或 tier-paid / tier-fee -->
  <div class="tier-label">免费档</div>
  <div class="tier-num">$0</div>
  <p class="tier-desc">描述</p>
  <p class="body-sm">补充说明</p>
</div>
```
- `tier-free` = 黄底黑字
- `tier-paid` = 黑底白字
- `tier-fee` = 浅黄底 + 2px 黑色边框

### 5. 工具列表（多分类页）
```html
<div class="cat-label">终端 Agent</div>     <!-- 黄色 chip 标题 -->
<div class="tool-row">
  <span class="tool-name">Claude Code</span>
  <span class="tool-path">环境变量 · Anthropic 兼容端点</span>
</div>
```

### 6. 代码块
```html
<div class="code">
  <span class="code-comment"># 注释</span>
  <span class="code-key">import</span> os
  <span class="code-string">"string"</span>
</div>
```
- `code-comment` = 灰色
- `code-key` = 蓝青色
- `code-string` = 黄色（与品牌色一致）
- 不用 emoji、不要横向滚动条（提前换行）

## 视觉加强技巧

| 技巧 | 用途 | 示例 |
|------|------|------|
| 黄色大数字 | 强调"是什么" | `$0` / `0%` / `5.5%` / `300+` |
| 黄色 icon 前缀 | 强调 list 项 | `+` / `−` / `→` 黄色 56px |
| 黑底反白块 | 强调对比 | `block-black` 包裹关键信息 |
| 黄色 chip | 分类小标 | `cat-label` / `chip` |
| 半透明背景大数字 | 封面装饰 | `hero-bg-num` 380px, opacity 0.08 |
| 右上角大水印 | 章节标识 | `watermark` 140px, opacity 0.06 |

## 完整模板

参考 `references/cartographer-template/` 下的 `openrouter-cartographer/` 项目：
- `index.html` — 12 页结构示例
- `css/styles.css` — 完整样式表
- `screenshots/` — 最终 PNG 产物
- `_shoot.py` — Playwright 截图脚本

## 两种出图方式

| 方式 | 工具 | 适用 |
|------|------|------|
| **AI 生图** | `gen_media.sh generate --style cartographer` | 单页封面、概念插图，AI 强项 |
| **HTML + Playwright 截图** | 见 `cartographer-template/_shoot.py` | 12 页技术拆解，需要精确排版、可读代码块、真实数据 |

**强烈推荐长图文用 HTML+Playwright**：
- AI 生图在多页 / 多行代码 / 中文段落上会出 OOD（变体、错位、臆造数字）
- HTML 能 100% 复用 CSS 设计系统、保证视觉一致
- 截图比生图快、确定性、可批量改

### HTML 截图管线
```python
# _shoot.py 关键逻辑
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

WIDTH, HEIGHT = 1080, 1440  # 3:4

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome",
        )
        ctx = await browser.new_context(viewport={"width": WIDTH, "height": HEIGHT})
        page = await ctx.new_page()
        await page.goto(f"file://{Path('index.html').absolute()}")
        for i in range(12):
            await page.locator(".slide").nth(i).screenshot(path=f"screenshots/slide-{i+1:02d}.png")
        await browser.close()
```

**前置依赖**：
```bash
# 一次性装好
pip install playwright
playwright install chromium
# 装系统 lib（chromium 启动依赖）
sudo apt install libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libatspi2.0-0
```

## 12 页结构（标准知识图解骨架）

| 页 | 类型 | 内容 |
|----|------|------|
| 01 | Hero 封面 | 大数字 + 一句话主张 + kicker + 页码 |
| 02 | 痛点（3 cards）| 反差对比，每个 card 一个 big-num |
| 03 | 定义（4 cards）| 是/不是二分法，+ / − 黄色 icon |
| 04 | 价值（3 cards）| 一把钥匙 / 一个 URL / 一个 Slug 形式 |
| 05 | 步骤（3 steps）| step-num + h3 + code 块 |
| 06 | 代码（3 sections）| curl / Python / TypeScript 同调用 |
| 07 | 工具地图（4 cat）| cat-label + tool-row 列表 |
| 08 | 路由（3 层）| 第一层 / 第二层 / 兜底 |
| 09 | 对比（2 cards）| Client SDK vs Agent SDK |
| 10 | 成本（3 tiers）| $0 / 0% / 5.5% tier 卡片 |
| 11 | FAQ（5 Q/A）| 5 个常见坑 |
| 12 | Hero 收束 | 金句 + ∞ 背景数字 + DONE |

## 公网部署 + 微信发送

12 张图生成后，部署到静态站（参考 `1Panel` / nginx `location /static/`）：

```bash
# 1. cp 到 1Panel 部署目录
sudo cp -f screenshots/slide-*.png /home/ubuntu/1panel/www/sites/thinkspc.fun/index/<project>/screenshots/
sudo chown -R root:root /home/ubuntu/1panel/www/sites/thinkspc.fun/index/<project>/screenshots/
sudo chmod 755 /home/ubuntu/1panel/www/sites/thinkspc.fun/index/<project>/screenshots/
sudo chmod 644 /home/ubuntu/1panel/www/sites/thinkspc.fun/index/<project>/screenshots/*.png

# 2. 验 200
for n in 01 02 03 04 05 06 07 08 09 10 11 12; do
  curl -s -o /dev/null -w "slide-$n: HTTP %{http_code} | %{size_download} bytes\n" \
    "https://<domain>/static/<project>/screenshots/slide-$n.png"
done

# 3. 发到 QQ / 微信（必须用公网 URL，base64 上传会被 QQ 服务端拒）
#    详见 MEMORY.md "QQ Bot <qqimg> 发送图片踩坑" 章节
```

## 反例（什么不能用 cartographer 风格）

- ❌ 节假日祝福图（太冷峻）
- ❌ 情感类 / 治愈系内容（米黄+黑+黄太硬）
- ❌ 美食 / 旅行 / 萌宠（无匹配语义）
- ❌ 表情包 / 梗图（违和）

## 失败机制

| 失败模式 | 触发条件 | 修复 |
|---------|---------|------|
| 下半屏空 | 内容 < 1440px，flex 没填满 | 加 `content--spread` 让 stack 撑满中间 |
| 字号小看不清 | 缩略图 375px 宽 | body 至少 24px，big-num 至少 80px |
| 风格断裂 | 12 页换了不同底色/字体 | 严格用同一份 `styles.css`，禁止 inline 改 |
| 段落被截 | 1440 高度不够，content 溢出 | 调 padding（60→40）或压字距 |
| AI 生图臆造 | 用 AI 生 12 页长图 | 长图文改用 HTML+Playwright |
