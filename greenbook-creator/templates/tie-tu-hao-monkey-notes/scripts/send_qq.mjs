// 发送 8 张重构版 Superset 小绿书到 QQ bot C2C 用户
// 用底层 openclaw-qqbot API（CLI messageId 空 = 没真发）

import { getAccessToken, sendC2CImageMessage, sendC2CMessage } from "/usr/lib/node_modules/openclaw-qqbot/dist/src/api.js";
import fs from "node:fs";
import path from "node:path";

const OPENID = "5588AB8B76D9A22624886F0B90FE98C1";

const cfg = JSON.parse(fs.readFileSync("/home/ubuntu/.openclaw/openclaw.json", "utf8"));
const qq = cfg.channels?.qqbot;
if (!qq?.appId || !qq?.clientSecret) {
  console.error("Missing qqbot credentials in openclaw.json");
  process.exit(1);
}

const IMG_DIR = "/home/ubuntu/.openclaw/workspace/output/superset-greenbook/v2/images";

const COVER_TEXT = `🚀 Superset 深度拆解（重构 v2 · 猴子AI笔记风）

为 AI Coding Agents 打造的编排型 IDE：并行 10+ Agent + Git Worktree 自动隔离 + 编码提速 ×10。

8 张图速通👇
1️⃣ 封面｜一句话定位 + 核心数据
2️⃣ WHAT IT DOES｜5 步工作流
3️⃣ RUNTIME ARCH｜三层架构图
4️⃣ KEY FEATURES｜5 大特性
5️⃣ VS OTHERS｜vs Cursor / 纯 CLI
6️⃣ INSTALLATION｜5 分钟上手
7️⃣ USE CASES｜适用 vs 不适用
8️⃣ GOTCHAS｜避坑 6 条

macOS 用户 + 想多 AI 协作 → 值得装。`;

const CAPTIONS = [
  `01/08 封面｜一句话定位
并行 10+ AI 编码 Agent，你只管挑最好的。
Git Worktree 自动隔离 · 编码提速 ×10 · 多界面同源
兼容 AmpCode / Claude Code / 任意 CLI Agent`,
  `02/08 WHAT IT DOES｜一句话定位
它不只补全代码，而是做完整任务。
5 步：需求 → 读仓库 → 改文件 → 跑命令 → 持续处理
三入口：TUI / HEADLESS / ACP`,
  `03/08 RUNTIME ARCHITECTURE｜运行链路
一次任务怎么持续跑完？
三入口 → LEADER(编排层) → SESSION ACTOR(工作区层) → MODEL ↔ TOOLS`,
  `04/08 KEY FEATURES｜5 大特性
① 并行工作区 ② 智能体监控 ③ 持久化终端
④ 内置 Diff 查看器 ⑤ 应用内浏览器 + 命令面板 / 远程`,
  `05/08 VS OTHERS｜对比优势
vs 传统工具，编排能力是分水岭。
6 维度：并行 Agent / Worktree / Diff / 终端 / 远程 / 多 AI 协作
Superset 是目前唯一原生支持多 AI 协作的编码工具。`,
  `06/08 INSTALLATION｜5 分钟上手
brew install bun gh caddy
git clone github.com/superset-sh/superset
bun install && bun run dev
在应用内接 amp / claude-code 即可并行调度
⚠️ 仅 macOS，Win/Linux 未测试`,
  `07/08 USE CASES｜适用 vs 不适用
✅ 适用：多 Agent 择优 / 多模块并行重构 / 远程固定机器跑 / 夜间自动化
❌ 不适用：Win/Linux / 纯手写党 / 单 Agent 小项目
你是 macOS 用户 + 想多 AI 协作 → 值得装`,
  `08/08 GOTCHAS｜避坑 6 条
⚠️ 仅 macOS  ⚠️ Bun ≥ 1.0  ⚠️ Git ≥ 2.20
⚠️ 必装 Caddy  ⚠️ Agent 自备 Key  ⚠️ 远程命令自配
装之前先 brew doctor，省去 80% 报错`,
];

async function main() {
  console.log("Getting QQ bot access token...");
  const token = await getAccessToken(qq.appId, qq.clientSecret);
  console.log("Token acquired");

  // 1. 先发封面文案
  console.log("\nSending cover text...");
  const r0 = await sendC2CMessage(token, OPENID, COVER_TEXT);
  console.log("Cover text sent, id:", r0?.id);

  await new Promise(r => setTimeout(r, 2500));

  // 2. 逐张发图 + 配文
  for (let i = 0; i < 8; i++) {
    const p = path.join(IMG_DIR, `card_${i + 1}.png`);
    console.log(`\n[${i + 1}/8] ${p}`);
    const buf = fs.readFileSync(p);
    const dataUrl = `data:image/png;base64,${buf.toString("base64")}`;
    const r = await sendC2CImageMessage(token, OPENID, dataUrl);
    console.log(`  image id: ${r?.id || "(none)"}`);
    await new Promise(r => setTimeout(r, 1200));
    const rt = await sendC2CMessage(token, OPENID, CAPTIONS[i]);
    console.log(`  caption id: ${rt?.id || "(none)"}`);
    await new Promise(r => setTimeout(r, 2000));
  }

  console.log("\n✅ All 8 cards sent to QQ bot");
}

main().catch(e => {
  console.error("Fatal:", e);
  process.exit(1);
});