# OpenAI 把 Codex 的 harness 做成了 API：这跟你自建智能体，到底差在哪

说起来，这两天微信群里刷得最多的一条，是 Michael Luo 加入 OpenAI。

一个华裔工程师，入职两周就参与发了 Agents API，节奏快得他自己在 X 上都感叹 crazy fast。但比人事新闻更值得聊的，是那个产品本身：OpenAI 把 Codex 背后的 Agent Harness，直接做成了 API 对外卖。

群里转的那篇稿子，末尾有人下了一句判断，说这东西跟我们在云上自己部署智能体没什么区别，无非换了个 harness 的概念。

作为每天自己搭 agent 干活的 AI Native Coder，我对这句话半信半疑。半信，是因为抽象层面确实像；半疑，是因为我越看越觉得，这两件事的方向是反的。

这篇我把 OpenAI 官方文档翻了一遍，也把转载里那堆数字挨个核了。顺手还把自己天天在用的 OpenClaw 的架构文档也对了一遍。结论先放这儿：**抽象层是同一件事，控制权正好相反，而且真正的增量其实只有一样——它把 API 开放了。**

[图片]

## 01 先把两边的"五件套"摊开看

要吵"有没有区别"，得先把能力拆开，一样一样对。

**会话与上下文。** 官方管它叫 Session，会话持久化，接近上下文窗口上限时自动压缩早期内容，能跨多个 context window 接着跑，目标是让任务稳跑几天。你自建那边，等价物是自己的会话历史、memory 文件，加一段自己写的摘要逻辑。

**工具。** MCP 服务器、自定义 function、内置 web search，还有两个细节：tool search 按需检索工具定义、programmatic tool calling 在代码里并行调工具。自建那边就是 MCP 加 skills，加你自己包的函数。

**编排。** 官方文档里的写法是 `multi_agent.enabled` 配 `max_concurrent_subagents`，主 agent 拆子任务分派下去，子 agent 各有上下文。自建那边，就是主 agent spawn 几个子 agent。

**运行时。** 托管沙箱里跑代码、读写文件、装包、产出 artifact。自建那边，就是你自己那台服务器或容器。

**恢复与介入。** session 可从检查点恢复，agent 干活时你能中途 steer。自建那边，就是你自己写的检查点和中断重放。

五件对上五件，所以"没区别"这句不是错觉。OpenAI 干的事，是把这层胶水标准化、托管化、按量卖。

这事十年前发生过一次：自建 K8s 变成托管 K8s。五年前又发生过一次：自建 MySQL 变成 RDS。现在轮到 harness。

> 每一次被商品化的都不是"技术"，是那层又脏又累、谁都不想维护的胶水。

## 02 但拆开看，每一条的方向都不一样

对完五件套，我原本准备认同那句"没什么区别"。结果往下多看一层，发现方向是反的。

**第一，托管对自托管。** 这是商业模式差异，不是技术差异。运维归谁，责任就归谁。

**第二，模型。** 这是最硬的一条。官方示例里的模型是 `gpt-6-astra`，只能选 OpenAI 自家的。自建 harness 是模型无关的，DeepSeek 顺、MiniMax 也顺，本地模型也能接。一个是接受中介给你的房源，一个是自己挑房。

**第三，交互面。** Agents API 是给开发者嵌进自己 App 的，前端还得你自己写。自建的智能体是渠道优先的，直接对话、群里发言、定时主动找人，天生自带一副"身体"。

**第四，数据合规。** 转载里写公测期数据驻留仅美国、暂不支持 Zero Data Retention。这条我暂时没核到原始出处，但对国内团队，它常常是一票否决。

**第五，计费。** 官方口径还算清楚：Agents API 本身不额外收费，模型按所选模型费率、内置工具按标准费率、托管沙箱按标准容器费率。翻译一下就是，接口免费，算力和工具照单收费。至于转载里那组"1/4/16/64GB 档位、20 分钟单价"，我在官方页面没找到出处，先别当事实用。

**第六，这条是我自己翻文档翻出来的。** OpenAI 把 Agents API、Agents SDK、Responses API 并列为三种 agent runtime，让开发者按"谁来跑 agent loop、谁管状态"来选。要自己掌控部署、存储、审批的时候，官方让你退回 SDK，或者退回 Responses API。

连官方都不认为托管 harness 能覆盖所有场景。这是整件事里最有意思的一处。

## 03 把 Agents API 放回 OpenClaw 的架构上，当场对一遍

上面那些"五件套"不是理论名词。我日常用的 OpenClaw 里，每一件都有对应的实现，而且是文档里写清楚、跑了一年多的东西。干脆当场对一遍。

**Session。** Agents API 那边是托管的 session，OpenAI 跑 agent loop、替你保存进度。OpenClaw 这边，会话状态由常驻的 Gateway 进程独占持有，落盘成 `sessions.json` 加一份 jsonl 转录；私聊、群、cron、webhook 各有各的路由规则，群聊按群隔离。

**上下文压缩。** 官方说会话接近上限时自动压缩。OpenClaw 也一样，compaction 默认就是开着的；但它多做了一件事——压缩之前先跑一次静默的 memory flush，把要点写进记忆文件，再压缩。另外它的上下文引擎是可插拔的，留了 ingest、assemble、compact、after turn 四个生命周期钩子。

**中途介入。** 官方叫 steer。OpenClaw 的队列模式默认就是 steer，而且注入时机卡得很细：在"模型边界"插入，也就是当前这一批工具跑完、下一次模型调用之前，不打断正在跑的工具。

**多 agent 编排。** 官方是配 `multi_agent`。OpenClaw 是 `sessions_spawn` 起一个子 agent，跑在独立 session 里，完成后用 push 的方式把结果回传给请求方，不用轮询。

**沙箱。** 官方是托管沙箱，或者自带。OpenClaw 的沙箱是自托管的，后端可选 docker、ssh、openshell，模式分 off、non-main、all 三档，默认全关。

**MCP。** 两家都支持。OpenClaw 这边是双向的：既能把 MCP server 挂进来当工具用，也能用 `openclaw mcp serve` 把自己反过来变成别人的 MCP server。

**工具治理。** 官方是工具清单。OpenClaw 是三层：工具档位（profile）先定基线，再用 allow/deny 收口（deny 永远赢），最后还有一层沙箱策略；被摘掉的工具，模型连 schema 都看不到。

对完这七条，我发现一个更别扭的事实：**这里没有一项是新的。** compaction、steering、spawn、MCP、沙箱、三层治理，全是既有机制，写得明明白白。

那区别在哪？

区别在于，OpenClaw 是一个软件，你得自己部署、自己运维、自己接渠道；Agents API 是一个接口，你调它就行。

所以 OpenAI 的增量不是"发明了 harness"，而是把 harness 从"自建软件"变成了"云上的标准件"。**各家 claw 早就有这套东西，只是从来没把它做成 API 卖出去。**

反过来看也一样成立。一个进程挂多渠道的适配器、确定性渠道路由、heartbeat 和 cron 那套主动性、memory_search 加 dreaming 的记忆巩固、background task 账本——这些 OpenClaw 有，Agents API 的公开概念里没明说。

## 04 它卖的不是技术，是"你不用运维"

官方公告里有句话说得挺实在：每次发新模型，开发者都得重搭一遍自己的 harness。Agents API 换了种做法，用版本化让模型更新直接对应能力入口。

换句话说，它省下的不是技术，是那部分"本来用于打磨产品、结果花在基础设施上的精力"。

买家画像其实很清楚：有想法、有用户、但不想养一支基础设施团队的小团队。华尔街见闻那篇报道里给了几个早期客户的数据，SafetyKit 把案例审核流程迁过去之后，单案处理成本降了 60%；Hypha 把 agent 执行框架和沙箱解耦，响应失败率降了 86%；另一家 Cirridae 的评估分从 0.71 升到 0.85，延迟降了 4 倍。

这几个数字确实挺猛。不过我留了个心眼：这类数字都是厂商自己披露的口径，样本和条件都没公开，看看方向就行，别当 benchmark。

真正要控数据、要换模型的人，还是会自建。所以我说这是两个联赛，不是同场比赛的两匹马。

## 05 抽象泄漏才是真批判

"不用自己造 harness"这句话，只对前 80% 的场景成立。

剩下那 20%，会从管理面板掉回底层：想换模型，出局；数据不能出境，出局；上下文压缩策略不合你的业务口味、想改却发现改不了，这是最典型的抽象泄漏，能用的部分很香，一旦要调，你就得自己重写。再往下还有沙箱成本失控、需要 GPU 或 VPC 之类的特殊配置。

用的时候觉得省了三个月，出问题的时候，可能还回去六个月。

而且这里有个细微但重要的差别：OpenClaw 的上下文引擎是可以插拔替换的，压缩策略不合口味就换一个；托管服务里，压缩策略是厂商的黑盒，你不喜欢也只能忍着。同样是抽象泄漏，一个能换零件，一个只能等版本更新。

所以那句"没区别"，我现在的版本是：**对急着上线的人，它确实替你省了事；对要长期掌控的人，它换走的东西比想象中多。**

## 06 写在最后

我们大概正站在一个分界线上：Agent Harness 从"每家自己焊的胶水"，变成了"云厂商的标准件"。

而这件事真正的分水岭，不是技术，是形态。能力早就跑在各家的智能体里了，谁也没比谁多长出什么；差别在于有人终于把它包成了 API，让"不用自己部署一套"成为可能。

标准件的好处是便宜、快、不用管。代价是，标准件只保证标准场景。

所以这事最后落到每个人身上的问题，其实就一句：你更贵的是时间，还是控制权。

至于要不要现在就上，我的建议是先等等。公测阶段，按官方自己的说法也是"会快速迭代"，别急着把生产环境搬进去。真要试，拿个内部工具练手就够了。

---

**参考资料（均为 2026-09-12 核对）**

openai.com/index/introducing-the-agents-api/ （官方发布公告）
developers.openai.com/api/docs/guides/agents-api/overview （官方文档 · Agents API 概览）
developers.openai.com/api/docs/guides/agents （官方文档 · 三种 runtime 对比）
community.openai.com/t/introducing-the-agents-api-and-hosted-sandboxes/1396481 （开发者社区帖，2026-09-10）
www.163.com/dy/article/L6H2UMJ505198NMR.html （华尔街见闻报道转载，2026-09-11）

**核对说明**：模型名 `gpt-6-astra`、字段 `multi_agent.enabled` / `max_concurrent_subagents`、沙箱合作方 9 家（Blaxel AI、Cloudflare Dev、Daytona、DigitalOcean、E2B、Modal、Oracle Cloud、Runloop AI、Vercel）、计费口径，均已对照官方文档确认。OpenClaw 侧机制（Gateway 持有会话状态、compaction 与 memory flush、queue mode steer、sessions_spawn 回传、docker/ssh/openshell 沙箱、bundle-mcp 与 mcp serve、三层工具治理）均出自 OpenClaw 官方架构文档。仍未核实的：数据驻留与 ZDR 措辞、沙箱具体档位单价、Michael Luo 个人履历细节。
