# 单图配文模板（P1–P8）

> 每张图配一段 30-80 字的中文短文,先发图再发配文。

```
NN/08 {tag}｜{title}
{核心要点 1}
{核心要点 2}
{数据/亮点 1}
{数据/亮点 2}
```

## Superset 案例（参考）

```
01/08 封面｜一句话定位
并行 10+ AI 编码 Agent,你只管挑最好的。
Git Worktree 自动隔离 · 编码提速 ×10 · 多界面同源
兼容 AmpCode / Claude Code / 任意 CLI Agent

02/08 WHAT IT DOES｜一句话定位
它不只补全代码,而是做完整任务。
5 步:需求 → 读仓库 → 改文件 → 跑命令 → 持续处理
三入口:TUI / HEADLESS / ACP

03/08 RUNTIME ARCHITECTURE｜运行链路
一次任务怎么持续跑完?
三入口 → LEADER(编排层) → SESSION ACTOR(工作区层) → MODEL ↔ TOOLS

04/08 KEY FEATURES｜5 大特性
① 并行工作区 ② 智能体监控 ③ 持久化终端
④ 内置 Diff 查看器 ⑤ 应用内浏览器 + 命令面板 / 远程

05/08 VS OTHERS｜对比优势
vs 传统工具,编排能力是分水岭。
6 维度:并行 Agent / Worktree / Diff / 终端 / 远程 / 多 AI 协作
Superset 是目前唯一原生支持多 AI 协作的编码工具。

06/08 INSTALLATION｜5 分钟上手
brew install bun gh caddy
git clone github.com/superset-sh/superset
bun install && bun run dev
在应用内接 amp / claude-code 即可并行调度
⚠️ 仅 macOS,Win/Linux 未测试

07/08 USE CASES｜适用 vs 不适用
✅ 适用:多 Agent 择优 / 多模块并行重构 / 远程固定机器跑 / 夜间自动化
❌ 不适用:Win/Linux / 纯手写党 / 单 Agent 小项目
你是 macOS 用户 + 想多 AI 协作 → 值得装

08/08 GOTCHAS｜避坑 6 条
⚠️ 仅 macOS  ⚠️ Bun ≥ 1.0  ⚠️ Git ≥ 2.20
⚠️ 必装 Caddy  ⚠️ Agent 自备 Key  ⚠️ 远程命令自配
装之前先 brew doctor,省去 80% 报错
```
