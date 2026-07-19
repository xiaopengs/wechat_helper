# AI 圈日报不用刷浏览器了：AI HOT 这个 Skill / RSS / REST API 我拆了

> 项目拆解 + 实操指南 + 工具盘点
> 2026-06-29 · 工程师向

---

## 导语

AI HOT(域名 `aihot.virxact.com`,也叫"热点")把每天 LLM 精编的 AI 圈动态,做成了一个匿名可读的"三轨接入服务":Skill(任意 Agent)/ RSS(零配置)/ REST API(OpenAPI 3.1 规范)。

今天不用浏览器、不用 RSS 阅读器、不用现写 CLI 客户端,你在 Claude Code / Cursor / Copilot / Codex CLI 任一 Agent 里说一句话,就能拿到 AI 圈精选+精编日报。

下面先说 3 种接入方式是什么、再讲装、最后讲按场景选哪个。

---

## 01 / 3 种接入方式速查

### 1. Skill — SKILL.md 标准(★ 默认推荐)

**做什么**:让任意 Agent 用自然中文读取 AI HOT 全部数据。

**适用场景**:Claude Code / Cursor / Copilot 用户 / 不想配置 API Key / 想要"在 Agent 里直接看到今天 AI 圈"。

**硬卖点**:
- · **1 行 install** — 在 Agent 里说"帮我安装这个 skill: https://aihot.virxact.com/aihot-skill/",Agent 自己装到对应目录;
- · **1 份 Skill,7 种 Agent 平台都生效** — Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / OpenCode / Cline / Windsurf;
- · **0 Token,匿名访问** — 无 API Key,无 MCP server 配置,直接走 SKILL.md 标准;
- · **智能意图路由** — 用户说"今天 AI 圈"自动走精选,说"日报"自动走 daily,说"全部"自动走 mode=all。

**踩坑/小毛病**:
- · **测试版** — 作者明说"目前 RSS / API / Skill 三轨都在测试阶段",生产业务不要强依赖;
- · **限流** — 单 IP 600 r/min + burst 40,Agent 串行调用记得加 200ms 间隔;
- · **Skill 同步合集** — 同时跟 hv-analysis / khazix-writer / neat-freak 等其他 Skill 一起进了 KKKKhazix/khazix-skills,装的时候看清是不是 ai 的。

**先装的人**:每天刷 AI 圈的人 + 想在 Agent 里看实时动态的人。

**一行命令**:
```
帮我安装这个 skill: https://aihot.virxact.com/aihot-skill/
```

---

### 2. RSS — 任何 RSS reader 零配置订阅

**做什么**:标准 RSS feed,任何 reader(Feedly / NetNewsWire / Inoreader / Reeder)都能订。

**适用场景**:习惯用 RSS 阅读器 / 想后台静默跟 / 想设自己定时轮询。

**硬卖点**:
- · **零配置** — RSS 几乎不需要 token,server 端 nginx proxy_cache 5 分钟;
- · **7 天硬上限** — since 参数最多回看 7 天,要更久走日报存档 `/daily/{date}`;
- · **服务端翻页** — `cursor` 由后端管,客户端无状态。

**踩坑/小毛病**:
- · **摘要质量** — 摘要是 LLM 生成的,引用前请用 `url` 字段回原文核对;
- · **时间撕裂** — items 接口按 `publishedAt` 倒序,feed 按 timeline 倒序,慢推 RSS 源上两者可能不一致;
- · **公众号爆文被排除** — mp_hot 信源不在 items 接口里,要单独查 `/mp` 页;
- · **arxiv 默认过滤** — 要论文请显式 `category=paper`。

**先装的人**:仍用 Feedly / Inoreader 的人 / 想做日更 quick-flip 的人。

**一行命令**:在 RSS reader 里 add `https://aihot.virxact.com/feed`(具体 feed URL 以站点文档为准)。

---

### 3. REST API — 开发者 / 自定义集成 · OpenAPI 3.1

**做什么**:完整 REST API,带 OpenAPI 3.1 规范,匿名只读,7 个核心端点。

**适用场景**:做自己的 AI 摘要推送 / 集成到 Notion 数据库 / 自己做 dashboard / 接 webhook。

**硬卖点**:
- · **OpenAPI 3.1 规范** — 完整 spec 在 `https://aihot.virxact.com/openapi.yaml`,直接用 codegen 生成客户端;
- · **ETag 304 缓存友好** — 无新条目时 < 1KB 空 body,适合 cron 定时拉;
- · **关键词搜索 2-6ms** — 走 PostgreSQL `pg_trgm` GIN 索引;
- · **cursor 优雅翻页** — 失效/篡改/过期静默回首屏,不报错;
- · **5 个分类** — ai-models / ai-products / industry / paper / tip。

**踩坑/小毛病**:
- · **cursor 是黑盒** — 别解析、别 +1、别跨端点复用,内部格式会变;
- · **单字符 q 退化为全表扫** — 1 个字符搜索会被服务端拒(保护他人);
- · **since 不能早于 7 天前** — 早于 7 天的服务端硬截;
- · **arxiv 默认不在 mode=all** — 全量列表过滤掉了论文源,要用显式 category=paper。

**先装的人**:开发者 / 要做自动化的人 / 想接 webhook / 想做自己的 newsletter。

**一行命令**:
```
curl https://aihot.virxact.com/api/public/items?mode=selected&take=10 \
  -H "If-None-Match: W/\"items-962ce9039439c8ea\""
```

---

## 02 / 7 种意图路由(从宽问题到精准搜索)

Skill 内部按用户意图自动分流。理解这个比"用哪个端点"更重要:

```
# / 用户说 / 调用端点 / 默认开关

| 用户说 | 端点 | 默认？ |
|--------|------|--------|
| 今天 AI 圈 / 过去 24h | GET /api/public/items?mode=selected | 默认 |
| 看下 AI 日报 / 今天的日报 | GET /api/public/daily |  |
| 全部 / 完整 / 所有 / 全量 | GET /api/public/items?mode=all |  |
| AI 模型 / 产品 / 论文 / 技巧 | GET /api/public/items?category=… |  |
| 最近 N 天 | GET /api/public/items?since=ISO-8601 |  |
| OpenAI / Anthropic 最近发的 | GET /api/public/items?q=OpenAI |  |
| 哪些日期有日报 | GET /api/public/dailies?take=N |  |
```

**关键约定**:宽问题(无明确词)默认走精选(`mode=selected`),不传 `mode` 等同 `selected` — 这是 2026-05-08 切换的契约。

---

## 03 / 实操:在 Claude Code 里 4 步拿到今天 AI 日报

走一遍最小可复现路径。

**步骤 1**:在 Claude Code 输入

```
帮我安装这个 skill: https://aihot.virxact.com/aihot-skill/
```

Agent 会自动识别当前平台,装到对应目录。

**步骤 2**:验证 Skill 已激活(可选)

不同 Agent 落点不一样,但都是同一份 SKILL.md:

```
Claude Code → ~/.claude/skills/aihot-skill/SKILL.md
Cursor      → .agents/skills/aihot-skill/SKILL.md
Codex CLI   → .codex/skills/aihot-skill/SKILL.md
Gemini CLI  → extension manifest
```

**步骤 3**:触发一句话,看 Agent 是否主动列出今天的精编日报

```
看下今天的 AI 日报
```

如果 Agent 列出当日模型/产品/论文/技巧/行业这 5 个 section,说明 Skill 已被加载。

**步骤 4**(可选):配 RSS reader 作为 backup。

Rester 同时去 REST API 也走一遍,验证你能直接 `curl` 拿原始 JSON:

```
curl "https://aihot.virxact.com/api/public/daily" | head -c 500
```

返回 `{"date":"2026-06-29","generatedAt":"…","sections":[…]}` 就对了。

---

## 04 / 7 种 Agent 兼容性

Skill 文件格式本身是通用的(SKILL.md 标准),你的 Agent 只要支持 Skills 规范,文件夹拷过去就能用:

| Agent / 运行时 | 接入方式 | 备注 |
|----------------|---------|------|
| Claude Code | Skill 直装 | 默认支持,装到 `~/.claude/skills/<name>/` |
| Cursor | Skill 直装 | 默认支持,装到 `.agents/skills/<name>/` |
| Codex CLI | Skill 直装 | 默认支持,装到 `.codex/skills/<name>/` |
| Gemini CLI | Skill 直装 | 默认支持,extension manifest |
| GitHub Copilot | 仅 RSS / REST API | CLI 装不上,走 reader 或自写请求 |
| OpenCode | Skill 直装 | 默认支持,装到 `.opencode/skills/<name>/` |
| Cline / Windsurf | Skill 直装 | 走 Claude Code 目录规范 |

---

## 05 / 按场景选哪个

直接对号入座:

▸ **想在 Claude Code 里一句中文拿到今天 AI 圈** → Skill
▸ **习惯 Feedly / Inoreader,想后台静默刷** → RSS
▸ **要做 Notion 数据库自动同步 / 自建 dashboard / 接 webhook** → REST API
▸ **要细分只看论文(arxiv 之类)** → REST API + `category=paper`
▸ **每天定时拉日报存档到本地** → REST API + cron + ETag(无新条目 < 1KB,几乎零成本)
▸ **三个一起用** → Skill 作主入口 + RSS 作 backup + REST API 作自动化(本日大部分生产用法)

**几句补充**:

- · **调试期三轨都装** — Skill 响应有问题可以同时查 RSS 与 API;
- · **生产前先看一两周稳定性** — 作者明说测试期可能临时下线/调接口/加限制;
- · **引用前必须回核原文** — 摘要是 LLM 生成的,引用前用 `url` 字段去原链接核对;
- · **6/29 真实案例**:我装完顺手拿了一下当天精选 — Grok 4.5 在 SpaceX/Tesla 私测、Meta Brain2Qwerty v2 非侵入脑电句级实时解码、Claude Code 打开 GitHub 仓库即执行隐藏恶意代码(新攻击向量,务必小心 share 仓库)、小红书 RedKnot 推理引擎 KV Cache 按头拆解。这质量不输一个细分 newsletter。

---

## ⚡ 反馈 / 想要新接入方式

走 `https://aihot.virxact.com/feedback` 直接提,会同步到内部群。

- · **接入页**:https://aihot.virxact.com/agent
- · **SKILL.md 真身**:https://aihot.virxact.com/aihot-skill/SKILL.md
- · **GitHub 同步**:KKKKhazix/khazix-skills
- · **OpenAPI 规范**:https://aihot.virxact.com/openapi.yaml
- · **匿名**:无需 token,无需登录,单 IP 600 r/min

如果还拿不准用哪个,先去 `/agent` 看一眼接入页。

(注意:公众号会剥除外链,建议访问上述地址查看。)
