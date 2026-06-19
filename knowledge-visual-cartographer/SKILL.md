---
name: knowledge-visual-cartographer
description: |
  将任意知识型主题(技术概念 / 方法论 / 知识框架)自动拆解为一套统一视觉风格、动态页数的可视化幻灯片方案。
  触发场景:用户说"做个长图讲解""出一套信息图""做幻灯片讲清楚 X""可视化拆解""画个思维导图式的图"
  短语,或者直接给一段资料并要求"做成图示/排版方案"。
  不触发:用户要生成真实 PPTX/PDF 文件(交给 minimax-pptx / minimax-pdf)、要纯文字总结、
  要一段对话式讲解。
  
  **2026-06-19 更新**:支持三种渲染模式(用户选择):
  - A) 纯文本合同输出(给 Gamma/Tome/PPT 工具)
  - B) HTML + Playwright 直接出图(精确排版 12 张 PNG,推荐)
  - C) 复用 greenbook-creator cartographer 模板(最快)
---

# Knowledge Visual Cartographer

## Inputs to collect

执行前从用户输入里确认/提取以下信息;缺失则按下方默认推断并在输出里标注 [默认] 让用户确认:

- **主题/核心概念**:一句话能讲清的主题词(必填)
- **知识背景**:文章 / 大纲 / 一句话补充(必填,1 句话也能跑)
- **目标受众**:开发者 / 管理者 / 普通职场人 / 学生(默认:通用职场人,中等深度)
- **画布尺寸**:**默认 3:4 (1080×1440)** — 小红书/公众号原生比例;若用户明确要其他比例,见 `references/canvas-specs.md`
- **⏵ 渲染模式(三选一,默认 B)**:
  - **A · 纯文本合同**:输出 `[总览] + [逐页细节]`,给 Gamma/Tome/PPT/HTML 工具渲染
  - **B · HTML + Playwright**(默认):直接产出 12 张 PNG 截图,精确排版,代码块清晰
  - **C · greenbook-creator 模板**:复用 `wechat_helper/greenbook-creator/references/cartographer-template/`,改 index.html 即可

最少必要输入:**主题 + 知识背景**。其它都能用默认值。

## Procedure

### 1. ⏵ 动态计算页数(根据知识背景字数)

**不再拍脑袋估"密度"档,而是用字数算出精确页数**。

#### 1.1 计算公式

```
核心字数 (CW) = 知识背景中文字数(不含标点/空格/代码块)
必选页数 = 4 页(M1+M3+M4+M5),若 CW ≥ 80 字则 +M2 痛点 = 5 页
扩展页数 = clamp(round(CW / 150), 0, 8)
总页数 = min(必选页数 + 扩展页数, 12)
```

**解读**:
- `CW / 150`:每 150 个中文字消耗 1 页(中文字密度经验值,可调整)
- `clamp(..., 0, 8)`:扩展页数最多 8 页
- `min(..., 12)`:总页数硬上限 12 页

#### 1.2 字数 → 页数速查表

| 知识背景字数 | 必选页数 | 扩展页数 | **总页数** | 处理 |
|----|----|----|----|----|
| < 80 字 | 4 | 0 | **4 页** | 纯骨架,无 M2 |
| 80-150 字 | 5 | 0 | **5 页** | 加 M2,刚起步 |
| 150-300 字 | 5 | 1 | **6 页** | 走出骨架 |
| 300-450 字 | 5 | 2 | **7 页** | 内容成形 |
| 450-600 字 | 5 | 3 | **8 页** | 内容丰富 |
| 600-900 字 | 5 | 4 | **9 页** | 内容充实 |
| 900-1200 字 | 5 | 5 | **10 页** | 开始拆细则 |
| 1200-1500 字 | 5 | 6 | **11 页** | 接近上限 |
| 1500-2000 字 | 5 | 7 | **12 页** | 上限 |
| ≥ 2000 字 | 5 | 8(钳到上限) | **12 页** | **提示拆套** |

#### 1.3 示例

- 主题"RAG 是什么"+ 背景 "为什么它比直接微调模型好"(12 字)→ CW=12 < 80 → **4 页**(封面+定义+价值+收束)
- 主题"RAG"+ 背景 200 字 → CW=200 → 5 + round(200/150)=5+1=**6 页**
- 主题"OpenRouter × Coding Agents"+ 背景 1500 字 → CW=1500 → 5 + round(1500/150)=5+10(钳到 8)=13 → min(13,12)=**12 页**

### 2. ⏵ 按扩展页数选扩展模块(M6-M11)

**总页数 = 必选页数 + 扩展页数,按特征逐一装填**:

| CW 范围 | 命中的扩展模块 |
|----|----|
| < 150 | 无(纯骨架) |
| 150-400 | M8 设计原则(三条),或 M6 结构拆解(一句话级别) |
| 400-800 | M6 + M8;若含代码字串命中 M7;若含案例命中 M9 |
| 800-1500 | M6 + M7 + M8 + M9 |
| 1500-2000 | M6 + M7 + M8 + M9 + M10 概念图谱 |
| ≥ 2000 | M6 + M7 + M8 + M9 + M10 + M11 Q&A;**提示拆套** |

### 3. 必选模块(M1-M5,不受页数影响)

- M1 封面 → 定调,黑底金句
- M2 痛点 → 3 个核心困境,黑底卡片(**仅 CW ≥ 80 才出现**)
- M3 定义 → "是什么 vs 不是什么" 对比
- M4 价值 → 对使用者的具体改变
- M5 金句 → 一句话收束

### 4. 扩展模块(M6-M11,按 1.3 命中)

- 含代码/配置 → M6 结构拆解 + M7 代码示例
- 含架构/原则 → M8 设计原则
- 含案例/产出 → M9 落地样包
- 宏大跨层 → M10 概念图谱
- 含 FAQ → M11 问题与解答

### 5. 扩展页数不足时的处理

**重要**:**总页数 = 必选页数 + 扩展页数**,两者必须凑够:

- **总页数 < 5**:从 M2 痛点 / M8 设计原则中凑,不建议降必选
- **总页数 = 4 且 CW ≥ 80**:自动补 M2 痛点变成 5 页
- **总页数 > 12**:跳过上限,**提示拆套为 [A] [B]**,并在输出里标注"建议拆为两套,本页数仅作单套最大输出"
- **总页数 ∝ 字数**:不要为了凑页数加重复内容(原则反向:**减内容而非加**)

### 6. 每页填三个字段
- **标题**:不超过 10 个字
- **排版布局建议**:左文右码 / 上图下文 / 整版金句 等具体说明
- **核心文案**:短句为主,每条不超过 1 行,整页 ≤ 6 行

### 7. 复用统一视觉规范(不允许某一页自由发挥)

### 4. 每页填三个字段
- **标题**:不超过 10 个字
- **排版布局建议**:左文右码 / 上图下文 / 整版金句 等具体说明
- **核心文案**:短句为主,每条不超过 1 行,整页 ≤ 6 行

### 5. 复用统一视觉规范(不允许某一页自由发挥)
- 底色 `#FCF6E0`(米黄),黑块 `#1A1A1A`,黄块 `#FFD700`
- 字体:无衬线,全部左对齐
- **页数控制**:**总页数 = 必选页数 + 扩展页数(动态根据字数计算)**,见 Procedure 第 1 步
- 字号表:**3:4 (1080×1440) 优化版**(详见 `references/style-spec.md`)
  - H1 92px / H2 56px / H3 36px / Lead 32px / Body 24px / Code 18px / Big-num 120px / Step-num 72px / Tier-num 80px / Hero-title 104px
  - Slide padding 60px,行距 1.4

### 8. ⏵ 渲染模式分支(用户选择 / 默认 B)

#### 模式 A · 纯文本合同(原版)
**用途**:下游交给 Gamma / Tome / HTML / PPT 工具渲染
**输出**:见下方"Output contract · 模式 A"部分,纯文本 `[总览] + [逐页细节]`
**不做**:不出 HTML、不跑 Playwright、不调 `gen_media.sh`

#### 模式 B · HTML + Playwright(默认,推荐)
**用途**:直接产出 12 张 PNG 截图,精确排版,代码块清晰,适合公众号/小红书长图文
**流程**:
1. **复制模板**: `cp -r /home/ubuntu/.openclaw/workspace/wechat_helper/greenbook-creator/references/cartographer-template/ /tmp/<project>/`
2. **写 HTML**: 打开 `/tmp/<project>/index.html`,按"逐页细节"修改 12 个 `<section class="slide">` 内容,删除模板里所有占位文案
3. **不动 CSS**: `css/styles.css` 已固化好 3:4 排版规范,任何修改都先回到这个文件
4. **截图**: `cd /tmp/<project> && python3 _shoot.py` → 输出 `screenshots/slide-01.png` ~ `slide-12.png`
5. **部署**: cp 到 1Panel 静态站(`/home/ubuntu/1panel/www/sites/thinkspc.fun/index/<project>/screenshots/`)+ `sudo chown -R root:root` + `sudo chmod 644 *.png`
6. **发送**: 用公网 URL 形式发到 QQ/微信(`<qqimg>https://thinkspc.fun/static/<project>/screenshots/slide-XX.png</qqimg>`,base64 上传会被 QQ 服务端拒)
**完整脚本与踩坑**: 见 `references/pipeline-html-playwright.md`

**前置依赖**(一次性装好):
```bash
pip install playwright && playwright install chromium
sudo apt install libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libatspi2.0-0
```
注意:**只能用 Playwright 自带 chromium**(`/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome`),snap chromium 要 GLIBC 2.38 但系统是 2.35 跑不起来

#### 模式 C · greenbook-creator 模板(最快)
**用途**:复用 cartographer-template 的完整 12 页结构,只改文案
**前置**:用户已读过 `greenbook-creator/references/style-cartographer.md` 并选定 cartographer 风格
**流程**:
1. 直接调 `wechat_helper/greenbook-creator/scripts/gen_media.sh generate --style cartographer --prompt "..."`
2. 风格预设已写好,只需把"逐页细节"翻译成 AI 生图 prompt
3. 适合「结构清晰但视觉可以灵活发挥」的场合(注:AI 生图在多代码块/中文段落会 OOD,纯概念图/封面适用)

### 7. 自检(交付前)
- 必选 5 模块是否齐?
- 扩展模块是否对应输入特征?
- 总页数 4-12 之间?
- 文案短句化?(任何一条超过 1 行就改)
- **模式 B/C 必须验证**:部署到公网 → curl 验 200 → 实际发送一张到 QQ/微信确认能正常显示
- **模式 B 的 spread 陷阱快速检查**(详见 `references/pipeline-html-playwright.md` Q9):
  - [ ] 自定义容器(`.loop-grid` / `.process-grid` / `.cure-list` / `.quote-bar` / `.timeline`)都有 `flex: 1 1 auto; min-height: 0;`
  - [ ] 没用 `space-between` 推 stack / cure-list 内部 block(改用 `gap: 16-20px`)
  - [ ] grid 容器保留 `display: grid`,没被改成 `flex column`
  - [ ] quote-bar 靠下用 `margin-top: auto`,**不是** `align-self: flex-end`
  - [ ] 卡片(`.loop-card` / `.process-row`)有 `height: 100%; box-sizing: border-box;` 撑满 grid cell

## Output contract

### 模式 A · 纯文本合同

按以下结构输出,纯文本,可直接复制到 Gamma/Tome/HTML/PPT 工具:

```
[总览]
共 N 页
1. <页 1 标题>
2. <页 2 标题>
...
N. <页 N 标题>

[逐页细节]

### 第 1 页 / 共 N 页
- 标题: <标题>
- 布局: <左文右码 / 上图下文 / 整版金句 / ...>
- 视觉重点: <用黑底块 / 黄底块 / 代码块 / 目录树>
- 核心文案:
  - <短句 1>
  - <短句 2>
  - <短句 3>
```

输出**不包含**真实 CSS/HTML 代码(避免和 minimax-visual-page / 用户自身设计工具冲突);如用户明确要 HTML 渲染,提示"切换到模式 B"。

### 模式 B · HTML + Playwright

按以下结构输出,先列变更清单再给文件:

```
[总览]
共 N 页
1. <页 1 标题>
...

[逐页细节 · HTML 变更清单]

### 第 1 页 / 共 N 页
- 标题: <标题>
- 布局: <黑底 hero / content--spread / qa stack / tier cards / ...>
- 视觉重点: <h1 92px / big-num 120px / cat-label 黄底 / ...>
- HTML 变更:
  - 编辑 `index.html` 第 X-Y 行,替换为:
    ```html
    <section class="slide slide--black slide--hero">
      ...
      <h1 class="hero-title">...</h1>
      ...
    </section>
    ```
- 核心文案:
  - <短句 1>
  - <短句 2>
```

执行后:跑 `_shoot.py` → cp 到 1Panel → curl 验 200 → 用公网 URL 发 12 张 `<qqimg>` 给用户

### 模式 C · greenbook-creator 模板

按以下结构输出 AI 生图 prompt,直接喂 `gen_media.sh`:

```
[逐页细节 · AI 生图 prompt]

### 第 1 页 / 共 N 页
- prompt: 米黄底色 #FCF6E0,黑块 #1A1A1A,黄块 #FFD700。整版黑底封面,顶部 KNOWLEDGE 水印。中央大数字 "300+",字号 380px,半透明黄色。标题「一把 Key 接住 300+ 模型」,字号 104px,白色。底部页码 01 / 12。
- 风格: --style cartographer
- 输出: --out screenshots/slide-01.png
- 核心文案: ...
```

## Failure handling

- **主题过于抽象,无法落到痛点**:不强凑痛点,改用"为什么这件事值得讲"开场,并在最终页里跟用户说明"主题偏抽象,痛点页是改造版"
- **用户只给一句话,信息密度极低**:压缩到 4 页骨架(痛点→定义→价值→总结),不要硬撑到 6 页以上
- **下游载体明确是 PPT 文件**:走模式 A,提示用户"这是排版指引文本,生成真实 PPTX 请用 minimax-pptx",不要自己越界去生成文件
- **用户后续要改视觉风格**:不要在原页上"加一点别的颜色",整套风格是固定资产;模式 B 建议回到 `css/styles.css` 修改;模式 C 建议改 `--style` 参数重新跑
- **用户要求固定画布(如 750×1334、9:16、方形)**:必须读 `references/canvas-specs.md` 重新校准字号/留白/列数;不做校准直接渲染会出现卡片溢出或大面积空白
- **模式 B 跑 Playwright 失败**:检查 chromium 路径 / 系统 lib / GLIBC 版本,见 `references/pipeline-html-playwright.md` 故障排查章节
- **模式 B 部署到 1Panel 失败**:老文件是 root:root 644,`cp -f` 不能覆盖,改用 `sudo cp -f`;验证用 `curl -s`(GET),不要用 `curl -sI`(HEAD,nginx HEAD 走不同 rewrite 链)

## Examples

### 输入

- 主题:RAG(检索增强生成)是什么
- 知识背景:一句话补充——为什么它比直接微调模型好
- 渲染模式:模式 B(默认)
- 画布:3:4(默认)

### 输出(模式 B · 简化版)

```
[总览]
共 7 页
1. 封面: 大模型落地的最后一公里
2. 痛点: 直接微调的三个坑
3. 定义: RAG vs Fine-tuning 对比
4. 结构: RAG 工作流的四块积木
5. 代码: 一个最小可运行的 RAG 配置
6. FAQ: 什么时候用 RAG,什么时候用微调
7. 收束: 模型的水管,不是博物馆

[逐页细节 · HTML 变更清单]

### 第 1 页 / 共 N 页
- 标题: 大模型落地的最后一公里
- 布局: slide--black slide--hero(整版黑底 + 大数字水印)
- 视觉重点: 顶部 kicker "KNOWLEDGE · 7 PAGES · 3:4",中央 hero-title 92px,"RAG" 半透明背景数字 380px
- HTML 变更:
  - 编辑 `index.html` 第 12-32 行,替换为:
    ```html
    <section class="slide slide--black slide--hero">
      <div class="watermark">KNOWLEDGE</div>
      <div class="content">
        <div class="kicker">KNOWLEDGE · 7 PAGES · 3:4</div>
        <div class="cat-label">第 01 章 · 引子</div>
      </div>
      <div class="hero-center">
        <div class="hero-accent"></div>
        <div class="hero-bg-num">RAG</div>
        <h1 class="hero-title">大模型落地的<br />最后一公里</h1>
        <p class="hero-sub">给模型接上一根实时水管<br />模型再强,知识不更新就是博物馆</p>
      </div>
      <div class="content" style="display:flex; justify-content:space-between;">
        <div class="foot">@knowledge-cartographer</div>
        <div class="foot">01 / 07</div>
      </div>
    </section>
    ```
- 核心文案:
  - 模型再强,知识不更新就是博物馆
  - RAG: 给模型接上一根实时水管
```

执行后:跑 `_shoot.py` → cp 到 1Panel → curl 验 200 → 用 `<qqimg>` 公网 URL 发 7 张图

详见:
- `references/module-catalog.md` — 必选 5 模块 + 扩展 6 模块触发条件
- `references/style-spec.md` — 颜色 / 字号 / 版式细节(2026-06-19 更新为 3:4 优化版)
- `references/canvas-specs.md` — 3:4 / 9:16 / 方形 / 手机长图 等画布适配参数
- `references/pipeline-html-playwright.md` — HTML 渲染管线 + Playwright 踩坑(2026-06-19 新增)