# Canvas Specs — 不同画布的适配参数

> **2026-06-19 更新**:默认改为 **3:4 (1080×1440)** — 小红书/公众号长图文原生比例,信息密度高,缩略图清晰。

## 画布速查表

| 画布 | 尺寸 | 用途 | 字号缩放系数 | 留白基准 | 推荐度 |
|----|----|----|----|----|----|
| **3:4 长图文(默认)** | **1080×1440** | **小红书/公众号长图文、12 页知识图解** | **1.0×** | **60px** | ⭐⭐⭐⭐⭐ |
| 默认长图 | 自适应 | 网页滚动 / Gamma / PDF | 1.0× | 8% 边距 | ⭐⭐ |
| 9:16 竖屏 | 1080×1920 | 视频号内文图 / 抖音封面 | 0.85× | 80px | ⭐⭐ |
| 桌面横屏 | 1920×1080 | 投影演示 / 视频封面 | 1.4× | 6% 边距 | ⭐ |
| 方形主图 | 1080×1080 | 朋友圈 / 微博 | 0.9× | 7% 边距 | ⭐⭐ |
| 手机长图 | 750×1334 (1x) / 1500×2668 (2x) | iPhone 6/7/8 Plus 适配 | 0.65-0.75× | 5-6% 边距 | ⭐ |

## 3:4 (1080×1440) · 默认画布 ★ 推荐

适用:小红书/公众号长图文、12 页知识图解、信息密度高的技术拆解

- 大标题 H1:92px(900 weight, line-height 1.05)
- 中标题 H2:56px(900 weight, line-height 1.10)
- 小标题 H3:36px(700 weight, line-height 1.20)
- 引文 Lead:32px(500 weight, line-height 1.40)
- 正文 Body:24px(400 weight, line-height 1.45)
- 注释 Body-sm:20px(400 weight, line-height 1.40)
- 代码 Code:18px(400 weight, line-height 1.55)
- 数字 Big-num:120px / Step-num:72px / Tier-num:80px(900 weight)
- Hero-title:104px / Hero-bg-num:380px(opacity 0.08)
- 内边距:60px(上下左右)
- 内容区:1080-120=960 宽

完整规范 → `style-spec.md`

## 9:16 竖屏 (1080×1920)

适用:视频号内文图、抖音封面、长视频截图

- 大标题 H1:60-72px
- 中标题 H2:36-42px
- 小标题 H3:24-28px
- 引文 Lead:22-24px
- 正文 Body:16-18px
- 注释 Body-sm:14-16px
- 代码 Code:12-13px
- 数字 Big-num:84-96px
- 内边距:56-64px
- 内容区:1080-120=960 宽 × 1920-120=1800 高

**为什么不推荐 9:16**:
- 缩略图过长,信息下移看不见
- 公众号/小红书默认封面 3:4,9:16 强制缩放会裁切
- 内容分布需要"上半挤压下半空"的妥协(用户原话:"3:4 结构吧,9 比 16 太长")

## 方形主图 (1080×1080)

适用:朋友圈单图、微博封面

- 内容必须精简,优先只保留"标题 + 1 个核心图 / 3 行短句"
- 大标题 H1:48-56px
- 中标题 H2:30-36px
- 正文:14-15px
- 内边距:60px

## 手机长图 (750×1334)

适用:iPhone 6/7/8 Plus 适配(老规格,2024 后推荐直接用 3:4)

- 大标题 H1:60-68px(原 84px → 缩 0.78×)
- 中标题 H2:34-40px(原 52px → 缩 0.75×)
- 正文:14-15px
- 卡片内文:12-13px
- 代码块 / 目录树:11-12px
- 内边距:48-56px

## 桌面横屏 (1920×1080)

适用:投影演示、视频封面

- 大标题 H1:128px(原 92px × 1.4)
- 中标题 H2:78px
- 正文:34px
- 内边距:60-80px

## 高度填满的关键技巧(★ 3:4 重点)

**坑**:固定高度画布(尤其是 1440px 的 3:4)如果用 `justify-content: center`,内容会被挤到中间,上下留出大块空白。

**正确做法**(用在模式 B 的 HTML 模板):

```css
.slide {
  width: 1080px;
  height: 1440px;
  padding: 60px 60px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
}

/* 关键:让 stack 撑满中间剩余空间,内部 space-between */
.content--spread {
  justify-content: space-between;
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

实际效果:标题固定顶部,stack 撑满中间,内部 block 用 space-between 自动均分 3-4 个卡片到全屏,无下半空。

## 哪些页最容易溢出

按 3:4 画布出现频率排序:
1. **多列卡片页**(痛点页、原则页):卡片堆不下必须改单列 + 缩字号
2. **目录树/YAML 配置页**:行数多 + 字号大,几乎必定溢出 → 缩到 16px / 行高 1.6
3. **AI 工具 chip 集合页**(slide-07 案例):chip 数量多,flex-wrap 后占用大量垂直空间 → 拆分类 chip + 缩字号
4. **三栏代码对比页**:每栏一个代码块,3:4 下字体必须缩到 16px 才能塞下

处理原则:**字号让位给布局,布局让位给信息密度**。宁可字号小,也要保证信息完整;宁可信息精简,也不要溢出。

## 反面案例

- 在 3:4 画布里塞 3 列卡片 + 60px 内边距 → 卡片内容被挤成 4-5 字一行,完全不可读
- 封面页用 `justify-content: center` 但内容总高度 > 视口 → 上下都留白,看起来像"半成品"
- 代码块不缩字号直接放进 3:4 画布 → 横向滚动条出现,截图截不到右侧
- 多 page 字号不统一(标题 60px / body 18px / code 12px 不成比例) → 视觉凌乱,不像一家人

## Playwright 截图关键参数

```python
viewport = {"width": 1080, "height": 1440}
device_scale_factor = 2  # 2x 高清,实际输出 2160×2880
```

- 一定要设 `device_scale_factor=2`,否则在视网膜屏看糊
- 截图前 `wait_for_timeout(800)` 等 Google Fonts 加载完,否则水印大字会回退到默认字体
- 用 `page.locator(".slide").nth(i).screenshot()` 单独截每张 slide 元素(比 full_page 精准)
- **必须用 Playwright 自带 chromium**:`/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome`
  - snap chromium 要 GLIBC 2.38,但系统是 2.35,**跑不起来**
  - 缺系统 lib 报 `libatk-1.0.so.0: cannot open shared object`,需 `sudo apt install libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libatspi2.0-0`

完整管线 → `pipeline-html-playwright.md`