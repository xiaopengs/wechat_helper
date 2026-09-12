# OpenAI 把 Codex 的 harness 做成了 API：这跟你自建智能体，到底差在哪

说起来，这两天微信群里刷得最多的一条，是 Michael Luo 加入 OpenAI。

一个华裔工程师，入职两周就参与发了 Agents API，节奏快得他自己在 X 上都感叹 crazy fast。但比人事新闻更值得聊的，是那个产品本身：OpenAI 把 Codex 背后的 Agent Harness，直接做成了 API 对外卖。

群里转的那篇稿子，末尾有人下了一句判断，说这东西跟我们在云上自己养的智能体没什么区别，无非换了个 harness 的概念，各家 claw 不过是没把 API 开放出来。

这句话，前半句我不同意，后半句我同意。

抽象层确实像，但控制权的方向是反的；而它真正的增量，也确实不在能力上——是在形态上。

这篇我把 OpenAI 官方文档翻了一遍，也把 OpenClaw 的架构文档逐节对着看了一遍。结论先放这儿：**能力早就有了，OpenAI 的增量是把这套 harness 变成了一个 API 商品。**

[图片]

## 01 先把两套东西摆到一张桌子上

先看 OpenAI 这边。官方给了四个核心概念：Agent（模型、指令、工具、MCP 服务器）、Environment（沙箱或电脑）、Session（可持久运行的实例）、Events and items（送进去的输入和跑出来的产出）。围绕这四个概念，harness 提供五件事：会话与上下文、工具、编排、运行时、恢复与介入。

再看 OpenClaw 这边。我按它的架构文档拆下来，长这样：

一个常驻的 Gateway 进程，把消息面和控制面收在一个进程里，内部跑着 agent runtime、session store、渠道适配器、provider 连接和一个 cron 调度器。

agent loop 是这么走的：请求进来先返回一个 runId，然后按 session 的通道串行跑这一轮，把 assistant、tool、lifecycle 事件流式吐出来。上下文不是模型自己管的，是 OpenClaw 拼好了再喂——基础系统提示、skills 列表、启动时注入的 AGENTS.md / SOUL.md / MEMORY.md 这些文件，再加每轮的覆盖项，skills 正文按需再读。

上下文压缩它也自己做：auto-compaction 默认开着，接近上限、或者模型直接返回 overflow，就把旧轮摘要掉重试；压缩之前还会静默跑一次 memory flush。Session 落盘在 `~/.openclaw/agents/<agentId>/sessions/`，一个索引文件加每会话一个 jsonl。中途想插话也有：默认走 steer，新消息在模型边界注入，不会打断正在跑的工具调用。

工具按组划分，fs、sessions、web、automation、messaging、nodes、media、plugins 各自成组，策略是一条链：profile → provider → allow/deny → per-agent → sandbox。沙箱默认关，开了之后分 off / non-main / all 三种模式，后端可选 docker、ssh、openshell。记忆是纯 Markdown，MEMORY.md 启动时注入，memory/*.md 默认不进上下文、按需检索。主动性有两套：heartbeat 是主 session 的周期唤醒，cron 走精确调度，每次执行还留一条 task 记录。

把两边的概念硬对上，大概是这么一张表：

Agent ↔ agent 人设
Session ↔ session（落盘 + 可恢复）
Events and items ↔ 流式事件 + 会话记录
multi_agent ↔ 子 agent 派生 + 结果回传
steering ↔ 运行时 steer
context compaction ↔ 自动压缩 + memory flush
hosted sandbox ↔ docker / ssh / openshell 后端
MCP ↔ 挂载为插件工具

对完这张表，我原来那句"抽象层是同一件事"就不是感觉了，是能逐条列出来的。有意思的是差异只在两个方向：OpenClaw 缺一个一级的 Environment 原语，用工作区加沙箱近似；反过来，多渠道加确定性路由、heartbeat 和 cron、Markdown 记忆、三层工具治理，这些 Agents API 一个都没有。

## 02 真正的差异：不是能力，是形态

对完表我得说句实话：这套 harness 的逻辑，自建智能体里早就跑起来了，而且跑了好几年。各家 claw 不是没有 harness，是没把它对外做成 API。

OpenAI 干的是三件事：API 化，一次调用起一个云端 agent；托管化，harness 归它运维；商品化，按 token、按工具、按容器资源计费。

所以"换个概念"这个说法，说反了。它换的不是概念，是交付形态。**能力从来不是瓶颈，封装和分发才是。** 十年前托管 K8s 赢的也不是技术，是谁来运维。

这也解释了为什么它的定位写得那么清楚：给"有想法、有用户、但不想养一支基础设施团队"的人用。你要是已经有自己的 harness 在跑，它对你最大的价值可能不是替换，而是当一面镜子，照出你自己那套缺哪一块。

## 03 但拆开看，每一条的方向都不一样

对完架构，我原本准备认同那句"没什么区别"。结果往下多看一层，发现方向是反的。

第一，托管对自托管。这是商业模式差异，不是技术差异。运维归谁，责任就归谁。

第二，模型。这是最硬的一条。官方示例里的模型是 `gpt-6-astra`，只能选 OpenAI 自家的。自建 harness 是模型无关的，DeepSeek 顺、MiniMax 也顺，本地模型也能接。一个是接受中介给你的房源，一个是自己挑房。

第三，交互面。Agents API 是给开发者嵌进自己 App 的，前端还得你自己写。自建的智能体是渠道优先的，直接对话、群里发言、定时主动找人，天生自带一副"身体"。

第四，数据合规。转载里写公测期数据驻留仅美国、暂不支持 Zero Data Retention。这条我暂时没核到原始出处，但对国内团队，它常常是一票否决。

第五，计费。官方口径还算清楚：Agents API 本身不额外收费，模型按所选模型费率、内置工具按标准费率、托管沙箱按标准容器费率。翻译一下就是，接口免费，算力和工具照单收费。至于转载里那组"1/4/16/64GB 档位、20 分钟单价"，我在官方页面没找到出处，先别当事实用。

第六，这条是我自己翻文档翻出来的。OpenAI 把 Agents API、Agents SDK、Responses API 并列为三种 agent runtime，让开发者按"谁来跑 agent loop、谁管状态"来选。要自己掌控部署、存储、审批的时候，官方让你退回 SDK，或者退回 Responses API。

连官方都不认为托管 harness 能覆盖所有场景。这是整件事里最有意思的一处。

## 04 抽象泄漏才是真批判

"不用自己造 harness"这句话，只对前 80% 的场景成立。

剩下那 20%，会从管理面板掉回底层：想换模型，出局；数据不能出境，出局；上下文压缩策略不合你的业务口味、想改却发现改不了，这是最典型的抽象泄漏，能用的部分很香，一旦要调，你就得自己重写。再往下还有沙箱成本失控、需要 GPU 或 VPC 之类的特殊配置。

用的时候觉得省了三个月，出问题的时候，可能还回去六个月。

不过话说回来，自建那边也不是没有抽象泄漏，只是泄漏在自己人身上：你的 harness 没人托管，模型一升级、渠道一改版，活儿还是你的。

所以那句"没区别"，我现在的版本是：**能力上确实没区别，区别在于谁替你扛运维，以及你为此交出去多少控制权。**

## 05 写在最后

我们大概正站在一个分界线上：Agent Harness 从"每家自己焊的胶水"，变成了"云厂商的标准件"。

标准件的好处是便宜、快、不用管。代价是，标准件只保证标准场景。

所以这事最后落到每个人身上的问题，其实就一句：你更贵的是时间，还是控制权。

至于要不要现在就上，我的建议是先等等。公测阶段，按官方自己的说法也是"会快速迭代"，别急着把生产环境搬进去。真要试，拿个内部工具练手就够了；真要学，不如先把自己的 harness 对着它那四个概念过一遍，看差在哪。

---

**参考资料（均为 2026-09-12 核对）**

openai.com/index/introducing-the-agents-api/（官方发布公告）
developers.openai.com/api/docs/guides/agents-api/overview（官方文档 · Agents API 概览）
developers.openai.com/api/docs/guides/agents（官方文档 · 三种 runtime 对比）
community.openai.com/t/introducing-the-agents-api-and-hosted-sandboxes/1396481（开发者社区帖，2026-09-10）
www.163.com/dy/article/L6H2UMJ505198NMR.html（华尔街见闻报道转载，2026-09-11）
docs.openclaw.ai（OpenClaw 架构文档：agent loop / compaction / session / sandboxing / multi-agent / channels / memory / heartbeat）

**核对说明**：模型名 `gpt-6-astra`、字段 `multi_agent.enabled` / `max_concurrent_subagents`、沙箱合作方 9 家（Blaxel AI、Cloudflare Dev、Daytona、DigitalOcean、E2B、Modal、Oracle Cloud、Runloop AI、Vercel）、计费口径，均已对照官方文档确认。OpenClaw 侧架构描述（Gateway 单进程、auto-compaction 与 memory flush、session 落盘路径、steer 在模型边界注入、沙箱 off/non-main/all 与 docker/ssh/openshell 后端、工具分组与策略链、heartbeat 与 cron 分工）均对照其架构文档逐条核实。仍未核实的：数据驻留与 ZDR 措辞、沙箱具体档位单价、Michael Luo 个人履历细节。
