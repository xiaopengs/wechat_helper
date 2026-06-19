# knowledge-visual-cartographer 接入说明

> 2026-06-18 集成 — 把「知识视觉化排版方案」作为 wechat_helper 的**独立工具类技能**,不接入主流水线（按用户要求"先不接"）。

## 这是什么

[`knowledge-visual-cartographer/`](./knowledge-visual-cartographer/) 是从 QQ 附件同步来的一个 **结构化排版方案生成器**(作者未知,版本 v2)。它的全部目的:**把一段知识(主题 + 背景)拆成 N 页统一视觉风格的可视化幻灯片方案,以纯文本合同形式输出。**

它**不直接出图**。产出的是"排版指引文本"(`[总览] + [逐页细节]`),下游交给 Gamma / Tome / HTML / PPT 工具渲染。

## 在 wechat_helper 里的位置

```
wechat_helper/ 工具集
├── 主流水线: 选题 → 初稿 → renwei 改稿 → 排版 → 配图 → 发布
├── 独立工具(创作类):  wechat-creation / wechat-explosive-analyzer / wechat-account-diagnostic
├── 独立工具(视觉类):  long-article-illustration / greenbook-creator / knowledge-visual-cartographer   ← 本次新增
├── 独立工具(改稿类):  renwei-writing
└── 独立工具(发布类):  wechat-draft-publish
```

**与主流水线的衔接点(可选,本版未自动接入)**:
- **初稿写作** 之后,产出主题词 + 知识背景 1 句话补充,丢给 cartographer 出 N 页方案
- **配图生成** 之前,把 cartographer 方案丢给 Gamma 或 visual-page 渲染,得到实际长图
- **HTML 排版** 时,若方案是"手机长图(750×1334)"或"9:16 竖屏(1080×1920)",按 `references/canvas-specs.md` 缩字号

**用户决定先不接**。当前状态:catalog 里登记,流水线里不默认调用,需要时手动触发。

## 三件套约定

cartographer 只做三件事:

1. **5 个必选模块**(无论信息密度都出):封面 / 痛点 / 定义 / 价值 / 金句
2. **6 个扩展模块**(按输入特征触发):代码结构 / 代码示例 / 设计原则 / 落地样包 / 概念图谱 / Q&A
3. **统一视觉规范**:`#FCF6E0` 米黄底 + `#1A1A1A` 黑块 + `#FFD700` 黄块,全左对齐,无衬线

页数自适应:**4-12 页**(必选 5 页 + 扩展 0-7 页),超出 12 说明内容应拆两套图。

## 输出合同

执行后必须按以下结构输出纯文本:

```
[总览]
共 N 页
1. <页 1 标题>
2. <页 2 标题>
...
N. <页 N 页标题>

[逐页细节]

### 第 1 页 / 共 N 页
- 标题: <标题(不超过 10 字)>
- 布局: <左文右码 / 上图下文 / 整版金句 / 三栏对比 / ...>
- 视觉重点: <黑底块 / 黄底块 / 代码块 / 目录树 / 双栏对比>
- 核心文案:
  - <短句 1(每条 ≤ 1 行)>
  - <短句 2>
  - <短句 3>
```

**不包含**真实 CSS/HTML 代码(避免和 visual-page / 用户设计工具冲突);如要 HTML 渲染,**提示"切换到模式 B"**(见下文)。

> **2026-06-19 重大更新**:**新增 3 种渲染模式**(SKILL.md 顶部 inputs 加了"渲染模式三选一"),让用户决定下游怎么出图。

## 渲染模式三选一(2026-06-19 新增)

| 模式 | 产出 | 优点 | 缺点 | 适用 |
|----|----|----|----|----|
| **A · 纯文本合同** | `[总览] + [逐页细节]` 文本 | 灵活、可对接 Gamma/Tome/PPT | 用户需自己手动渲染 | 商业演示 / 内部汇报 / 设计师自己排 |
| **B · HTML + Playwright(默认)** | 12 张 1080×1440 PNG | 精确排版、代码块清晰、可批量改 | 需装 Playwright + 系统 lib | **公众号/小红书长图文、技术拆解、代码密集型内容** ★ |
| **C · greenbook 模板** | `gen_media.sh --style cartographer` 单张生图 | 快、风格统一、不需 HTML | AI 生图在多代码块/中文段落会 OOD | 封面 / 概念插图 / 单页海报 |

**默认模式 B**,用户没指定就走这条路径。

## 跟现有 skill 的区别(避免误用)

| Skill | 产出形式 | 页数 | 适用场景 |
|---|---|---|---|
| **greenbook-creator** | 短图文卡片(AI 生图)| 4-6 张 | 小绿书 / 公众号轮播(单图独立成卡) |
| **long-article-illustration** | 单张配图 | 1 张/段 | 长文逐段插图(单图配文字) |
| **knowledge-visual-cartographer 模式 A** | 讲解型长图文本方案 | 4-12 页 | 概念讲解 / 方法论(Gamma/Tome 手动渲染) |
| **knowledge-visual-cartographer 模式 B(默认)** | 12 张 1080×1440 PNG + 公网 URL | 6-12 页 | 公众号/小红书长图文(精确排版,代码密集) |
| **knowledge-visual-cartographer 模式 C** | `gen_media.sh --style cartographer` AI 生图 | 任意 | 封面 / 单页概念图 |

**何时用 cartographer**:
- 内容是「讲清楚一个概念」(RAG 是什么 / 注意力机制怎么工作)
- 内容是「拆解一个方法论」(3 步决策框架 / 5 阶段产品流程)
- 内容是「复盘一个宏观话题」(AI 编程这一年)
- 常规推文/快讯/书评 ❌ 不要用(用 greenbook 或 long-article-illustration 更合适)

**模式选择决策树**:
- 内容有大量代码块/配置 → **模式 B**
- 内容纯概念/方法论/叙事 → **模式 A**(给 Gamma/Tome)或**模式 C**(AI 生图)
- 不确定 → **模式 B**(默认)
- 用户明确要 PPTX → 模式 A + 提示用 minimax-pptx

## 配套 skill(已就位 / 待装)

### HTML + Playwright 模板(已就位)

`wechat_helper/greenbook-creator/references/cartographer-template/` 包含 12 页完整 HTML 模板,模式 B 直接复用:

```
cartographer-template/
├── index.html      # 12 页结构骨架,改文案即可
├── css/styles.css  # 3:4 字号/颜色 token 全固化
└── _shoot.py       # Playwright 截图脚本
```

完整管线 + 踩坑 → `wechat_helper/knowledge-visual-cartographer/references/pipeline-html-playwright.md`

### minimax-visual-page(待装,非公开)

SKILL.md 多次提到 **`minimax-visual-page`** —— 负责把 [逐页细节] 转成 HTML 的渲染器。

- **状态**:GitHub 搜不到(`api.github.com/search/repositories?q=minimax-visual-page` 返回 `total_count: 0`),**非公开**
- **依赖路径**:cartographer SKILL.md 写"如用户明确要 HTML 渲染,提示把以上逐页细节发给我,我用 visual-page skill 转成 HTML"
- **计划**:用户提供 zip 后,按 cartographer 同样方式放到 `wechat_helper/minimax-visual-page/` 平级位置
- **临时替代**:用本 skill 模式 B + cartographer-template(功能等价,且更精确)

## 触发方式

**手动触发**(默认,本版未做自动识别):
- 用户说"做个长图讲解 X"、"出一套信息图"、"做幻灯片讲清楚 X"、"可视化拆解"、"画个思维导图式的图"
- 用户给一段资料并要求"做成图示/排版方案"
- 用户说"出一套 12 页长图文 / 小绿书 / 公众号图解"

**默认走模式 B**(HTML+Playwright),除非用户指定其他模式。

**自动触发候选场景**(后续可加,但本版不做):
- 创作 skill 初稿后,若检测到「概念讲解」/「方法论」/「宏观复盘」标签,自动调用 cartographer 出方案
- 配图生成前,若需要"讲解类长图"载体,自动调用

## 文件结构(2026-06-19 更新)

```
wechat_helper/
└── knowledge-visual-cartographer/
    ├── SKILL.md                          # 心法 + 输入输出 + 失败处理 + 3 模式选择
    └── references/
        ├── module-catalog.md             # 5+6 模块清单 + 触发条件
        ├── style-spec.md                 # 颜色/字号/版式/不允元素(3:4 优化版)
        ├── canvas-specs.md               # 固定画布字号缩放(默认 3:4)
        └── pipeline-html-playwright.md   # 模式 B 完整管线 + 踩坑(2026-06-19 新增)
```

## 使用流程(完整版)

```
1. 用户提需求: 「用 cartographer 做个 RAG 讲解」/「出 12 页长图文讲 X」
2. agent 确认: 主题 + 知识背景(必填) + 渲染模式(默认 B) + 画布(默认 3:4)
3. agent 按 SKILL.md Procedure 跑:
   - 判断内容密度 → 4-5 / 6-9 / 10-12 页
   - 跑必选 M1-M5
   - 按特征激活扩展 M6-M11
   - 每页填 4 字段(标题/布局/视觉重点/核心文案)
4. agent 按用户选择的模式输出:
   - 模式 A: 输出 [总览] + [逐页细节] 纯文本
   - 模式 B: 输出 [HTML 变更清单] + 跑 _shoot.py + 部署 1Panel + curl 验 200 + 用 <qqimg> 发公网 URL
   - 模式 C: 输出 [AI 生图 prompt] + 跑 gen_media.sh
5. 用户确认后,可发布到小红书/公众号/微信图文
```

## 上游/许可

- **来源**: QQ 附件 `knowledge-visual-cartographer-v2_*.zip`(2026-06-18 收到)
- **作者**: 未知(SKILL.md 头部未署名)
- **许可**: 未知(zip 内无 LICENSE 文件)
- **版本**: v2(从 zip 文件名推断)

⚠️ **授权未确认**: 内部使用 OK,如要对外发布或二次分发,需先确认作者授权。

## 已知限制

- **模式 A**:不直接出图,需靠下游 Gamma/Tome/PPT
- **模式 B**:依赖 Playwright(一次性装好,见 pipeline-html-playwright.md);部署依赖 1Panel 静态站
- **模式 C**:AI 生图在多代码块/中文段落会 OOD,仅适合封面/概念图
- **未对接 wechat-draft-publish**:cartographer 出的 12 张图,要变成公众号图文需要手动复制到草稿箱(看 build_article 是否兼容,本版未验证)
- **未对接 minimax-visual-page**(待装)

## 关联资源

- 模板:`wechat_helper/greenbook-creator/references/cartographer-template/`
- 设计系统:`wechat_helper/greenbook-creator/references/style-cartographer.md`
- AI 生图风格:`wechat_helper/greenbook-creator/scripts/styles/cartographer.txt`
- 12 页骨架示例:OpenRouter × Coding Agents(`openrouter-cartographer/`)
- Playwright 截图踩坑:MEMORY.md "12 页知识图解 HTML+Playwright 管线"
- QQ Bot 发图踩坑:MEMORY.md "QQ Bot `<qqimg>` 发送图片踩坑"

## 上游/许可

- **来源**: QQ 附件 `knowledge-visual-cartographer-v2_*.zip`(2026-06-18 收到)
- **作者**: 未知(SKILL.md 头部未署名)
- **许可**: 未知(zip 内无 LICENSE 文件)
- **版本**: v2(从 zip 文件名推断)

⚠️ **授权未确认**: 内部使用 OK,如要对外发布或二次分发,需先确认作者授权。

## 已知限制

- **不直接出图**:必须靠下游(Gamma / Tome / visual-page / 手动)
- **未对接现有生图链路**(`gen_media.sh` 是单张生图,不是排版渲染;`long-article-illustration` 是按文章段配图,不是讲解型多页)
- **未对接 wechat-draft-publish**:cartographer 出的 N 页方案,要变成公众号图文需要走别的渲染路径(等 visual-page)
- **依赖 minimax-visual-page 才有自动化 HTML 渲染能力**:目前需要手动复制到 Gamma / Tome
