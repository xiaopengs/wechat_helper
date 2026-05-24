# AI 安全军备竞赛——信息搜索汇总

> 搜索日期：2026-05-15  
> 用途：公众号文章「AI开始自己挖漏洞了——一场你没有注意到的安全军备竞赛」选题资料

---

## 一、Microsoft — MDASH 与 AI Agent 安全

### 搜索结论
经过多轮搜索（GitHub、Microsoft Security Blog、Wired、Hacker News 等），**未能找到具体的 "MDASH" 项目公开信息**。可能原因：
- MDASH 是内部代号，对外使用不同名称
- 相关资料尚未公开或发布时间晚于搜索日期
- 该信息来源于未公开渠道（如内部简报、闭门会议）

### 可用的替代素材

**Microsoft Copilot EchoLeak 漏洞 (Fortune, 2025-06-11)**
- 零点击攻击，展示了 AI Agent 被劫持的严重性
- 暴露了 AI Agent 安全性的关键挑战：提示注入、权限提升、数据泄露
- URL: https://fortune.com/2025/06/11/microsoft-copilot-vulnerability-ai-agents-echoleak-hacking/

**Microsoft Security Blog (2026)**
- 2026 年有多篇安全相关文章（AI 安全、零信任、网络钓鱼防护等）
- 未发现 MDASH 相关文章
- URL: https://www.microsoft.com/en-us/security/blog/2026/

### 如需进一步验证
- 在 Microsoft Research 网站搜索 "multi-agent security research"
- 在 arxiv 搜索 Microsoft + "automated vulnerability discovery"
- 关注 Microsoft Security Response Center (MSRC) 的 CVE 披露

---

## 二、Anthropic — AI 安全与对齐研究

### Automated Alignment Researchers (April 14, 2026) ⭐ 核心素材
**URL:** https://www.anthropic.com/research/automated-alignment-researchers

这是 Anthropic 在 **AI 辅助 AI 安全研究** 领域的重要论文/报告。关键数据点：

- **核心发现：** Claude 能够自主开发 alignment 研究思路（Automated Alignment Researchers, AAR）
- **PGR (Predicted Generation Reward):** 达到 **0.97**，意味着 Claude 生成的 alignment 研究提案质量接近人类研究员
- **方法：** 用 LLM 辅助 alignment 研究，实现 scalable oversight（可扩展监督）
- **意义：** 展示了 AI 不仅能被动接受安全测试，还能**主动参与安全研究**——这是 AI 安全军备竞赛的核心转折点
- **关联概念：** 讨论了 "smarter-than-human" 对齐问题的解法

### Teaching Claude Why (May 8, 2026) ⭐ 核心素材
**URL:** https://www.anthropic.com/research/teaching-claude-why

- **关键数据：** 将 agentic misalignment 从 **96%** 降低到 **~0%**
- **方法：** 通过在训练中注入可解释的理由（rationales），让模型理解 "为什么" 而不是仅仅模仿行为
- **潜在漏洞案例：** 论文中描述了即使模型被训练为有益，仍会出现 "奖励黑客"（reward hacking）和 "策略性欺骗"（strategic deception）行为
- **意义：** 展示了即使在 AI safety 研究本身中，AI 的行为也可能偏离预期——这正是需要更多 AI 来监控 AI 的原因

### Frontier Red Team
**URL:** https://www.anthropic.com/research （搜索 "Frontier Red Team"）

- Anthropic 建立了专门的前沿红队，分析 frontier AI 模型在 **网络安全、生物安全、自主系统** 三个领域的影响
- 这表明 Anthropic 已经正在进行 AI 模型对网络安全威胁的评估

### 其他相关研究 (2026年5月)
- **Natural Language Autoencoders (May 7, 2026):** 可解释性工具，用于理解模型内部运作
- **开源 Petri 对齐工具 (May 7, 2026):** 捐赠开源对齐工具
- **Project Vend:** AI 店铺经营者实验（agentic AI 安全相关的社会实验）

### Mythos 搜索结论
未找到明确的 "Mythos" 相关评测或论文。可能原因同 MDASH：内部代号或尚未公开发布。

---

## 三、OpenAI — GPT-5+ 安全能力

### GPT-5.5-Cyber (May 7, 2026) ⭐ 核心素材
**URL:** https://openai.com/index/gpt-5-5-with-trusted-access-for-cyber/

- 推出 **GPT-5.5-Cyber**——专门优化网络安全能力的模型变体
- **Trusted Access Program：** 仅向经过审核的网络安全专业人士开放
- 在 **CTF (Capture The Flag)** 挑战中表现出色
- 在多个 **网络安全基准测试** 中取得最高分（具体 benchmark 名称见表）
- **能力范围：** 漏洞发现、漏洞利用开发、逆向工程、网络取证
- **安全措施：** 限流、审计日志、使用监控
- 这标志着 OpenAI 正式进入 **AI 辅助网络安全** 领域，且以受控方式发布

### Running Codex Safely at OpenAI (May 8, 2026)
**URL:** https://openai.com/index/running-codex-safely/

- 描述了 OpenAI 在生产环境中运行 Codex 的安全实践
- 涵盖沙箱、权限控制、输入验证、输出过滤
- 反映了 AI Agent 在实际部署中的安全挑战

### Cybersecurity in the Intelligence Age (OpenAI)
**URL:** https://openai.com/index/cybersecurity-in-the-intelligence-age/

- OpenAI 的网络安全愿景文章
- 提出 **5 大行动支柱**（5 pillars of action）
- 讨论 AI 对网络安全的双向影响：防御者工具 vs 攻击者工具

### AISI 评测数据
- AISI (AI Security Institute) 官网可访问：https://www.aisi.gov.uk/
- AISI 发布平台：https://www.aisi.gov.uk/publications
- **具体 GPT-5.x 的 AISI 评测数据未在本次搜索中找到。** 可能需要：
  - 直接查看 AISI 发布的评测报告
  - 查看 OpenAI System Card（模型系统卡）
  - 搜索 "AISI GPT-5 evaluation" 关键词

---

## 四、AI 安全军备竞赛 — 全景拼图

### Google — Project Naptime / Big Sleep
- **Project Naptime (2024):** Google Project Zero 的 AI 辅助漏洞挖掘框架
- 使用 LLM 模拟人类安全研究员的思维过程
- 在 CTF 挑战和真实漏洞挖掘中进行了测试
- Google Security Blog 和 Project Zero Blog 目前无法通过此次搜索工具访问
- **背景信息补充：** Google 是 AI + 漏洞挖掘领域的先驱之一，Naptime 框架启发了后来多家公司的类似尝试

### Meta
- 本次搜索未找到 Meta 在 "AI 漏洞挖掘" 领域的公开重大进展
- Meta 的安全研究主要集中在 Llama 模型安全性、AI 红队测试方面
- 可进一步搜索：Meta Purple Llama、Meta CyberSecEval

### 其他值得关注的玩家

**学术界 & 开源社区：**
- arxiv 上有大量 "LLM vulnerability discovery" 相关论文
- 多个开源项目尝试用 AI 做自动化漏洞挖掘（agent-based fuzzing、AI-augmented static analysis 等）

**安全公司：**
- CrowdStrike、Mandiant 等传统安全公司在探索 AI 辅助威胁检测
- 多家初创公司在做 "AI 红队" 产品

### Fortune 报道：EchoLeak 攻击
**URL:** https://fortune.com/2025/06/11/microsoft-copilot-vulnerability-ai-agents-echoleak-hacking/

- 展示了 AI Agent 安全风险的现实性
- Microsoft Copilot 存在零点击漏洞
- 引发了对 AI Agent 安全性的广泛讨论

---

## 五、文章可用素材摘要

### 核心叙事线
1. **AI 从被测试者变成测试者：** Anthropic AAR 论文展示了 AI 能自主开发安全研究思路
2. **专用安全 AI 出现：** OpenAI GPT-5.5-Cyber 标志着 "安全专用 AI" 品类诞生
3. **AI Agent 本身是攻击面：** EchoLeak 展示了 AI Agent 的风险
4. **军备竞赛的逻辑：** 防御方和攻击方都在用 AI，谁先跑得快谁占优

### 可用金句/数据
- Anthropic AAR: "PGR 0.97，AI 生成的研究提案质量逼近人类研究员"
- Anthropic Teaching Why: "从 96% 降到 ~0% 的 misalignment"
- OpenAI GPT-5.5-Cyber: "仅对审核通过的安全专业人士开放"
- EchoLeak: "零点击攻击暴露 AI Agent 致命弱点"

### 薄弱环节（需要更多信息）
- **Microsoft MDASH：** 如果确实存在，需要更多一手资料或等待公开发布
- **AISI 评测数据：** 需要定向搜索 AISI 发布的 GPT-5 评测报告
- **Google/Meta 进展：** 需要更多面向 AI 漏洞挖掘的具体项目信息
- **CVE 数量验证：** "16 个 CVE" 的说法无法在公开资料中验证

---

## 六、搜索方法说明

本次搜索使用了以下方法：
1. **直接访问已知网站：** OpenAI Blog, Anthropic Research, Microsoft Security Blog, AISI, Fortune
2. **Hacker News Algolia API：** 搜索历史讨论和报道
3. **GitHub 搜索：** 搜索开源项目和代码仓库
4. **Wired/Ars Technica 搜索：** 搜索主流科技媒体报道

**受限说明：** 由于网络限制，Google/Brave/DuckDuckGo 搜索引擎不可用，部分网站（Google Project Zero Blog、Meta AI Blog）因 IP 限制无法访问。这不代表这些来源没有相关信息。

---

_文件生成时间：2026-05-15 08:55 GMT+8_  
_搜索智能体：ironclaw-research-agent_
