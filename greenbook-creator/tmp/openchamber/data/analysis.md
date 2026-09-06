# OpenChamber 深度拆解

> 自动生成于 2026-08-10 | 来源：github.com/openchamber/openchamber + openchamber.dev

## 1. 一句话定位
OpenChamber 是一个基于代理（agentic）的开源开发环境，开发者用来在桌面/浏览器/手机/VS Code 上运行、监督和审查 AI 编码工作。

## 2. 核心数据
- ⭐ Stars: 7,980
- 🍴 Forks: 850
- 📅 创建: 2025-09-11
- 📅 最近更新: 2026-08-10（今天还在 push，活跃）
- 👥 贡献者: 20+（核心 btriapitsyn 1,579 commits）
- 📝 语言: TypeScript 主导（17.1MB）+ JavaScript（4.3MB）
- 📦 License: MIT
- 🏷️ Topics: ai, opencode, opencode-app, opencode-ui
- 🔖 最新版本: v1.18.1（2026-08-04），迭代节奏快
- 🌐 官网: openchamber.dev

## 3. 核心特性
- **会话目标（Session Goals）**：设一个终点线，每轮结束后独立审计模型检查进度，agent 自动继续直到完成/阻塞/预算用尽——即使你关掉应用
- **多模型并行（Multi-run）**：同一任务最多跑 5 个模型，各自独立 session + 可选独立 worktree，保留最佳结果或用 Fusion 融合各模型最强部分
- **变更走查（Changes Walkthrough）**：把大 diff 按逻辑分组为有序步骤，AI 逐段讲解"这段改了什么、为什么这样组合"，标记 Key change / Context
- **预览（Preview）**：指向运行中应用的任意元素，把截图/样式/位置/浏览器报错发给 agent；桌面版内置浏览器可审查任意网页
- **GitHub 全流程**：从 issue/PR 带上下文开 session，把失败的 checks/评审意见发回 agent，直接在 OpenChamber 里更新或合并 PR
- **定时任务**：cron 计划运行 prompt，可与会话目标配对，让定时任务朝结果推进
- **跨设备工作区**：Desktop（macOS/Win/Linux）/ Web/PWA / VS Code / iOS+Android（beta）/ CLI/Server，上下文不丢
- **Private Relay 远程访问**：一次性 QR 配对，端到端加密，无开放端口，随时可撤销；也支持直连/LAN/VPN/tunnel/SSH

## 4. 原理/架构
- 基于 **OpenCode SDK**（opencode.ai 的开源 agentic coding 引擎）——OpenChamber 是"跑在它外面的监督/审查/编排层"，独立项目、与 OpenCode 团队无隶属
- **Monorepo 6 个包**：`electron`（桌面壳）/ `web`（Web+PWA）/ `ui`（共享 UI）/ `vscode`（编辑器扩展）/ `mobile`（iOS/Android）/ `docs`
- **Session Goals 循环**：agent 停 → 小模型审计（keep going / done / stuck）→ 发继续 prompt → 连续 3 次 stuck 才判定 blocked；硬安全停止：token 预算、自动续跑上限、turn error 即停
- **Multi-run 隔离**：isolate runs 开启后每个 run 独立 git worktree + branch，互不碰文件（需 git 仓库）
- **安全模型**：默认只绑 127.0.0.1；`--ui-password` 保护浏览器 UI；passkeys（Face ID/Touch ID）支持；设备配对用一次性 QR + 每设备独立 token，可随时吊销

## 5. 对比优势
| 维度 | OpenChamber | OpenCode（CLI/TUI） | Cursor/Windsurf | OpenClaw |
|---|---|---|---|---|
| 定位 | agent 工作区（监督层） | agent 引擎（终端） | 闭源 IDE AI | 消息渠道 agent 平台 |
| 界面 | 桌面/Web/手机/VS Code | 终端 TUI | IDE 内 | 聊天渠道 |
| 开源 | ✅ MIT | ✅ | ❌ | ✅ |
| 会话目标 | ✅ 自动推进+审计 | ❌ | ❌ | 部分（cron） |
| 多模型并行 | ✅ 5 模型+融合 | 单模型为主 | 单模型 | 可配 |
| 远程访问 | Private Relay 加密 | 无 | 无 | 网关 |

## 6. 实践上手
```bash
# 桌面版（自带 OpenCode CLI，无需另装）
chmod +x OpenChamber-*.AppImage && ./OpenChamber-*.AppImage

# CLI / Web 模式（需 Node.js 22+ 和 OpenCode CLI）
curl -fsSL https://raw.githubusercontent.com/openchamber/openchamber/main/scripts/install.sh | bash
openchamber --ui-password be-creative-here   # 打开 http://localhost:3000

# 常用操作
openchamber status
openchamber connect-url --qr                 # 手机配对
openchamber tunnel start --provider cloudflare --mode quick --qr
openchamber startup enable                   # 开机自启
openchamber update
```

## 7. 适用场景
### ✅ 适用
- 需要"放出去干 + 回来审"的 agent 编码：设目标后关掉应用，回来审查 diff
- 同一任务多模型对比：Multi-run 5 路并行 + Fusion 融合
- 跨设备：办公室桌面 → 手机看进度/审批/回答问题
- 定时维护任务：cron + Session Goals 配对
- 团队 issue → PR 全流程在 VS Code 旁完成

### ❌ 不适用
- 纯终端党、不想装 GUI：直接用 OpenCode CLI
- 非编码场景的 agent 自动化（消息机器人/定时报告）：用 OpenClaw 等平台更合适
- 无 Node.js 22+ 或不允许本地服务常驻的环境

## 8. 注意事项
- ⚠️ Linux AppImage 依赖 FUSE（libfuse.so.2），无 FUSE 用 `APPIMAGE_EXTRACT_AND_RUN=1` 运行
- ⚠️ CLI/Web/VS Code 模式需**自己装 OpenCode CLI**；只有桌面版自带
- ⚠️ 默认只监听 localhost；要暴露网络必须先设 `--ui-password`，远程优先 Private Relay/tunnel，别裸开端口
- ⚠️ 移动端仍是 beta：iOS 走 TestFlight，Android 走 APK，未上架应用商店
- ⚠️ 项目很新（2025-09 创建），v1.18 迭代快，824 个 open issues，API 可能变动
- ⚠️ 独立项目，与 OpenCode 团队无隶属关系，支持走 ko-fi（无企业背书）
