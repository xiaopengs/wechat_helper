# AI 圈日报不用刷浏览器了:AI HOT 这个 Skill 我拆了

> 项目拆解 + 实操指南 + 工具盘点
> 2026-06-29 · 工程师向

---

## 导语

AI HOT(域名 `aihot.virxact.com`,也叫"热点")把每天 LLM 精编的 AI 圈动态,做成了一个匿名可读的"三轨接入服务":Skill(任意 Agent)/ RSS(零配置)/ REST API(OpenAPI 3.1)。

今天不用浏览器,你就能在 Claude Code / Cursor / Copilot / Codex CLI 任一 Agent 里说一句话拿到 AI 圈精选+精编日报。

下面先说 3 种接入方式是什么、再讲装、最后讲按场景选哪个。

---

## 01 / 3 种接入方式速查

### 1. Skill — SKILL.md 标准(★ 默认推荐)

**做什么**:让任意 Agent 用自然中文读取 AI HOT 全部数据。

**适用场景**:Claude Code / Cursor / Copilot 用户 / 不想配置 API Key。

**硬卖点**:
- · **1 行 install** — 在 Agent 里说"帮我安装这个 skill: https://aihot.virxact.com/aihot-skill/";
- · **1 份 Skill,7 种 Agent 平台都生效** — Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / OpenCode / Cline / Windsurf;
- · **0 Token,匿名访问** — 无 API Key,无 MCP 配置,直接走 SKILL.md 标准;
- · **智能意图路由** — 说"今天 AI 圈"自动走精选,说"日报"自动走 daily,说"全部"自动走 mode=all。

**踩坑**:
- · **测试期** — 作者明说 RSS / API / Skill 三轨都在测试阶段;
- · **限流** — 单 IP 600 r/min + burst 40;
- · **同步合集** — 同时进了 KKKKhazix/khazix-skills,跟 hv-analysis / khazix-writer / neat-freak 在一起,装时看清是不是 ai 的。

**先装的人**:每天刷 AI 圈的人 + 想在 Agent 里看实时动态的人。

**一行命令**:`帮我安装这个 skill: https://aihot.virxact.com/aihot-skill/`

---

### 2. RSS — 任何 RSS reader 零配置订阅

**做什么**:标准 RSS feed,任何 reader(Feedly / NetNewsWire / Inoreader / Reeder)都能订。

**适用场景**:习惯用 RSS 阅读器 / 想后台静默跟 / 想设自己定时轮询。

**硬卖点**:
- · **零配置** — RSS 几乎不需要 token,server 端 nginx proxy_cache 5 分钟;
- · **7 天硬上限** — since 参数最多回看 7 天,要更久走日报存档 `/daily/{date}`;
- · **服务端翻页** — `cursor` 由后端管,客户端无状态。

**踩坑**:
- · **摘要质量** — 摘要是 LLM 生成,引用前用 `url` 字段回原文核对;
- · **时间撕裂** — items 按 `publishedAt` 倒序,feed 按 timeline 倒序,慢推 RSS 源可能不一致;
- · **mp_hot 不在 feed** — 公众号爆文要查单独 `/mp` 页。

**先装的人**:仍用 Feedly / Inoreader 的人。

**一行命令**:`https://aihot.virxact.com/feed`(具体以站点文档为准)

---

### 3. REST API — 开发者 / 自定义集成 · OpenAPI 3.1

**做什么**:完整 REST API,带 OpenAPI 3.1 规范,匿名只读。

**适用场景**:做自己的 AI 摘要推送 / 集成到 Notion 数据库 / 自己做 dashboard。

**硬卖点**:
- · **OpenAPI 3.1 规范** — spec 在 `https://aihot.virxact.com/openapi.yaml`,直接 codegen 生成客户端;
- · **ETag 304 缓存友好** — 无新条目时 < 1KB 空 body,适合 cron 定时拉;
- · **关键词搜索 2-6ms** — 走 PostgreSQL `pg_trgm` GIN 索引;
- · **cursor 优雅翻页** — 失效/篡改/过期静默回首屏,不报错。

**踩坑**:
- · **cursor 是黑盒** — 别解析、别 +1、别跨端点复用,格式会变;
- · **单字符 q 拒服** — 1 字符搜索服务端拒(保护他人);
- · **since 不能早于 7 天前** — 早于 7 天服务端硬截。

**先装的人**:开发者 / 要做自动化的人。

**一行命令**:`curl "https://aihot.virxact.com/api/public/items?mode=selected&take=10" -H 'If-None-Match: W/"items-962ce9039439c8ea"'`

---

## 02 / 7 种意图路由(从宽到精准)

Skill 内部按用户意图自动分流,理解这个比"用哪个端点"重要:

| 用户说 | 端点 |
|--------|------|
| 今天 AI 圈 / 过去 24h | GET /api/public/items?mode=selected |
| 看下 AI 日报 / 今天的日报 | GET /api/public/daily |
| 全部 / 完整 / 所有 / 全量 | GET /api/public/items?mode=all |
| AI 模型 / 产品 / 论文 / 技巧 | GET /api/public/items?category=… |
| 最近 N 天 | GET /api/public/items?since=ISO-8601 |
| OpenAI / Anthropic 最近发的 | GET /api/public/items?q=OpenAI |
| 哪些日期有日报 | GET /api/public/dailies?take=N |

关键约定:宽问题默认走精选(`mode=selected`) — 2026-05-08 切换的契约。

---

## 03 / 实操:在 Claude Code 里 4 步拿到今天 AI 圈

走一遍最小可复现路径。

**步骤 1**:在 Claude Code 输入
```
帮我安装这个 skill: https://aihot.virxact.com/aihot-skill/
```
Agent 会自动识别当前平台,装到对应目录。

**步骤 2**(可选):验证激活
```
Claude Code → ~/.claude/skills/aihot-skill/SKILL.md
Cursor      → .agents/skills/aihot-skill/SKILL.md
Codex CLI   → .codex/skills/aihot-skill/SKILL.md
Gemini CLI  → extension manifest
```

**步骤 3**:触发一句话
```
看下今天的 AI 日报
```
如果 Agent 列出当日模型/产品/论文/技巧/行业 5 个 section,说明 Skill 已加载。

**步骤 4**(可选):`curl "https://aihot.virxact.com/api/public/daily" | head -c 500`,返回 `{"date":"2026-06-29","sections":[…]}` 就对了。

---

## 04 / 7 种 Agent 兼容性

| Agent | 接入 |
|-------|------|
| Claude Code / Cursor / Codex CLI / Gemini CLI / OpenCode / Cline / Windsurf | Skill 直装 |
| GitHub Copilot | 仅 RSS / REST API(CLI 装不上) |

---

## 05 / 按场景选哪个

▸ **想在 Claude Code 里一句中文拿到今天 AI 圈** → Skill
▸ **习惯 Feedly / Inoreader 后台静默刷** → RSS
▸ **要做 Notion 自动同步 / 自建 dashboard** → REST API
▸ **要细分只看论文** → REST API + `category=paper`
▸ **每天定时拉日报存档** → REST API + cron + ETag(< 1KB 几乎零成本)
▸ **三个一起用** → Skill 主入口 + RSS 备份 + REST API 自动化

几句话补充:调试期三轨都装好排查;生产前先看一两周稳定性;引用前必须用 `url` 字段回核原文;6/29 装完顺手拿当天精选 — 质量不输一个细分 newsletter(Grok 4.5 在 SpaceX 私测、Meta Brain2Qwerty v2 非侵入脑电句级实时解码、Claude Code 打开 GitHub 仓库即执行隐藏恶意代码、RedKnot 推理引擎 KV Cache 按头拆解)。

接入页 `https://aihot.virxact.com/agent` · SKILL.md 真身 `https://aihot.virxact.com/aihot-skill/SKILL.md` · 反馈页 `https://aihot.virxact.com/feedback` · OpenAPI 规范 `https://aihot.virxact.com/openapi.yaml` · 同步仓 `KKKKhazix/khazix-skills` · 匿名 / 单 IP 600 r/min。
