# wechat_helper

> 微信公众号内容创作与分析工具集 — OpenClaw Skill

专注于公众号的全流程内容创作、配图、排版发布与爆款分析。

---

## 🚀 标准流水线（已验证，2026-05-28，2026-06-13 补充 renwei 改稿步骤）

从一篇 Markdown 草稿到公众号后台草稿箱：

```
选题讨论 → 初稿写作 → renwei 改稿(可选·默认开) → 三遍审校 → 配图生成 → HTML排版 → 图片上传 → 草稿推送
   │            │              │                │            │           │          │          │
 创作技能    创作技能      改稿技能         创作技能     配图技能    发布技能   发布技能   发布技能
```

**renwei 改稿说明**：「人味改稿」是默认开启的中间步骤，植入《人味儿写作心法》(renwei-writing)，原则是**少动 / 毛边是手迹 / 不写金句 / 上限是隐形**。每处改动都会交代理由；作者/黑爪爪可逐处回滚。详见 `INTEGRATION-renwei.md` 与 `renwei-writing/SKILL.md`。

**文章结构硬规则（2026-06-16 沉淀）**：
- **不带「本稿的 renwei 改稿实录」段落** —— 改稿是发布前内部工序，不上正文（仅 renwei skill 本身的教学性拆解文可保留作为演示）。
- **主语默认是「我」** —— 避免「Jerry 给/让/说/要求/丢来」这种把 Jerry 推到台前的破第四面墙写法。例：开篇「Jerry 给了我一个测试题」改写为「我拿来一个题」或直接进入演示。

**已验证的技术栈**：

| 环节 | 工具/模型 | 备注 |
|------|-----------|------|
| 初稿写作 | 黑爪爪风格 / Jerry 口述 | markdown 草稿存档于 `草稿/` |
| renwei 改稿 | renwei-writing 心法 | 少动 / 逐处交代 / 位置·代价·手迹 |
| 三遍审校 | 第一遍错别字 / 第二遍表达 / 第三遍风格 | 紧跟 renwei 改稿后面 |
| 配图生图 | gpt-image-2 via TokenRouter | 2K 分辨率，~2分钟/张 |
| 配图风格 | 马卡龙风格 | 柔和粉/薄荷绿/薰衣草，奶白底 |
| 图片压缩 | PIL → JPEG 85% | 原图 1.5MB → 95KB，微信正文限 1MB |
| HTML 排版 | jerry 规范（内联样式） | 品牌色块分隔、段落号、关键词着色 |
| 图片上传 | 微信 uploadimg API | 必须 mmbiz.qpic.cn 域名 |
| 草稿创建 | 微信 draft/add API | 封面 media_id + HTML content |

**即开即用口令**：
> "给这篇配图，马卡龙风格" → "排版推送到公众号"
> "打磨一下这段" → 走 renwei 改稿（少动·逐处交代）
> "跳过改稿直接排版" → 关闭 renwei 可选步骤

---

## 技能列表

### ✍️ wechat-creation — 内容创作

**公众号全流程创作技能（基于黑爪爪风格）**

从选题讨论→信息搜索→内容创作→renwei 改稿(可选)→三遍审校→爆款优化→配图标注。

| 能力 | 说明 |
|------|------|
| 选题讨论 | 3-4个方向 + 大纲 + 优劣势分析 |
| 信息搜索 | 写前必搜，确保内容有据 |
| 内容创作 | 初稿撰写 + renwei 改稿(可选·默认开) + 三遍审校 |
| renwei 改稿 | 「人味改稿」心法：少动 / 毛边是手迹 / 不写金句 / 逐处交代 |
| 爆款优化 | 5种爆文公式 + 完读率检查 |
| 配图标注 | 推荐5-8张配图位 |

---

### 🎨 long-article-illustration — 长文配图

**读取文章 → 拆段 → 生成配图提示词 → 调用生图模型**

| 能力 | 说明 |
|------|------|
| 架构图 prompt | 必须描述具体组件/层级/流向，禁止抽象概念 |
| 马卡龙风格 | 柔和粉彩、奶白底、2K 分辨率 |
| 生图引擎 | gpt-image-2 via TokenRouter（国内直连超时） |
| 图片压缩 | 自动转 JPEG <1MB，适配微信限制 |

**风格预设库**：扁平插画 / 科技感 / 马卡龙 / 水彩 / 极简线条 / 国风水墨

---

### 📤 wechat-draft-publish — 排版发布

**Markdown → jerry风格 HTML → 图片上传 → 草稿创建 → 发布**

| 能力 | 说明 |
|------|------|
| HTML 排版 | jerry规范：内联样式、品牌色块分隔、段落号、关键词着色 |
| 正文图上传 | 自动上传到微信 mmbiz.qpic.cn 域名 |
| 封面上传 | 获取永久素材 media_id |
| 一键发布 | 图片处理→封面上传→草稿创建，一步到位 |

---

### 🔥 wechat-explosive-analyzer — 爆款分析

**六维审核评分 + 可落地修改方案**

| 维度 | 权重 |
|------|------|
| 标题强度 | 30% |
| 开头钩子 | 20% |
| 选题切口 | 25% |
| 结构与节奏 | 15% |
| 社交货币 | 10% |
| 算法适配 | — |

触发：提供公众号文章链接 / 粘贴草稿 / 要求爆款诊断 → 输出评分+瓶颈+修改方案

---

### 📊 wechat-account-diagnostic — 账号诊断优化（官方API版）

**自动拉取数据 + 智能分析 + 可执行优化建议**

基于微信公众平台官方API，自动化完成从数据拉取到诊断报告生成的全流程。

| 能力 | 说明 |
|------|------|
| **自动数据拉取** | 自动拉取最近20篇文章列表 + 30天阅读/在看/分享统计数据 |
| **账号画像评分** | 100分制：更新规律性 + 标题风格统一性 + 主题集中度 + 人味指数 |
| **内容风格分析** | 标题类型分布、主题聚类、AI/人味信号检测 |
| **热点关联策略** | 结合AI哨兵晚报热点，输出立即跟进/深度挖掘/长期布局建议 |
| **可执行优化** | 不说"优化内容"这种空话，给出具体可落地的调整建议 |

**前置条件**：认证服务号/企业订阅号的 AppID + AppSecret（个人号可手动录入数据）

**一键使用**：
```bash
python wechat-account-diagnostic/scripts/account_analyzer.py full \
  --appid YOUR_APPID \
  --secret YOUR_SECRET \
  --output 诊断报告.md
```

触发：说"分析一下我的公众号" / "做个账号诊断" / "结合晚报看看内容策略"

→ 详细使用说明：[wechat-account-diagnostic/QUICKSTART.md](wechat-account-diagnostic/QUICKSTART.md)

---

### ✏️ renwei-writing — 人味改稿

**「打磨时把作者留住」的改稿心法**(2026-06-13 集成)

出自 `https://github.com/orange2ai/renwei-writing`(橘子/Cola)。原理：位置·代价·手迹三件事；原则：少动·毛边是手迹·不写金句·拿不准就白描·上限是隐形。

| 能力 | 说明 |
|------|------|
| 原理层 | 人味是什么、什么能动什么不能动、改动上限 |
| 事后检查 | 动过的地方扫一遍，破折号堆·「不是X而是Y」·意义拔高·万能展望 |
| 真实案例 | 橘子凌晨 5 点改 ADHD 观察的失败/成功版本对照 |

触发：用户提供一段文字要求「打磨/润色/改写/精简」；或 wechat-creation 流程初稿后的可选步骤。**默认开启**，作者/黑爪爪可逐处回滚；说「跳过改稿」可关闭。详见 `renwei-writing/SKILL.md` 与 `INTEGRATION-renwei.md`。

---

### 🗺️ knowledge-visual-cartographer — 知识视觉化排版方案（2026-06-18 集成 / 2026-06-19 重大更新）

**把一段知识拆成 N 页统一视觉风格的可视化幻灯片方案,支持三种渲染模式,页数动态根据字数算出**。

吃「主题 + 知识背景(1 句话补充也能跑)」,页数按 `核心字数 / 150` 算法 4-12 页自适应,产出 `[总览] + [逐页细节]` 结构化文本。

**三种渲染模式(用户选择)**:

| 模式 | 产出 | 适用 |
|------|------|------|
| **A · 纯文本合同**(原版) | `[总览] + [逐页细节]` | Gamma / Tome / PPT 手动渲染 |
| **B · HTML + Playwright**(默认) | 12 张 1080×1440 PNG | **公众号/小红书长图文**(推荐) |
| **C · greenbook 模板** | `gen_media.sh --style cartographer` | 封面 / 单页概念图 |

**模块架构**(5 必选 + 6 扩展,扩展页数动态命中):
- 必选:M1 封面 / M2 痛点 / M3 定义 / M4 价值 / M5 金句(无论密度必出)
- 扩展:M6 代码结构 / M7 代码示例 / M8 设计原则 / M9 落地样包 / M10 概念图谱 / M11 Q&A(按特征触发)
- 统一视觉:`#FCF6E0` 米黄底 + `#1A1A1A` 黑块 + `#FFD700` 黄块,全左对齐无衬线
- 画布:默认 3:4 (1080×1440);9:16 / 方形 / 手机长图按 `canvas-specs.md` 缩放

**页数控制**(2026-06-19 新增动态算法):

| 知识背景字数 | 总页数 |
|----|----|
| < 80 字 | 4 页(纯骨架) |
| 80-150 字 | 5 页(加痛点) |
| 150-300 字 | 6 页 |
| 300-600 字 | 7-8 页 |
| 600-1200 字 | 9-10 页 |
| 1200-2000 字 | 11-12 页 |
| ≥ 2000 字 | 12 页 + 提示拆套 |

**与 greenbook-creator / long-article-illustration 互补场景**:
- greenbook-creator:7-9 张短图文(单图独立成卡,小绿书/公众号轮播)
- long-article-illustration:1 张配图/段(长文逐段插图)
- **cartographer**:4-12 页讲解型长图(多页连贯叙事,讲清一个概念/方法论/复盘)

**触发**:用户说「做个长图讲解 X」「出一套信息图」「做幻灯片讲清楚 X」「可视化拆解」「画个思维导图式的图」「出个 12 页长图文讲 X」,或给一段资料要求「做成图示/排版方案」。

**当前状态**:**独立工具类**,不接入主流水线(用户决定"先不接")。需要时手动触发。模式 B 配套 HTML + Playwright 管线详见 `references/pipeline-html-playwright.md`;模式 B/C 模板复用 `greenbook-creator/references/cartographer-template/`。

详见 `knowledge-visual-cartographer/SKILL.md` 与 `INTEGRATION-cartographer.md`。

---

## 目录结构

```
wechat_helper/
├── wechat-creation/                      # 内容创作技能
│   ├── SKILL.md
│   └── references/ (style-guide, templates, practical-notes)
├── long-article-illustration/            # 长文配图技能
│   ├── SKILL.md
│   └── references/ (style-presets, prompt-templates)
├── wechat-draft-publish/                 # 排版发布技能
│   ├── SKILL.md
│   ├── scripts/ (wechat_api, build_article)
│   └── references/
├── wechat-explosive-analyzer/            # 单篇爆款分析技能
│   ├── SKILL.md
│   └── references/
├── wechat-account-diagnostic/            # 全账号诊断优化技能
│   ├── SKILL.md
│   ├── references/ (diagnostic-framework, data-metrics, style-guidelines)
│   └── scripts/
├── greenbook-creator/                    # 绿皮书创作技能（新增）
│   ├── SKILL.md
│   ├── scripts/ (gen_image, publish)
│   └── references/ (design-system, copy-templates, style-ai-tech)
├── renwei-writing/                       # 人味改稿技能 (2026-06-13 集成)
│   ├── SKILL.md
│   └── references/ (post-edit-checklist, case-study)
├── knowledge-visual-cartographer/        # 知识视觉化排版方案 (2026-06-18 集成)
│   ├── SKILL.md
│   └── references/ (module-catalog, style-spec, canvas-specs)
├── README.md
├── INTEGRATION-renwei.md                 # renwei 接入说明
├── INTEGRATION-cartographer.md           # cartographer 接入说明
├── 新功能/                               # 新功能文章与架构图
├── 信息池/                               # 历史文章与数据池
└── 草稿/                                 # 文章草稿存档
```

---

## 第四次文章发布纪实（2026-05-28）

标题：《一天4700颗星——Understand-Anything证明「代码理解」正在从阅读变成导航》

**流水线实录**：
1. 数据收集 → 7款代码理解工具横评
2. 初稿写作 → ~3700字
3. 配图生成 → gpt-image-2 马卡龙风格 4 张（TokenRouter 中转）
4. 图片压缩 → 1.5MB PNG → 95KB JPEG
5. HTML 排版 → jerry 规范，6 段章节 + 产品矩阵
6. 图片上传 → 4 张正文图 + 1 张封面
7. 草稿推送 → 公众号后台草稿箱 ✅

**关键教训**：
- gpt-image-2 国内必须走 TokenRouter，直连 OpenAI 超时
- 架构图 prompt 必须描述具体组件/层级/流向，纯抽象概念出图无信息量
- 微信正文图片限 1MB，gpt-image-2 出图 ~1.5MB 需 JPEG 压缩
