---
name: greenbook-creator
description: 小绿书（微信图文消息）内容创作全流程助手。覆盖选题策划→图片设计→短文撰写→排版发布，专为微信生态内"图片+短文"轻量内容格式打造。触发词：小绿书/绿书/图文消息/微信图文/图片笔记/公众号轮播图/图文卡片/科普海报/信息图海报/poster/carousel。也适用于"把XX做成图"、"生成一套XX图"、"XX风格的轮播图"等自然语言请求。使用时自动读取 references/ 下的设计系统和文案模板。
---

# 小绿书创作 — 让信息在滑动中完成传递

## 目标

将结构化内容（教程、清单、对比、攻略、观点）转化为微信公众号「图片·文字」消息格式。每张图独立可传播，图文互补而非重复。

**同时支持两种规格**:
- **小绿书图文消息**: ≤6 页(含封面),手机端阅读,信息密度适中 → `default` / `tech-dark` / `tech-light` 风格
- **长图文知识图解**: 6-12 页,小红书/公众号长文配图,精确排版,信息密度高 → `cartographer` 风格 + HTML+Playwright 管线

## 第一性原理

> **小绿书的本质不是「做漂亮的图」，而是「让信息在滑动中完成传递」。**
> 图是信息容器，文是注意力钩子。

核心公式：**70% 信息设计 + 20% 排版 + 10% 插画**

**规格 1：小绿书图文消息（≤6 页）**
- 图片上限：≤ 6 张（含封面），多一页不如少一页
- 出图引擎：gpt-image-2（默认，TokenRouter 路由），全篇统一 Prompt 体系 + 风格预设
> 也支持 Gemini 图像系列 (`gemini-2.5-flash-image` / `gemini-3.1-flash-image-preview` / `gemini-3-pro-image-preview`) 与字节方舟视频 (`doubao-seedance-2.0-fast` / `doubao-seedance-2.0`) — 详见 [scripts/gen_media.sh](scripts/gen_media.sh)
- 风格：default / tech-dark / tech-light

**规格 2：长图文知识图解（6-12 页）**
- 适用：技术拆解、概念地图、对比手册、FAQ 集
- 出图引擎：**HTML + Playwright 截图**（非 AI 生图，AI 在多页/多代码块/中文段落上会 OOD）
- 风格：**cartographer**（米黄+黑+黄，editorial 编辑感）
- 完整设计系统 → [references/style-cartographer.md](references/style-cartographer.md)
- 工作模板 → [references/cartographer-template/](references/cartographer-template/)

内容底线：**有干货**——每页必须有读者能带走的具体信息（数字/方法/结论），不堆砌空话

## 高风险操作黑名单

| 禁止操作 | 危害 | 替代方案 |
|---------|------|---------|
| 图片和文字内容重复表达 | 浪费读者注意力，图文1+1<1 | 图给数据/结构/对比，文给解读/钩子/引导 |
| 单页塞多个主题 | 信息过载，读者记不住任何一点 | 一页 = 一个信息点，宁可多一页 |
| 封面没有「点击理由」 | 0.1秒划走，前功尽弃 | 数字/悬念/利益点三者至少有其一 |
| 结尾没有行动引导 | 读者看完就关，无转化无传播 | 收藏/转发/评论，给读者一个下一步 |
| 用「在当今」「众所周知」等 AI 腔开头 | 信任瞬间归零 | 从具体数字、反常识、痛点场景切入 |
| 用非标准字体 | 微信不渲染自定义字体 → 排版崩坏 | 系统内置字体 → 文字转 PNG 锁定 |

## 编码规则

### 规则 0：数据先行，官方源校验（出图前强制门禁）

**任何包含数据/数字/价格/评测结果的图片，出图前必须完成以下校验，禁止凭记忆或二手搜索结果直接出图。**

- **数据源优先级**：官方博客 > 官方文档 > 一手评测论文 > 权威媒体。搜索引擎聚合结果仅作线索，不可直接引用
- **校验清单**（出图前逐项核对）：
  1. 所有百分比/数字是否有官方源支撑？→ 无源则删，不编
  2. 对比关系（超过/接近/低于）是否正确？→ 对照官方原文逐字确认
  3. 价格/时间/版本号是否精确？→ 从官方定价页/发布公告直接摘取
  4. 是否存在漏缺的关键 benchmark？→ 通读官方源全文，确认无遗漏
- **Prompt 中数字必须逐字指定**：不用「约」「左右」「大概」等模糊词，不用模板变量，每个数字直接硬编码到 prompt 中
- **每张图必须标注数据来源**：底部小字写清 URL，便于追溯和纠正

> **失败机制**：跳过官方源校验 → 数字错误被读者发现 → 信任不可逆崩塌。小绿书传播链长，一张有误的图被截图转发后，更正永远追不上错误扩散。

> **本轮教训**：MiniMax M3 首版轮播图，SWE-Bench Pro 写成 72%（实际 59.0%），漏掉了 Claw-Eval / SVG-Bench / OmniDocBench 等 5 个关键 benchmark，开源状态误标为「已开源」（实际为 10 天内开源）。根源：用了二手搜索结果而非官方博客。

### 规则 1：每页一个信息原子，≤ 6 张，视觉占比 ≥30%

每张卡片必须有一个核心信息点（数字/结论/对比），在画面中占据至少 30% 面积。全篇不超过 6 张（含封面）。

- **字号标准**：主信息 48-72px（`HarmonyOS Sans SC Heavy`），正文 ≥ 16px
- **尺寸标准**：统一 1080×1440px（3:4），JPEG quality 85%，≤ 2MB
- **数量上限**：≤ 6 张（含封面）。超过就砍——多一页不如少一页，读者滑动耐力有限
- **留白原则**：文字区域 ≤40% 画面，留白 ≥30%
- **生成工具**：[`scripts/gen_media.sh`](scripts/gen_media.sh)（统一入口：图像/视频/编辑/多模型）
  - `gen_media.sh generate --prompt "..." --out path.png [--model gpt-image-2] [--style default] [--size 1024x1024]`
  - `gen_media.sh edit --prompt "..." --image src.png --out path.png` (gpt-image-2 / gemini-*)
  - `gen_media.sh video --prompt "..." --out path.mp4 --model doubao-seedance-2.0-fast`
  - `gen_media.sh models` 列出所有支持的模型 + 价格 + 所在 group
  - 风格预设 `default`（浅色知识漫画）| `tech-dark`（深色科技风）| `tech-light`（浅色架构风）| **`cartographer`（米黄+黑+黄知识图解，2026-06-19 新增）**— 在 `scripts/styles/` 下增删 `.txt` 即可
  - 默认 1024×1024，公众号配图自动压到 1MB 以下
  - 旧 `gen_image.sh` 保留为 wrapper，向后兼容
  - **凭据**：`~/.openclaw/provider-auth.json` → `tokenrouter.api_key`（支持 `TOKENROUTER_API_KEY` / `OPENAI_API_KEY` 环境变量覆盖）
  - **长图文（6-12 页）走 HTML+Playwright 管线**而非 AI 生图 → 详见 [references/style-cartographer.md](references/style-cartographer.md) "两种出图方式" 章节

> **失败机制**：字号 < 24px → 手机 375px 宽屏幕不可读 → 读者直接划走 → 完读率 < 15%。设计时必须用 375px 等效宽度模拟校验。

### 规则 2：钩子前置，前 3 句决定停留率

每页配文第一句必须是钩子。正文 50-200 字，每句 ≤ 25 字。

- **钩子类型**：具体数字（「73%」）、反常识（「你以为…其实…」）、痛点共鸣（「我也踩过这个坑」）
- **结构模板**：钩子句 → 展开句 → 结论/引导句
- **避免句式**：「在当今」「众所周知」「随着XX的发展」——这些是 AI 腔第一诊断信号
- **干货检验**：每页结束，读者能不能说出「这一页教会我什么」？说不出来 = 这页是空话，删

> **失败机制**：开头泛泛而谈 → 触发读者「这条没信息量」的潜意识判断 → 100ms 内划走 → 整篇白做。用「遮掉第一句」测试：从第二句开始读仍然成立，第一句就是废话。

### 规则 3：Prompt 一致性 + 统一配色，全篇一家人

同一篇小绿书所有页面必须同底色、同字体族、同排版架构，且**共用一套 Prompt 体系**。

- **Prompt 一致性**：先写一个 `base_prompt`（含风格+配色+字体+布局+分辨率），每页只替换 `content_block` 字段。**禁止每页重写全新 Prompt**——这是风格断裂的头号原因
- **配色上限**：主色系 1-2 个 + 强调色 1 个
- **预置方案**：6 套（暖橘/深海蓝/森林绿/薰衣草/极简黑白/AI科技蓝紫）→ `references/design-system.md`
- **科技类专用**：`#4F6BFF → #8B5CFF` 渐变 + 3D Isometric 插画 → `references/style-ai-tech.md`
- **出图流程**：`base_prompt` 只写一次 → 每页替换 `content_block` → 逐张调 `gen_media.sh generate --style default`

> **失败机制**：Prompt 不一致或换配色 → 视觉碎片化 → 读者以为内容是从不同来源拼凑的 → 品牌感崩塌、信任归零。统一不是审美偏好，是信任基础设施。

### 规则 4：Prompt 严守原意，wrapper 不"美化"（2026-06-17 新增）

**Prompt 是用户的资产,wrapper 是调用的脚手架。** wrapper 的职责是"忠实搬运 + 处理故障",不是"改写成更漂亮的样子"。

- 用户给的是 prompt → 走 `--prompt` 直传,**一字不动**传给模型
- 用户给的是素材(文章/主题/方向) → 走 `--from-article` 翻译,且 `--image-desc` 必须由用户写,不能 wrapper 补
- 严禁在 `--prompt` 和 `--from-article` 之间"智能选择"或合并
- 故障降级(PIL 兜底)时,产物严守"最小可用"原则:深色背景 + 主副标题 + 关键词高亮,不要为了"显得不土"加额外装饰
- 详细决策表 + 实战案例 → [references/prompt-philosophy.md](references/prompt-philosophy.md)

> **失败机制**：wrapper 替用户"美化" prompt → 用户的精心设计被 LLM 改坏 → 风格断裂 / 数据失真 / 信任崩塌;故障降级时伪装"AI 产物" → 读者识破后反感更深。

## 失败机制速查

| 失败模式 | 触发条件 | 根因 | 症状 | 修复动作 |
|---------|---------|------|------|---------|
| 图片上传被拒 | 文件 > 2MB | 微信公众平台素材库上传限制 | 后台 toast：「文件大小不能超过 2M」 | `convert -quality 85%` JPEG 压缩，或 `pngquant` 减色 |
| 手机阅读不可用 | 字号 < 24px（PC 预览误判） | 分辨率换算错误 | 文字模糊如蚂蚁，完读率暴跌 | 缩小到 375px 宽目测检查 |
| 封面文字被裁切 | 图片比例 ≠ 3:4 | 微信封面自动居中裁剪 | 标题上半段或下半段消失 | 封面必须 1080×1440，标题居中占 30%-60% |
| AI 腔劝退读者 | 使用论文/官文模板句式 | 模型偏好安全表达 | 完读率 < 20%，0 分享 | 每页首句替换为数字/反问/痛点/例子 |
| 图文割裂 | 图说 A，文说 B | 图文分开构思 | 读者困惑「这两页有关吗」 | 先写文案骨架，再定每页视觉；正文首句呼应核心视觉 |
| 风格断裂 | 每页重写全新 Prompt | 忽略了 Prompt 一致性 | 同一篇看起来像不同人做的 | 固定 `base_prompt`，只替换 `content_block` |
| 页数过多读者疲劳 | 超过 6 张 | 不舍得砍信息 | 完读率断崖下跌，后几页白做 | 砍到 ≤ 6 张，把最弱的两页信息合并或删除 |
| 数据错误 | 跳过官方源校验，用二手数据 | 省时间、信任搜索引擎聚合 | 读者截图转发 → 错误扩散不可逆 | 规则 0 强制门禁：逐项核对官方源后再出图 |

## SOP

### 规格 1：小绿书图文消息（≤6 页）

1. **选类型** — 从 5 种结构（清单/步骤/对比/反常识/地图）中确定一种 → 参考 `references/copy-templates.md`
2. **拆卡片** — 拆为 4-5 个信息原子（封面 + 3-4 内页 = ≤ 6 张），每卡含「核心视觉元素 + 50-200 字配文」
3. **写 base_prompt** — 固定风格/配色/字体/布局，只留 `content_block` 为变量 → `references/design-system.md` / `style-ai-tech.md`
4. **生图** — 逐张调 `gen_media.sh generate --style default`，每张只改 `content_block`，保持其余 Prompt 完全一致
5. **验证发布** — 手机端预览 → 通过检查清单 → 公众号后台「图片/文字」→ 发布

### 规格 2：长图文知识图解（6-12 页，cartographer 风格）

1. **确定章节骨架** — 用 12 页标准结构（封面 / 痛点 / 定义 / 价值 / 步骤 / 代码 / 工具 / 路由 / 对比 / 成本 / FAQ / 收束）→ `references/style-cartographer.md` "12 页结构" 章节
2. **写 HTML** — 复制 `references/cartographer-template/` 项目作为起点，改 `index.html` 内容，保持 `css/styles.css` 不动
3. **截图** — `python3 _shoot.py` 生成 12 张 1080×1440 PNG 到 `screenshots/`
4. **部署公网** — cp 到 1Panel 静态站 + chown + curl 验 200
5. **发送** — 用公网 URL 形式发到 QQ / 微信（base64 上传会被 QQ 服务端拒）→ MEMORY.md "QQ Bot `<qqimg>` 发送图片踩坑" 章节

## 验证

- [ ] 全篇 ≤ 6 张（含封面）
- [ ] **所有数据已通过规则 0 官方源校验**（数字/价格/百分比/版本号均有官方源支撑）
- [ ] 每张图底部标注数据来源 URL
- [ ] 所有图片 1080×1440px，≤ 2MB
- [ ] 封面标题占画面 30%-60%，375px 宽可读
- [ ] 每页只有 1 个核心信息点
- [ ] 每页首句钩子测试通过（遮掉后无影响 = 不合格）
- [ ] 每页有干货（读完能说出「这页教会我什么」）
- [ ] 所有图片共用同一 `base_prompt`，无 Prompt 漂移
- [ ] 配色全程统一（跨页对比底色/字体/布局一致）
- [ ] 结尾有明确行动引导
- [ ] emoji ≤ 2 个/页，无 AI 腔模板句

## 产出物

| 产出 | 规格 | 数量 |
|------|------|------|
| 封面图 | 1080×1440px PNG/JPG，≤2MB | 1 |
| 内页图 | 1080×1440px PNG/JPG，≤2MB | 3-5 |
| 配文 | 50-200 字/条 | 与图片数量一致 |
| 发布草稿 | 微信公众平台后台 | 1 |

---

## 资源索引

- 设计系统：[references/design-system.md](references/design-system.md) — 6 套配色 / 5 种布局 / AI 生图 Prompt 模板
- 文案模板：[references/copy-templates.md](references/copy-templates.md) — 封面公式 / 卡片模板 / 内容框架
- AI 科技风专题：[references/style-ai-tech.md](references/style-ai-tech.md) — 蓝紫渐变完整方案 / OpenClaw 架构专用 Prompt
- **知识图解专题**：[references/style-cartographer.md](references/style-cartographer.md) — 米黄+黑+黄 editorial 风格 / 12 页骨架 / HTML+Playwright 管线（2026-06-19 新增）
- **知识图解模板**：[references/cartographer-template/](references/cartographer-template/) — openrouter-cartographer 完整 12 页 HTML 项目（开箱即用）
- **Prompt 哲学**：[references/prompt-philosophy.md](references/prompt-philosophy.md) — 严守原意 vs 走 LLM 美化的决策表(2026-06-17 新增)
- Skill 设计规约：[references/skill-design-spec.md](references/skill-design-spec.md) — 复旦-微软论文三维质量标准
- 生图脚本：[scripts/gen_media.sh](scripts/gen_media.sh) — 多模型 + 图像/视频/编辑，`--model gpt-image-2|gemini-*|doubao-seedance-*`
- 兼容 wrapper：[scripts/gen_image.sh](scripts/gen_image.sh) — 老调用方式不破坏
- 风格预设：[scripts/styles/](scripts/styles/) — `default.txt`（知识漫画）/ `tech-dark.txt` / `tech-light.txt` / **`cartographer.txt`（米黄+黑+黄知识图解，2026-06-19 新增）**
- 发布脚本：[scripts/publish.sh](scripts/publish.sh)
