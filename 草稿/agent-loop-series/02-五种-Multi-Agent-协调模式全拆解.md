---
title: '[Workflow→Loop 02] 五种 Multi-Agent 协调模式全拆解——从 Anthropic 官博到三厂取舍'
series: workflow 到 loop 拆解与实战
series_no: 02
series_total: 08
status: 草稿 v0.1
created: 2026-06-17
updated: 2026-06-17
---

# [Workflow→Loop 02] 五种 Multi-Agent 协调模式全拆解——从 Anthropic 官博到三厂取舍

> **「workflow 到 loop 拆解与实战」系列目录**
> 01 综述·从自研到大厂默认
> 02 五种 Multi-Agent 协调模式全拆解 ← **你在这里**
> 03 一行 Bash 循环里的工程哲学:Ralph Loop 拆解
> 04 Context Window 是编排与循环的第一性约束
> 05 Cursor Subagent 完整使用手册
> 06 Claude Code Agent Teams + Outcomes + Dreaming
> 07 OpenAI Codex /goal:目标驱动的 Agent 循环
> 08 收官 · 我们的工作流如何被大厂磨平 + 自留地清单
>
> 本文是 **第 02 篇**。
> 上一篇:[01 综述·从自研到大厂默认](#)
> 下一篇:[03 一行 Bash 循环里的工程哲学:Ralph Loop 拆解](#)

---

## 一句话开篇

**01 综述里那张「5 种模式实现成本从 2024 到 2026 断崖式下降」的表,02 篇展开:每种模式给经典实现、对应大厂工具、我们该选它的具体信号。** 这五种不是 Anthropic 创造的,是 LLM 出现之前就存在的工程范式;Anthropic 4/10 那篇[多智能体协调模式博客](https://claude.com/blog/multi-agent-coordination-patterns) 干的事,是给它们一个"LLM 时代的命名 + 边界"。

读懂这五种,你就能看懂三厂(Anthropic / OpenAI / Cursor)为什么对"多智能体编排"给出完全不同的答案——它们其实是在不同场景里选不同模式。

---

## 01 模式总览:为什么是这五种

Anthropic 在 4/10 的官博里,把多智能体协调拆成五种 workflow 模式。这五种覆盖了**所有"多 LLM 协作"的可能**:

| 模式 | 一句话 | 经典类比 |
| :-- | :-- | :-- |
| Prompt chaining | 上一步输出是下一步输入 | Unix 管道 `a | b | c` |
| Routing | 先分类,再分流到专门 prompt | 客服工单系统派单 |
| Parallelization | 同输入多分片,各跑各的,合结果 | Celery / MapReduce |
| Orchestrator-workers | 中央调度,动态拆任务给 worker | 主编给记者派选题 |
| Evaluator-optimizer | 生成-评估-迭代,直到达标 | 编辑-作者校稿循环 |

**为什么不只三种**:任何多 agent 系统,任务粒度、依赖关系、并发度、质量要求,在这五个维度上各选一个位置,就构成了你的系统骨架。

**为什么不是七种**:再往上加,要么是这五种组合(如 Orchestrator + Routing),要么不是"协调模式"而是"架构风格"(如 Hierarchical 是拓扑,不是流程)。06 篇会讲 Agent Teams / Hierarchical / Network 这些"另一套分类"。

---

## 02 Prompt chaining(链式):最朴素也最稳

**核心机制**:把任务拆成有序的 N 步,每步的输出是下步的输入,整条链路上一个 agent。

### 经典实现:LangChain Expression Language(LCEL)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

step1 = ChatPromptTemplate.from_template("把下面这段话改写得更正式:{input}")
step2 = ChatPromptTemplate.from_template("从下面这段话里提取三个关键词:{input}")
step3 = ChatPromptTemplate.from_template("用这三个关键词写一首五言绝句:{input}")

chain = (
    step1
    | ChatOpenAI(model="gpt-4o")
    | StrOutputParser()
    | step2
    | ChatOpenAI(model="gpt-4o")
    | StrOutputParser()
    | step3
    | ChatOpenAI(model="gpt-4o")
    | StrOutputParser()
)

print(chain.invoke({"input": "今天天气不错,适合出门散步"}))
```

**`|`** 就是 chain。每一步的输出直接喂给下一步。

### 三厂对应

- **Claude Code 计划模式**:`Shift+Tab` 进入 plan mode,Claude 自动把任务拆成 3-7 步,逐步执行,每步展示给用户看
- **Codex /goal multi-step**:`/goal` 内置 step progression,每完成一步需要 verification
- **OpenAI 内部:OpenAI Agents SDK 的 handoffs** 本质是链式

### 选它的具体信号

- 每步输出**强依赖**前一步(不能并行)
- 步骤数稳定在 **3-7 步**,超过 7 步说明该拆成 Orchestrator-workers 了
- 错误有明确"在哪一步崩"的诊断,能重试单步

### 我们的踩坑

LangGraph 文档里"为什么 supervisor 比 chain 更通用"那节我们当时没读——把 chain 模式堆到 12 步,中间任何一步 API 限流整条链就卡住。后来才改 supervisor。

---

## 03 Routing(路由):输入分类,分流到专门 prompt

**核心机制**:进来一个输入,先用 classifier 分类(关键词 / 意图 / embedding),根据分类结果路由到对应的专门 prompt 处理。

### 经典实现:客服工单派单 → LLM 时代

LLM 之前的版本:

```python
def route_ticket(ticket):
    category = svm_classifier.predict(ticket.text)  # "billing" / "tech" / "general"
    return handler_table[category](ticket)
```

LLM 时代,把 classifier 换成意图识别 prompt:

```python
def route(user_query: str) -> str:
    intent = llm.invoke(
        f"从下面用户输入里识别意图(账单/技术/其他),只回一个词:{user_query}"
    ).strip()
    handlers = {
        "账单": billing_agent,
        "技术": tech_agent,
        "其他": general_agent,
    }
    return handlers[intent](user_query)
```

### 三厂对应

- **Cursor Subagent 文件**:`.cursor/agents/billing.md`、`tech.md`、`general.md`,frontmatter 里的 `description:` 字段就是"什么场景触发这个 subagent"
- **Claude Code Skills**:跟 Cursor Subagent 同源思路,通过 description 字段自动触发
- **Codex /goal**:可以指定多个 subagent 文件,运行时按 description 匹配

**为什么"description 字段"是 Routing 模式**:LLM 看到主 agent 上下文,根据 description 决定"我该不该把这个子任务交给它"——这就是 routing 决策。

### 选它的具体信号

- 输入类别**稳定**(≤ 10 个),不会动态新增
- 每个类别有**专门工具集**或**专门 prompt** 才处理得好
- 分类错误代价不大(兜底走 general)

### 我们的踩坑

我们 IM agent 第一版 routing 是硬编码关键词表。用户说"我的订单有问题"被分到"账单",因为"订单"命中关键词。后来改成 LLM 路由——但 LLM 路由在"用户输入含敏感词"时会拒识,导致 routing 失败。**最终方案是 LLM 路由 + 关键词兜底,两路并行**。

---

## 04 Parallelization(并行):同输入多分片,各跑各的,合结果

**核心机制**:把同一个任务切成 N 个独立分片,N 个 worker 并行处理,最后 merge。

### 经典实现:MapReduce / Celery

LLM 之前:

```python
import asyncio
from celery import group

# 同步版(Celery)
job = group(process_chunk.s(chunk) for chunk in chunks)
result = job.apply_async().get()
final = merge_results(result)
```

LLM 时代(`asyncio.gather`):

```python
async def parallel_summarize(docs: list[str]) -> list[str]:
    tasks = [summarize_one(d) for d in docs]
    return await asyncio.gather(*tasks)
```

### 三厂对应

- **Cursor /multitask**:把大任务显式拆成多个 subagent 并行跑,8 个上限
- **Claude Code Parallel tool calls**:主 agent 在一个 turn 里发出多个独立 tool call,SDK 内部并行执行
- **Codex /goal**:同 prompt 可以 spawn 多个 subagent 并行

### 选它的具体信号

- 任务**可分片**(分片之间无依赖)
- 分片数 **4-8 个**,再往上 LLM 单 turn 装不下
- merge 函数**简单**(concat / 投票 / 简单 LLM 总结)

### 投票变体:sectioning + voting

Parallelization 还有两种变体:
- **Sectioning**(分片):拆 input,各跑各的,合结果(如批量文档摘要)
- **Voting**(投票):同 input 跑多次,投票决定(增加稳定性,降低 hallucination)

```python
# 投票变体
async def vote_5_times(prompt: str) -> str:
    results = await asyncio.gather(*[llm.invoke(prompt) for _ in range(5)])
    return most_common(results)  # 简单多数
```

`/best-of-n`(Cursor)就是 voting 变体的产品化。

### 我们的踩坑

第一批并行 subagent 我们用 `multiprocessing.Pool` 跑——子进程之间不共享 LLM client 连接,每次 fork 都重新建立 HTTPS 连接,慢 5 倍。**改 asyncio + 共享 client 之后速度从 23 秒降到 4 秒**。

---

## 05 Orchestrator-workers(编排):中央调度,动态拆任务给 worker

**核心机制**:一个 orchestrator agent 持有全局状态和策略,运行时把任务拆给多个 worker agent,worker 完成后把结果返回 orchestrator,orchestrator 决定下一步。

### 经典实现:LangGraph supervisor 模式

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class State(TypedDict):
    task: str
    worker_outputs: list[str]
    done: bool

def orchestrator(state: State) -> Literal["worker_a", "worker_b", END]:
    if len(state["worker_outputs"]) >= 3:
        return END
    if "research" in state["task"]:
        return "worker_a"  # 研究员
    return "worker_b"  # 写手

def worker_a(state: State) -> State:
    output = research_agent.invoke(state["task"])
    return {"worker_outputs": state["worker_outputs"] + [output]}

workflow = StateGraph(State)
workflow.add_node("orchestrator", orchestrator)
workflow.add_node("worker_a", worker_a)
workflow.add_node("worker_b", worker_b)
workflow.set_entry_point("orchestrator")
workflow.add_conditional_edges("orchestrator", orchestrator)
workflow.add_edge("worker_a", "orchestrator")
workflow.add_edge("worker_b", "orchestrator")
graph = workflow.compile()
```

### 三厂对应

- **Anthropic Managed Agents(5/6)**:Lead Agent + 最多 20 subagent,深度**刻意限制 1 层**(subagent 不能 spawn 子 subagent)
- **Cursor /orchestrate(5/7)**:中央 orchestrator + 8 个并行 worker,深度可递归但有限制
- **Codex /goal**:主 agent 动态委派给 subagent,无深度限制

### 选它的具体信号

- 任务**动态变化**(事先无法穷举所有步骤)
- worker 类型 **≥ 3**,每个有专门能力
- **中央协调是关键**(没有 orchestrator,workers 不知道下一步该谁上)
- 上下文需要**全局视角**(orchestrator 持有全状态,workers 只看到自己那段)

### Anthropic 限制深度 1 的真实理由

**不是技术限制,是产品决策**。Anthropic 工程团队在 AMA 里说过:深度 1 是"足够覆盖 95% 用例 + 把递归失控的概率压到 0"的折中。

递归失控的真实案例:2025 年 Q3 某用户跑 LangGraph supervisor,worker 写了一个工具会触发自身递归,跑了 18 小时消耗 $12,000 API 费,只在 context window 撑爆后停。Anthropic 显然知道这件事——所以宁可限制深度,也不要让用户重蹈覆辙。

### 我们的踩坑

我们 supervisor 模式第一版没限制递归深度,踩了 Anthropic 提到的那类坑:worker 在某次任务里误判"这个任务需要再拆",递归 4 层,context 32 万 token 撑爆 LLM 端点。后来**加了一层硬限制:orchestrator 调 worker 最多 3 次/任务**。

---

## 06 Evaluator-optimizer(评估优化):生成-评估-迭代,直到达标

**核心机制**:generator 出一个结果,evaluator 给评分和反馈,不达标就带着反馈再调 generator,直到达标或 N 轮上限。

### 经典实现:Reflexion 论文(2023)

```python
def evaluator_optimizer(input: str, max_rounds: int = 5) -> str:
    output = generator.invoke(input)
    for round in range(max_rounds):
        score, feedback = evaluator.invoke(output)
        if score >= 0.8:
            return output
        output = generator.invoke(f"{input}\n\n上轮反馈:{feedback}")
    return output  # 5 轮没达标也返回
```

### 三厂对应

- **Codex /goal + verification subagent**:Goal 文本同时充当"起始指令 + 完成审计",verification subagent 独立评估
- **Claude Code Outcomes(5/6 同发)**:开发者定义成功标准,独立评分器评估输出,不达标提示修订
- **Cursor /best-of-n**:投票变体(同 prompt 跑 N 次,选最好)

### 选它的具体信号

- 输出有**明确好坏标准**(代码能不能跑 / 文章字数 / 评分 ≥ 阈值)
- 生成一次**不够稳定**(LLM 第一次输出经常跑偏)
- 评估函数**比生成函数便宜**(否则成本爆炸)

### 评估函数 vs 生成函数的成本反讽

Reflexion 论文里"evaluator 是个独立 LLM"——但这意味着**每次评估 = 一次完整 LLM 调用**,5 轮迭代 = 5 次生成 + 5 次评估 = 10 次 LLM 调用。如果生成任务本身是 30 秒,evaluator 也 30 秒,5 轮 = 5 分钟。

`/goal` 设计的巧妙之处:evaluator 可以用**比 generator 更小、更快、更便宜**的模型(比如 generator 用 o3,evaluator 用 gpt-4o-mini)。**评估函数的成本必须是生成的 1/5 以下**,否则这个模式不划算。

### 我们的踩坑

第一版 Evaluator-optimizer,我们 evaluator 用了和 generator 一样的模型。跑"代码生成 + 自评"任务,一轮 30 秒,5 轮 150 秒,成本跟 generator 一样——**等于付了 5 倍价格换稳定性**。后来 evaluator 换成 gpt-4o-mini,成本压到 1/3,稳定性反而更好(因为 evaluator 和 generator 不同模型,blindness 更彻底)。

---

## 07 脚注:另一套分类(架构风格维度)

[Coding Agent 三连](https://...) §一.② 给的另一套 5 种分类(Generator-Verifier / Orchestrator-Subagent / Agent Teams / Hierarchical / Network),其实是**从"架构拓扑"维度**看的,跟 02 篇主线 5 种(从"workflow 模式"维度看)**不冲突**:

| 维度 A:workflow 模式(02 篇主线) | 维度 B:架构风格(脚注) |
| :-- | :-- |
| Prompt chaining | 单 agent / Network(无中央) |
| Routing | 单 agent + 多个 handler |
| Parallelization | 多 agent peer(临时) |
| Orchestrator-workers | Orchestrator-Subagent(中央) / Hierarchical(多层中央) |
| Evaluator-optimizer | Generator-Verifier(双 agent) |

06 篇会详解 Agent Teams(角色化拓扑),08 篇对照收官时会拉出"维度 A × 维度 B"的全景表。

**为什么两套分类同时存在**:
- Anthropic 4/10(workflow 维度)是为**开发者选择模式**用
- Anthropic 5/6 后(架构风格)是为**产品设计拓扑**用
- 它们是**正交**的:你可以用 Orchestrator-workers 模式,选 Hierarchical 拓扑

---

## 08 三厂取舍深读:为什么答案不同

01 综述那张对照表给了"是什么",02 篇补"为什么"。

### 08.1 为什么 Anthropic 限制 1 层

**产品定位**:Anthropic 的客户是**企业**。企业 IT 最怕"agent 在我服务器上跑了 18 小时消耗 $12,000"这种事故。**深度 1 = 递归失控 = 0**。

**技术代价**:深度 1 限制下,复杂任务(比如"调研 X 主题写报告 + 校对 + 翻译")必须**显式拆成多个 subagent 文件,每个 subagent 完成一段**,orchestrator 串起来。这要求开发者**写得更细**,但跑得更可控。

**典型客户场景**:Anthropic 文档里给的例子是"10 份合同批量审阅 + 风险标注"——这个任务**不会递归**,深度 1 完全够用,反而限制深度让单步可解释、可审计。

### 08.2 为什么 OpenAI 不限深度

**产品定位**:OpenAI Codex /goal 主打**长时无人值守**(@skirano 18 小时演示)。要跑长任务链,必须允许递归。

**技术代价**:不限深度 = 失控风险 = 需要额外保护机制。Codex 给的保护:Goal 文本**同时充当起始指令与完成审计**,verification subagent 独立评分,5 轮评估不达标就停。

**典型客户场景**:"把代码库从 React 16 升级到 React 19"——这个任务**本身会递归**(改一处触发连锁),无限深度才跑得完。

### 08.3 为什么 Cursor 卡 8 个

**产品定位**:Cursor 是**IDE**。IDE 里的核心限制是"开发者看屏幕看得过来"。

**8 个的来历**:Cursor 文档原话是"8 个并行 agent 的输出在 IDE 面板里能并排展示,超过 8 个开发者就 monitor 不过来了"。这不是技术上限,是人因工程上限。

**技术代价**:并行度受 IDE 屏幕限制,所以 Cursor 把"长任务链"交给"深度可递归",把"广并行任务"卡在 8 个——**两条腿走路,不押宝一边**。

### 08.4 同一题面三种答案的启示

三厂答案的差异不是"哪个更好",是**不同风险偏好 + 不同产品定位**:
- **Anthropic**:企业安全,宁可功能少,不可失控
- **OpenAI**:长任务链,宁可放手,不可半途
- **Cursor**:开发者体验,宁可限制,不可过载

我们做自研编排时,其实也在做同样的取舍——只是没明说。08 篇对照收官时,会回头看我们当时的取舍对不对。

---

## 09 实战选型决策树

任务来了怎么选模式?按这个顺序问:

```
任务是否可分片且分片间无依赖?
├── 是 → 各分片是否需要专门 prompt / 工具?
│   ├── 是 → Routing(分类 → 分流)
│   └── 否 → Parallelization(分片并行 + merge)
└── 否 → 任务是否动态变化,需要中央协调?
    ├── 是 → Orchestrator-workers
    └── 否 → 任务是否有明确好坏标准?
        ├── 是 → Evaluator-optimizer
        └── 否 → Prompt chaining(几段串行)
```

**实战口诀**:
- **可分片 + 同质** → Parallelization
- **可分片 + 异质** → Routing
- **强依赖** → Prompt chaining(短) / Orchestrator-workers(长)
- **有标准 + 不稳** → Evaluator-optimizer

**复合场景**:真实系统**不会只用一种**。我们的 IM agent 编排实际上是:
- **Routing** 把用户输入分到"对话/创作/工具"三类
- **Orchestrator-workers** 在每类里动态拆任务给 subagent
- **Evaluator-optimizer** 在"创作"类里做质量把控
- **Parallelization** 在"工具"类里并行执行多个独立操作

四种模式叠加,才是真实系统。

---

## 10 收束:模式是组合,不是选择

02 篇拆解的 5 种 multi-agent 协调模式,不是"5 选 1",是**5 种积木**:

- **Prompt chaining** 是最朴素的"串行"
- **Routing** 是"分流到专门"
- **Parallelization** 是"广度并行"
- **Orchestrator-workers** 是"深度动态"
- **Evaluator-optimizer** 是"质量循环"

真实系统是这五种**在任务链不同节点上的组合**——04 篇会讲"context window 怎么约束这些模式的可组合性",05/06/07 篇会看三厂怎么用这些模式搭自家产品,08 篇对照收官时拉出"我们自研编排 vs 大厂工具"的全景对照。

03 篇先回头看一个更原始的问题:**循环本身**——为什么 `while :; do cat PROMPT.md | claude-code ; done` 这一行 bash,能撑起"目标自转"这个新范式?Ralph Loop 的工程哲学是什么,跟 02 篇这 5 种模式怎么衔接?

---

> **系列脚注**
> 上一篇:[01 综述·从自研到大厂默认](#)——三厂同步发布快照 + 8 篇预告
> 下一篇:[03 一行 Bash 循环里的工程哲学:Ralph Loop 拆解](#)——`while :; do cat PROMPT.md | claude-code ; done` 这一行,藏着 2026 年最重要的工程范式转移

---

## 附录:本篇参考链接

- [Anthropic: Building Effective Agents](https://anthropic.com/research/building-effective-agents) — 02 篇主参考
- [Anthropic: Multi-agent Coordination Patterns](https://claude.com/blog/multi-agent-coordination-patterns) — 4/10 5 种 workflow 模式来源
- [Anthropic Managed Agents 多智能体编排文档](https://docs.claude.com/en/docs/managed-agents) — 5/6 Orchestrator-Subagent + 深度 1 来源
- [LangGraph supervisor 模式文档](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) — 经典 Orchestrator-workers 实现
- [Reflexion 论文 (NeurIPS 2023)](https://arxiv.org/abs/2303.11381) — Evaluator-optimizer 学术源头
- [Cursor Subagent 文档](https://cursor.com/docs/subagents) — Routing 模式在 Cursor 的产品化
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices) — context 资源管理与模式选择
- [Codex /goal 文档](https://developers.openai.com/codex/use-cases/follow-goals) — Evaluator-optimizer 在 Codex 的产品化
- `Coding Agent 三连` 报告 §一.②(本地) — 5/6 Anthropic 多智能体编排深度拆解
