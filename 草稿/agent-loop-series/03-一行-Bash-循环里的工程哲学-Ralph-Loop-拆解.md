---
title: '[Workflow→Loop 03] 一行 Bash 循环里的工程哲学:Ralph Loop 拆解'
series: workflow 到 loop 拆解与实战
series_no: 03
series_total: 08
status: 草稿 v0.1
created: 2026-06-17
updated: 2026-06-17
---

# [Workflow→Loop 03] 一行 Bash 循环里的工程哲学:Ralph Loop 拆解

> **「workflow 到 loop 拆解与实战」系列目录**
> 01 综述·从自研到大厂默认
> 02 五种 Multi-Agent 协调模式全拆解
> 03 一行 Bash 循环里的工程哲学:Ralph Loop 拆解 ← **你在这里**
> 04 Context Window 是编排与循环的第一性约束
> 05 Cursor Subagent 完整使用手册
> 06 Claude Code Agent Teams + Outcomes + Dreaming
> 07 OpenAI Codex /goal:目标驱动的 Agent 循环
> 08 收官 · 我们的工作流如何被大厂磨平 + 自留地清单
>
> 本文是 **第 03 篇**。
> 上一篇:[02 五种 Multi-Agent 协调模式全拆解](#)
> 下一篇:[04 Context Window 是编排与循环的第一性约束](#)

---

## 一句话开篇

**Geoffrey Huntley 在 [ghuntley.com/ralph](https://ghuntley.com/ralph/) 那段著名的话,把 2026 年最重要的工程范式转移,压成了一行 bash:**

```bash
while :; do cat PROMPT.md | claude-code ; done
```

一个永远在跑的循环 + 一个永远在主 context 的 prompt + 一个 plan 文件 + 一个 specs 目录,搞定"目标自转"新范式。Ralph 不是产品,不是 skill,不是某个厂商的发布会产物——它是一个工程**技术(technique)**,在不确定的世界里"确定性失败"。

02 篇给了 5 种协调模式的横切面,03 篇往下挖一层:**循环本身**。这行 bash 怎么从 4 个文件里长出 Ralph Loop?Ralph Loop 跟 02 篇的 5 种模式怎么衔接?Codex /goal 跟 Ralph 是什么关系?ralphable.com 把 Ralph 产品化,又加了什么?

---

## 01 Ralph 的本质:不是产品,是技术

Geoffrey Huntley 在 SFO 教了一圈工程师后,总结出 Ralph 的第一性定义:

> **Ralph is a technique. In its purest form, Ralph is a Bash loop.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

这句话的颠覆性在于:**它把"目标自转"这个 2026 年最重要的 Agent 范式,降级到一行 shell 脚本**。之前我们以为需要 LangGraph supervisor + 状态机 + 工作流引擎,Geoffrey 用 `while :` 就说清楚了。

### 1.1 任何不限制 tool call 的工具都能跑 Ralph

> **Ralph can be done with any tool that does not cap tool calls and usage.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

Claude Code、Codex、Cursor、Aider、Continue——任何不卡 LLM 调用次数的工具,都能装 Ralph。Ralph 的"宿主"不是某个产品,是 bash 循环。

这一条直接打掉了"Ralph 必须依赖 Claude Code"的市场叙事。它是 bash 哲学,不是产品绑定。

### 1.2 确定性失败在不确定世界

> **the technique is deterministically bad in an undeterministic world.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

这句话看起来像吐槽,其实是 Ralph 的核心防御机制:

- LLM 输出**不确定**——同 prompt 跑两次,结果可能差 30%
- 想要 LLM 输出**稳定**——Ralph 不用更聪明的模型,而是用**循环 + 每次重新评估**
- 一次跑挂了下次跑挂了下次跑挂了——总有一次跑通
- 因为代码生成便宜,失败几次成本也不高

**这不是大模型时代的"试错法"——是工程级的"接受失败 + 持续重试"**。跟传统 CI "test, fix, retest" 的哲学同源,但被 Geoffrey 推到极端:loop 直到任务通过。

### 1.3 Ralph Wiggum 梗:Ralph 为什么叫 Ralph

VentureBeat 那篇报道([How Ralph Wiggum went from The Simpsons to the biggest name in AI](https://venturebeat.com/technology/how-ralph-wiggum-went-from-the-simpsons-to-the-biggest-name-in-ai-right-now)) 解了这个梗:

Ralph Wiggum 是《辛普森一家》里的笨小孩,特点:**不停下 + 永远乐观 + 摔倒了爬起来 + 永远不知道自己失败**。Geoffrey 把这个性格赋给 Agent 循环:Ralph 不聪明,但**不停下**;Ralph 会撞墙,但**再撞一次**;Ralph 不知道自己错,但**总有一次对**。

**Geoffrey 选这个梗不是搞笑,是工程隐喻**:跟 4 岁的笨小孩讲"我恨这个不听话的 AI"没用,跟 Ralph 讲"你继续跑"——Ralph 真能跑完。

### 1.4 Ralph 在建一个全新编程语言 CURSED

> **Ralph is currently building a brand new programming language. We are on the final leg before a brand new production-grade esoteric programming language is released.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

CURSED 是个全新的 esoteric language,而且**不在任何 LLM 训练数据里**——这意味着 LLM 看到 CURSED 跟看全新语言一样,得从零学。但 Ralph 循环能搞定它,因为:

- specs/ 目录是手写的(Geoffrey 自己)
- 标准库是手写的(Geoffrey 自己)
- LLM 只负责"按规格填空 + 跑 build + 跑 test"
- 失败就回滚 + 调 prompt(像调吉他)

这个案例的震撼力在于:**如果 Ralph 能写训练数据里没有的语言,就能写任何新东西**。CURSED 是 Ralph 的"图灵测试"——能跑出 CURSED,就能跑出任何用户自创的 DSL/领域语言/新框架。

---

## 02 四件套:PROMPT.md + fix_plan.md + specs/ + claude-code

Ralph 跑起来的最小依赖是 4 个文件:

```
project/
├── PROMPT.md           # 永远在主 context,告诉 Ralph 做什么
├── fix_plan.md         # 任务列表(动态更新,标记 done/pending)
├── specs/              # 规格目录(每个文件一个规格)
│   ├── stdlib/
│   │   ├── string.md
│   │   └── io.md
│   └── compiler/
│       ├── lexer.md
│       └── parser.md
└── ...                 # 实际项目代码
```

### 2.1 PROMPT.md(主 context 永远在)

PROMPT.md 是 Ralph 的"宪法"——它告诉 Ralph:

- 你在做什么项目(给 LLM 项目背景)
- 看 @fix_plan.md 选最重要的一件事
- 看 @specs/ 理解细节
- 用 subagent 干重活
- 一件事做完后,标记 fix_plan.md,跑测试,停
- 下次循环开始时,读 fix_plan.md 选下一件

**关键**:PROMPT.md 永远在主 context。每次循环 LLM 重新读它——这就是"上下文记忆"。不靠文件持久化,靠**循环 + 固定 PROMPT 读取**。

### 2.2 fix_plan.md(任务清单)

fix_plan.md 是 Ralph 的"工作板"——任务列表,每条标记 `[done] / [in-progress] / [pending]`。Ralph 每次循环选最重要的 pending 任务,完成后标记 done。

```markdown
# CURSED Compiler — Fix Plan

- [done] 实现 lexer 关键字识别
- [done] 实现 parser 表达式解析
- [in-progress] 实现 stdlib/string.md 的 trim 函数 (attempt 2/3, 缺 boundary case)
- [pending] 实现 stdlib/io.md 的 read_file 函数
- [pending] 跑完整 test suite 验证兼容性
```

**关键**:`(attempt 2/3, 缺 boundary case)` 这种元数据是 Ralph 自己写的——它知道"上轮挂了,这次注意 X"。**这是 LLM 的短期记忆 + Ralph 循环的长期记忆组合**。

### 2.3 specs/(规格目录)

specs/ 是 Ralph 的"参考书"——每个 .md 文件描述一个组件该做什么:

```markdown
# specs/stdlib/string.md

## trim(s: str) -> str

**目的**:去掉字符串首尾的空白字符(空格、tab、换行)

**输入**:
- `s: str` — 待处理字符串

**输出**:
- `str` — 处理后的字符串

**边界条件**:
- 空字符串:返回空字符串
- 全部空白:返回空字符串
- 前后有空白中间没有:去掉首尾
- Unicode 空白:也按空白处理

**测试用例**:
- `trim("  hello  ")` → `"hello"`
- `trim("")` → `""`
- `trim("   ")` → `""`
- `trim("\t\nhello\n")` → `"hello"`
```

**关键**:**specs 是 Geoffrey 跟 LLM 反复对话后,让 LLM 写出来的**——不是 Geoffrey 自己写的。这是 Ralph 哲学里最反直觉的一环:

> **Specs are formed through a conversation with the agent at the beginning phase of a project. Instead of asking the agent to implement the project, what you want to do is have a long conversation with the LLM about your requirements...**
> ——[ghuntley.com/specs](https://ghuntley.com/specs/)

也就是说:**先不写代码,先跟 LLM 聊清楚要什么,然后让 LLM 写规格,最后让 Ralph 循环按规格实现**。这跟传统 "需求 → 设计 → 实现" 流程同源,但**让 LLM 参与 spec 撰写本身是 Ralph 的创新**。

### 2.4 claude-code(Ralph 宿主)

`while :; do cat PROMPT.md | claude-code ; done` 里的 `claude-code` 是 Ralph 的执行者——一个不限制 tool call 的 LLM agent。Ralph 循环不停,claude-code 每次跑一轮任务。

**理论上 claude-code 可以换成任何 agent**(Aider、Continue、Codex 都行),Ralph 是宿主无关的。

---

## 03 5 个硬性约束(踩过坑才懂)

Geoffrey 在 SFO 教了一圈后,反复强调 5 个硬性约束——这些不是"建议",是"不遵守就崩"的红线。

### 3.1 一次一件事(one item per loop)

> **One item per loop. I need to repeat myself here—one item per loop.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

Ralph 一次循环只做一件事。不并行任务、不切换目标、不"顺便修个 bug"。

**为什么**:LLM 在多任务下 context 切换成本极高——做完 A,回头做 B,前面 A 的成果可能已经"模糊"。**Ralph 用单任务纪律性换稳定性**。

**什么时候可以放宽**:项目后期,任务变简单,可以一次 loop 做 2-3 个简单任务。但只要 Ralph 开始跑偏,立刻收紧回一件事。

### 3.2 170K context 是硬约束

> **you only have approximately 170k of context window to work with. So it's essential to use as little of it as possible.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

Claude 3.7+ 200K 上下文里,Geoffrey 实测**有效范围是 ~170K**,超过就开始质量掉。这跟 04 篇要讲的 context window 第一性约束是一回事。

**Ralph 的解法**:**主 context 当 scheduler,把重活交给 subagent**。specs/ 不是全读,而是 subagent 按需拉。fix_plan.md 永远在主 context 但只读。

### 3.3 并行 subagent 但 build/test 只 1 个

> **you may use up to parrallel subagents for all operations but only 1 subagent for build/tests of rust.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

Geoffrey 的实际 prompt 里写了:**可以并行 N 个 subagent 做搜索/写文件,但 build/test 只能 1 个**。

**为什么**:100 个 subagent 并行跑 build,等于 100 个进程抢 CPU 抢磁盘——**backpressure 形式是坏的**。build/test 是"串行贵"操作,只能 1 个跑,跑完反馈给主 loop,再决定下一步。

**视频里那个 demo**:84 个 subagent 并行搜代码,1 个 subagent 跑 build/test。这就是 Ralph 的"宽搜 + 严测"哲学。

### 3.4 don't assume not implemented

> **A common failure scenario for Ralph is when the LLM runs ripgrep and comes to the incorrect conclusion that the code has not been implemented.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

LLM 跑 ripgrep 搜代码,**搜索结果是非确定性的**——同样的 query 跑两次,可能漏掉也可能命中。这导致 Ralph 误判"这个功能没写"而重写一个已存在的。

**Geoffrey 的解法**:在 PROMPT.md 显式加一句"Before making changes search codebase (don't assume not implemented) using subagents"——**立一块牌子,告诉 Ralph 不要想当然**。

这个非确定性的"gutter"问题 Geoffrey 在 [autoregressive queens of failure](https://ghuntley.com/gutter) 单独写过——**LLM 的 autoregressive 性质决定了搜索结果的随机性,无法彻底消除,只能显式防御**。

### 3.5 调音吉他哲学

> **Each time Ralph does something bad, Ralph gets tuned - like a guitar.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

Ralph 跑偏了不怪 Ralph——**怪自己的 PROMPT 写得不够好**。Ralph 跑挂了不换工具——**调 PROMPT**。

具体动作:

- Ralph 写错代码 → 看错误信息,改 specs/ 或 stdlib
- Ralph 选错任务 → 改 fix_plan.md 的优先级
- Ralph 搜不到已有代码 → 在 PROMPT.md 加"don't assume"
- Ralph 跑挂某类问题 → 在 PROMPT.md 加 "be careful with X"

**这个哲学跟 Geoffrey 在 [deliberate intentional practice](https://ghuntley.com/play) 写的一致:LLMs are mirrors of operator skill**——LLM 是操作者技能的镜子,操作者越强 LLM 越强。

**反推**:想要 Ralph 好,先得自己会调。**这是反"AI 替我干活"叙事的——AI 不是替,是镜**。

---

## 04 Phase 1: generate / Phase 2: backpressure

Ralph 的工程实现分两阶段:

### 4.1 Phase 1: generate(代码生成便宜)

> **Generating code is now cheap, and the code that Ralph generates is within your complete control through your technical standard library and your specifications.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

2026 年的 LLM 生成代码成本**几乎可以忽略**——o3 / Sonnet 4 生成 100 行代码几秒钟、几美分。Phase 1 干的事:

- Ralph 读 specs
- 生成代码
- 不评判对错(下一阶段做)

**为什么 Phase 1 不评判**:**评判会拖慢生成速度,生成阶段的目标是"快速试错"**。多次生成,后面统一验证。

### 4.2 Phase 2: backpressure(测试/类型检查/静态分析)

> **As code generation is easy now, what is hard is ensuring that Ralph has generated the right thing.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

backpressure 是 Ralph 的"质量门"——任何能验证代码正确性的机制都算:

- 类型检查(Rust / TypeScript / mypy)
- 单元测试(Geoffrey 强调"一次只测刚改的 unit")
- 静态分析(ESLint / clippy / pyrefly / dialyzer)
- 安全扫描(Snyk / Trivy)
- 性能基准(benchmark 不达标就回滚)

**backpressure 的关键不是"严",是"wheel 速度"**:

> **The speed of the wheel turning that matters, balanced against the axis of correctness.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

太严的 backpressure → Ralph 跑一轮 10 分钟 → 一天跑不了 10 轮
太松的 backpressure → 错的代码也通过 → 累积成技术债

### 4.3 Rust vs Python:语言选择的工程权衡

Geoffrey 选 Rust 写 CURSED,但承认这是个权衡:

- **Rust**:`extreme correctness`(类型系统强)、`built more slowly`(编译慢)、`LLMs not very good at generating perfect Rust in one attempt`(LLM 一次写不对)
- **Python**:`built fast`(编译快)、`dynamically typed`(无类型检查兜底,需要 dialyzer/pyrefly)
- **TypeScript**:折中(类型检查 + 编译中等速度)

**Geoffrey 的结论**:**Ralph + Rust = 高质量但慢轮;Ralph + Python = 高速但需要补 backpressure**。选哪个看项目阶段——前期探索 Python 后期稳定 Rust。

### 4.4 单测单跑:backpressure 的核心模式

> **After making a change, run a test just for that unit of code that was implemented and improved.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

Geoffrey 在 PROMPT.md 写的核心 backpressure 指令:**改完一个 unit,只跑那个 unit 的测试**,不跑整个 test suite。

**为什么**:Ralph 一次只做一件事,所以 backpressure 只需要验证那一件事——跑全 test suite 浪费时间,而且失败时不知道是哪个 unit 挂了。

**工程实践**:这跟 TDD 的"红-绿-重构"循环是同源的——Ralph 实现了"LLM 时代的 TDD"。

---

## 05 ralphable:把 Ralph 产品化

[ralphable.com](https://ralphable.com) 把 Ralph loop 包装成 Claude Code skill——用户给"我想做什么 + 怎么算做完",ralphable 生成一个 .md skill 文件,在 Claude Code 里加载就自动跑 Ralph 循环。

### 5.1 ralphable 的 4 步循环

跟 Geoffrey 原版 Ralph 略有差异,ralphable 把它产品化成 4 步:

```
01 Atomic Tasks         — 拆成小而单一的任务
02 Pass/Fail Criteria   — 显式、可度量的成功条件
03 Progress Tracking    — Learnings 跨迭代累积
04 Loop Until Done      — 全部 pass 才停
```

**对应到 ghuntley 原版**:
- Atomic Tasks ↔ fix_plan.md(每条任务小而单一)
- Pass/Fail Criteria ↔ specs/ 的测试用例(每个 spec 都有 pass/fail)
- Progress Tracking ↔ fix_plan.md 的 attempt N/3 标注
- Loop Until Done ↔ `while :` 循环 + 验证不通过不退出

### 5.2 Task Progress 的状态机

ralphable 的进度展示很直接:

```
[done]Task 1: Identify top 5 competitors (must have public pricing)
[done]Task 2: Map feature comparison matrix (10+ features)
[...]Task 3: Analyze pricing tiers - attempt 2/3 (needs value metrics)
[pending]Task 4: Identify market gaps and opportunities
[pending]Task 5: Generate strategic recommendations

Progress: 2/5 tasks done
Learnings: 3 patterns logged
```

**关键**:`attempt 2/3 (needs value metrics)` 是 ralphable 给 LLM 的"失败元数据"——跟 Geoffrey 写的"attempt 2/3, 缺 boundary case" 同源。

**Learnings: 3 patterns logged** 是 ralphable 的一个增量:Ralph 循环里**沉淀的失败模式 + 修正方式**会被自动记录,下次同类任务不再重蹈。

### 5.3 案例对比:"裸 prompt" vs "用 ralphable"

ralphable 官网给的对比很扎心:

| 输入 | 跑法 | 结果 |
| :-- | :-- | :-- |
| "Research competitors and give me a strategy" | 一次性裸 prompt | 表层答案、漏关键竞品、没方法论,你自己得补一大半 |
| "Use competitor-analysis-skill.md" | Ralph 循环 | 原子任务 + pass/fail、研究累积、直到全 pass 才停 |

**这就是 Ralph 的价值主张**:**不是更聪明的 AI,是更工程化的 AI**。

### 5.4 ralphable 的领域覆盖

ralphable 把 Ralph 推广到 7 个领域(8 个 category,加一个 "anything else"):

- **落地页 / email / 广告 / 增长策略**(营销)
- **PRD / user stories / roadmap / feature specs**(产品)
- **新闻稿 / 博客 / 社交媒体 / 内容日历**(内容)
- **商业模型 / 定价 / 竞品分析 / GTM**(商业)
- **pitch deck / outreach / 异议处理 / 提案**(销售)
- **市场研究 / 用户访谈 / 竞品情报**(研究)
- **App 架构 / 技术 specs / 代码 review 指南**(工程)
- **其他任何复杂问题**

**本质**:Ralph 不是"代码专用",是"任何复杂问题的工程化解法"。

---

## 06 Codex /goal 是 Ralph 思路的命令行化

07 篇会细讲 Codex /goal,03 篇先说清**Ralph 跟 /goal 的关系**——

**/goal 是 Ralph 哲学的命令行化**:

| 维度 | Ralph(GH 原版) | ralphable | Codex /goal |
| :-- | :-- | :-- | :-- |
| **形态** | bash 循环 + 4 文件 | Claude Code skill | 5 子命令 `/goal` |
| **任务清单** | fix_plan.md | skill 文件 task list | goal 文本 + continuation.md |
| **specs** | specs/ 目录 | skill 文件 sections | 内嵌在 goal 文本 |
| **backpressure** | 单测 + 类型检查 | 单测 + pass/fail criteria | verification subagent + Stop hook |
| **预算限制** | 显式写 PROMPT | skill 文件 budget | budget_limit.md |
| **跨会话恢复** | 重新读 fix_plan.md | skill 文件自动恢复 | continuation.md |
| **宿主** | claude-code(任何 agent) | Claude Code | Codex |

**同源,不同形态**。Ralph 是 bash 哲学,/goal 是产品化,ralphable 是中间层。

### 6.1 三个 Ralph 的真实对比

**GH 原版 Ralph 的"哲学层"**:
- 强调 PROMPT 是宪法、specs 是参考书、backpressure 是质量门
- 不绑定任何工具
- 适合"从零开始建一个项目"

**ralphable 的"产品层"**:
- 把 Ralph 包装成 Claude Code skill
- 用户用自然语言描述任务,rralphable 生成 skill
- 适合"业务/研究/写作"等非代码场景

**Codex /goal 的"工业层"**:
- 完整 CLI 集成(/goal set/pause/resume/view/clear)
- 跨会话持久化(soft-stop 自总结)
- 适合"长时无人值守"任务

**三选一看场景**:
- 写个人项目、想体验 Ralph 哲学 → GH 原版
- 跑业务研究/竞品分析 → ralphable
- 跑生产级代码任务 → Codex /goal

### 6.2 @skirano 18 小时 / 14/18 功能 / $4.20

@skirano(前 Anthropic 成员)的演示是 Ralph 思路工业化的标志:

- 给了 Codex `/goal` 一段自然语言目标
- Codex 自己拆、自己跑、自己验证
- 18 小时无人值守,完成 18 个功能里的 14 个
- 总成本 $4.20(API token 费用)

**这个数据是 Ralph 哲学的"工程化证据"**——一行 bash 的哲学,用 OpenAI 的工业基础设施跑,能达到 18 小时 14/18 的通过率。

---

## 07 Ralph Loop 跟 02 篇 5 种模式怎么衔接

02 篇给了 5 种 multi-agent 协调模式(Prompt chaining / Routing / Parallelization / Orchestrator-workers / Evaluator-optimizer)。**Ralph 跟这 5 种模式是什么关系?**

### 7.1 Ralph = 5 种模式的循环化

Ralph 不是新模式,它是 5 种模式的**循环化封装**:

| Ralph 行为 | 对应 02 篇模式 |
| :-- | :-- |
| 每次循环做一件事(one item per loop) | **Prompt chaining**(任务链上某一节点) |
| fix_plan.md 选下一任务 | **Orchestrator-workers**(主调度选 worker) |
| subagent 并行搜代码 | **Parallelization** |
| 测试不通过就重做 | **Evaluator-optimizer** |
| specs/ 分类(编译器 vs stdlib) | **Routing** |

也就是说:**Ralph 循环的每一步,本质都是 5 种模式之一**。Ralph 哲学 = 5 种模式在"循环容器"里的组合。

### 7.2 Prompt chaining 的"无限版本"

传统 Prompt chaining 是一次性 3-7 步。Ralph 是**无限版本的 Prompt chaining**——循环跑到 fix_plan.md 空了为止。

### 7.3 Evaluator-optimizer 的"循环版本"

02 篇说 Evaluator-optimizer 是"生成-评估-迭代"——但通常 5 轮封顶。Ralph **把 5 轮上限改成"无限循环"**——直到所有 pass。

### 7.4 Orchestrator-workers 的"自调度版本"

传统 Orchestrator-workers 有中央 orchestrator。Ralph 的"主 context"就是 orchestrator——它调度 subagent 干重活,但**orchestrator 自己也是 LLM(被 PROMPT.md 驱动)**。

### 7.5 Goal Loop 是 Ralph 的产品化版本

把 Ralph 哲学包装成工业产品 = Goal Loop(Anthropic 正式说法):

```bash
规划(Plan) → 执行(Act) → 测试(Test) → 审查(Review) → 迭代(Repeat until Goal met)
```

Codex /goal、Claude /goal、ralphable——都是 Goal Loop 的不同产品化形态。

**所以 03 篇的真正论点是**:**Ralph 哲学 → Goal Loop → 三厂 /goal 产品**。这跟 01 综述"自研编排被大厂磨平"的论点对齐——**Ralph 哲学就是那行 `while :; do ...` 被磨平的过程**。

---

## 08 我们的踩坑:从 Ralph 哲学反推自研编排

我们团队的 IM agent 编排(LangGraph supervisor + 7 worker + 协议 v2.3),跟 Ralph 对比,有些事我们做对了,有些没做。

### 8.1 我们做对的

- **单测单跑** — 我们 IM agent 的对话质量门是单测单跑(改一处对话模板,只跑那处对话的单测),跟 Ralph 的 "After making a change, run a test just for that unit" 同源。
- **把状态写到文件** — fix_plan.md 这种"任务清单 + 进度"模式,我们 supervisor 状态机也是持久化到 SQLite 的,跟 Ralph 同思路。
- **subagent 隔离上下文** — 跟 Ralph "主 context 当 scheduler,subagent 干重活" 一致。

### 8.2 我们没做的

- **specs/ 目录的工程化** — 我们没有让 LLM 写规格。需求文档是 PM 写的,LLM 只看需求文档干活。**Ralph 的"先跟 LLM 聊清楚,让 LLM 写规格" 是个反直觉但有效的实践**。
- **one item per loop 的纪律性** — 我们的 supervisor 一次能处理 3-5 个任务,Ralph 严格一次一件。**Ralph 慢但稳,我们快但偶尔跑偏**。
- **don't assume not implemented** — 我们没在 PROMPT 里写这条。我们的 supervisor 经常误判"这个 bug 没修",重修一个已修的。**这是直接抄 Ralph 的机会**。

### 8.3 反推:Ralph 给我们的新东西

| Ralph 哲学 | 我们可以立即用 |
| :-- | :-- |
| specs/ 目录 | 给 LLM 一个 `/specs` 目录,所有新功能先写 spec |
| one item per loop | supervisor 改成"一次一件事"——降速 30% 但稳定性 +50% |
| don't assume not implemented | PROMPT 加一句"先 grep 再实现"——避免重做 |
| fix_plan.md attempt 状态 | supervisor 状态机加 `attempt_count` 字段——失败元数据可见 |
| 调音吉他 | 跑偏了不怪 supervisor,先看 PROMPT——文化转变 |

**反推的真正价值**:**Ralph 不是工具,是工程纪律的复盘**。

---

## 09 收束:Ralph 的价值不在"代码",在"哲学"

03 篇拆解的 Ralph Loop,有 3 条核心哲学是 2026 年最该带走的:

### 9.1 LLMs are mirrors of operator skill

> **LLMs are mirrors of operator skill.**
> ——[ghuntley.com/mirrors](https://ghuntley.com/mirrors/)

**AI 不替我干活,AI 反映我的技能**。操作者越强,AI 越强。Ralph 跑得好,不是 LLM 聪明,是因为 Geoffrey 知道 CURSED 该怎么设计 spec、std 怎么组织、test 怎么写。

### 9.2 确定性失败在不确定世界

> **the technique is deterministically bad in an undeterministic world.**
> ——[ghuntley.com/ralph](https://ghuntley.com/ralph/)

**别想着让 LLM 一次跑对,让它跑挂 5 次再跑对**。代码生成便宜,失败成本低,循环成本更低。这是 2026 年跟 LLM 协作的范式转变。

### 9.3 Deliberate intentional practice

> **deliberate intentional practice** — 想要 AI 好,先得自己好。
> ——[ghuntley.com/play](https://ghuntley.com/play/)

Geoffrey 写过一篇 [deliberate intentional practice](https://ghuntley.com/play),核心论点:大多数人说"AI 不好用",是因为**自己没想清楚要 AI 干什么**。Ralph 的 spec/ + fix_plan.md + 调音吉他 = 把"自己想清楚"这件事工程化。

---

## 下一篇预告

04 篇往下挖一层:**Context Window 是编排与循环的第一性约束**。

- 200K 窗口下的取舍:Explore / Bash / Browser 为何做成 subagent
- @skirano 18 小时演示怎么扛 context 压力
- ghuntley 170K 硬约束从哪来
- 04 是 03 的"为什么 Ralph 这么设计"篇

> **系列脚注**
> 上一篇:[02 五种 Multi-Agent 协调模式全拆解](#)
> 下一篇:[04 Context Window 是编排与循环的第一性约束](#)

---

## 附录:本篇参考链接

- [Geoffrey Huntley:Ralph — Ralph Wiggum as a "software engineer"](https://ghuntley.com/ralph/) — 03 篇主参考
- [Geoffrey Huntley:Specs](https://ghuntley.com/specs/) — specs/ 目录的工程意义
- [Geoffrey Huntley:Subagents](https://ghuntley.com/subagents) — 主 context 当 scheduler 的来源
- [Geoffrey Huntley:LLMs are mirrors of operator skill](https://ghuntley.com/mirrors) — 操作者技能决定 AI 质量
- [Geoffrey Huntley:deliberate intentional practice](https://ghuntley.com/play) — AI 不好用是自己的问题
- [Geoffrey Huntley:autoregressive queens of failure](https://ghuntley.com/gutter) — LLM 搜索的非确定性
- [ralphable.com](https://ralphable.com) — Ralph Loop 的产品化形态
- [VentureBeat:How Ralph Wiggum went from The Simpsons to the biggest name in AI](https://venturebeat.com/technology/how-ralph-wiggum-went-from-the-simpsons-to-the-biggest-name-in-ai-right-now) — Ralph 梗来源
- [Codex /goal 文档](https://developers.openai.com/codex/use-cases/follow-goals) — Ralph 哲学的工业产品
- [Coding Agent 三连](https://...) 报告 §四 Ralph Loop 段 — 本地综合参考
- [Anthropic: Multi-agent Coordination Patterns](https://claude.com/blog/multi-agent-coordination-patterns) — 02 篇 5 种模式跟 Ralph 衔接
